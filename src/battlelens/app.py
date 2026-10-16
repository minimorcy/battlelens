"""Punto de entrada: une configuración, atajos, pipeline, overlay y bandeja."""

from __future__ import annotations

import argparse
from dataclasses import replace
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PyQt6.QtCore import (
    QLibraryInfo,
    QLocale,
    QObject,
    QPoint,
    QRunnable,
    QThreadPool,
    QTimer,
    QTranslator,
    QUrl,
    pyqtSignal,
)
from PyQt6.QtGui import QDesktopServices, QGuiApplication
from PyQt6.QtWidgets import QApplication, QMessageBox

from . import APP_NAME, __version__
from .core.config import AppState, Config, ConfigError, load_config, save_config
from .core.detection import Action, BattleDetector, RegionWatcher
from .core.games import GameDetector
from .core.updates import Release, check_latest, due
from .core.learnsets import Learnsets, LearnsetsMissingError
from .core.matcher import NameMatcher
from .core.moves import MoveMatcher, MoveMemory
from .core.pokedex import DatasetMissingError, Pokedex
from .core.profiles import Profile, ProfileStore
from .core.presets import preset_for, to_profile_regions
from .core.report import ReportInputs, issue_form_url, write_report
from .core.storage import app_data_dir
from .i18n import N_, _, resolve_language, set_language
from .pipeline import (
    RecognitionPipeline,
    RecognitionResult,
    combined_fingerprint,
    crop_regions,
    levels_of,
    read_crop,
    read_moves,
    read_regions,
)
from .platform import windows
from .platform.capture import CaptureError, WindowMinimized, WindowUnavailable, capture_client
from .platform.hotkeys import Hotkey, HotkeyManager, HotkeyParseError, parse_hotkey
from .platform.ocr import OcrLanguageError, available_languages, recognize, resolve_languages
from .platform.ocr_setup import (
    MANUAL_INSTRUCTIONS,
    InstallOutcome,
    InstallResult,
    install_ocr,
    proposed_ocr_tag,
    ui_language_tag,
)
from .platform.single_instance import SingleInstance
from .ui.settings import SettingsWindow
from .ui.calibrator import CalibrationDialog, ask_profile
from .ui.icons import app_icon
from .ui.overlay import Overlay
from .ui.preset_wizard import PresetWizard
from .ui.report import ReportDialog
from .ui.tray import Tray
from .stream.payload import build_cards
from .stream.server import StreamServer, StreamState
from .vision.preprocess import crop_region, fingerprint, fingerprint_distance

log = logging.getLogger("battlelens")


class _WorkerSignals(QObject):
    finished = pyqtSignal(object)
    failed = pyqtSignal(object)


class _Task(QRunnable):
    """Ejecuta `fn(*args)` en el QThreadPool y devuelve el resultado o la excepción por señales."""

    def __init__(self, fn, *args) -> None:
        super().__init__()
        self.signals = _WorkerSignals()
        self._fn, self._args = fn, args

    def run(self) -> None:
        try:
            self.signals.finished.emit(self._fn(*self._args))
        except Exception as exc:  # se gestiona en el hilo de la interfaz
            self.signals.failed.emit(exc)


class Controller(QObject):
    def __init__(self, app: QApplication, config: Config, pokedex: Pokedex) -> None:
        super().__init__()
        self.app = app
        self.config = config
        self.data_dir = app_data_dir()
        self.state_path = self.data_dir / "state.json"
        self.state = AppState.load(self.state_path)
        self.profiles = ProfileStore(self.data_dir / "profiles")
        self.move_memory = MoveMemory(self.data_dir / "moves.json")  # spec own-moves
        self._move_matcher: MoveMatcher | None = None
        self.profiles.load(preferred_active=self.state.active_profile)
        self.target: windows.WindowInfo | None = windows.find_window(
            self.state.last_window_exe, self.state.last_window_title
        )
        self.pipeline = RecognitionPipeline(
            pokedex,
            NameMatcher(pokedex, threshold=config.threshold),
            capture_client,
            recognize,
            debug_dir=self.data_dir / "debug" if config.debug else None,
        )
        self._busy = False
        self._recognition_game: str | None = None
        self._pool = QThreadPool.globalInstance()
        self.pokedex = pokedex
        self.detector = GameDetector(pokedex.games)

        self.overlay = Overlay(pokedex, config.language, config.auto_hide_seconds, mode=config.overlay_mode)
        self.overlay.hidden = {mode: config.hidden_sections(mode) for mode in ("normal", "competitive")}
        self._last_battle = None  # (clave, juego, niveles) de la última ficha, para redibujarla
        self._form_choice: dict[int, str] = {}  # especie -> forma elegida con el atajo (add-alternate-forms D4)
        # Modo stream: fuente de navegador para OBS (spec stream-mode)
        self.stream_state = StreamState(config.stream_card_mode)
        self.stream_server = StreamServer(self.stream_state)
        self._stream_args = None  # (rivales, tu Pokémon, niveles, movimientos, probables) de la última ficha
        if self.state.overlay_pos:
            self.overlay.saved_pos = QPoint(*self.state.overlay_pos)
        self.overlay.moved.connect(self._on_overlay_moved)
        self.overlay.dismissed.connect(lambda: self.battle.on_hidden_by_user())
        for mode, keys in (self.state.collapsed_sections or {}).items():  # bloques plegados (improve-card-visuals D11)
            self.overlay.collapsed[mode] = set(keys)
        self.overlay.collapsed_changed.connect(self._on_overlay_collapsed)

        # Detección automática del combate (spec battle-detection)
        self.battle = BattleDetector(fingerprint_distance, config.detection_hide_after_seconds)
        self.moves_watcher = RegionWatcher(fingerprint_distance)  # menú de ataques (add-own-moves D3)
        self._moves_busy = False
        self._watch_busy = False
        self._modal_open = False
        self._watch_timer = QTimer(self)
        self._watch_timer.setInterval(config.detection_interval_ms)
        self._watch_timer.timeout.connect(self._watch_tick)

        bindings, invalid = self._parse_hotkeys()
        self.tray = Tray(
            windows.list_windows,
            lambda: self.target,
            self._profiles_snapshot,
            {name: hk.text for name, hk in bindings.items()},
        )
        self.tray.recognize_requested.connect(self.recognize)
        self.tray.auto_detect_toggled.connect(self.set_auto_detect)
        self.tray.mode_selected.connect(self.set_mode)
        self.tray.set_mode(config.overlay_mode)
        self.tray.window_selected.connect(self.select_window)
        self.tray.profile_selected.connect(self.select_profile)
        self.tray.preset_requested.connect(self.new_profile_from_preset)
        self.tray.manage_profiles_requested.connect(lambda: self.show_settings("profiles"))
        self.tray.install_ocr_requested.connect(self.install_ocr)
        self.tray.report_requested.connect(self.show_report)
        self.tray.settings_requested.connect(lambda: self.show_settings())
        self.tray.update_requested.connect(self.open_update)
        self.tray.stream_toggled.connect(self.set_stream_enabled)
        self.tray.copy_stream_url_requested.connect(self.copy_stream_url)
        self._settings: SettingsWindow | None = None
        self._ocr_missing = False
        self.release: Release | None = None
        self.tray.quit_requested.connect(self.quit)
        self.tray.show()

        auto = self.state.auto_detect if self.state.auto_detect is not None else config.detection_enabled
        self.tray.set_auto_detect(auto)
        if auto:
            self._watch_timer.start()

        self._apply_stream(config)
        self.hotkeys = HotkeyManager(bindings)
        self.hotkeys.triggered.connect(self._on_hotkey)
        failed = self.hotkeys.start() + invalid
        self._startup_notices(failed, bindings)
        self.check_for_updates()

    # ---- arranque ----------------------------------------------------------

    def _parse_hotkeys(self, config: Config | None = None) -> tuple[dict[str, Hotkey], list[str]]:
        config = config or self.config
        bindings: dict[str, Hotkey] = {}
        invalid: list[str] = []
        for name, text in (
            ("recognize", config.hotkey_recognize),
            ("calibrate", config.hotkey_calibrate),
            ("hide", config.hotkey_hide),
            ("toggle_mode", config.hotkey_toggle_mode),
            ("cycle_form", config.hotkey_cycle_form),
            ("toggle_stream", config.hotkey_toggle_stream),
        ):
            try:
                bindings[name] = parse_hotkey(text)
            except HotkeyParseError as exc:
                log.warning("Atajo inválido %s: %s", name, exc)
                invalid.append(name)
        return bindings, invalid

    def _startup_notices(self, failed: list[str], bindings: dict[str, Hotkey]) -> None:
        notices = []
        if failed:
            labels = {"recognize": _("reconocer"), "calibrate": _("calibrar"), "hide": _("ocultar"),
                      "toggle_mode": _("cambiar de modo"), "cycle_form": _("cambiar de forma"),
                      "toggle_stream": _("ficha del stream")}
            invalid = _("inválido")
            detail = ", ".join(
                f"{labels[n]} ({bindings[n].text})" if n in bindings else f"{labels[n]} ({invalid})" for n in failed
            )
            notices.append(_("No se pudieron registrar los atajos: {detail}. Cámbialos en config.toml.", detail=detail))
        if not self.ocr_available():
            self._set_ocr_missing(True)
            notices.append(_("Falta el OCR de Windows. Instálalo desde el menú de la bandeja: «Instalar OCR de Windows…»."))
        if self.target is None:
            notices.append(_("Selecciona la ventana del emulador en el menú de la bandeja."))
        elif self.profiles.active is None:
            notices.append(_("Entra en un combate y abre «Nuevo perfil con un preset…» en la bandeja (o calibra a mano)."))
        if notices:
            self.tray.notify("\n".join(notices), warning=bool(failed))
        else:
            self.tray.notify(_("Listo. Pulsa {hotkey} en un combate.", hotkey=self.config.hotkey_recognize))

    @staticmethod
    def ocr_available() -> bool:
        try:
            resolve_languages(("es", "en", "fr", "de", "it"))
            return True
        except OcrLanguageError:
            return False

    # ---- acciones ----------------------------------------------------------

    def install_ocr(self) -> None:
        tag = proposed_ocr_tag(ui_language_tag())
        answer = QMessageBox.question(
            None,
            _("Instalar OCR de Windows"),
            _("Se instalará el reconocimiento de texto de Windows ({tag}).\n\n"
              "Windows pedirá permiso de administrador y la descarga puede tardar unos minutos.", tag=tag),
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.tray.notify(_("Instalando el OCR de Windows… Te aviso al terminar."))
        task = _Task(install_ocr, tag)
        task.signals.finished.connect(self._on_ocr_installed)
        task.signals.failed.connect(
            lambda exc: self._on_ocr_installed(InstallResult(InstallOutcome.FAILED, tag, None))
        )
        self._pool.start(task)

    def _on_ocr_installed(self, result: InstallResult) -> None:
        if result.outcome is InstallOutcome.CANCELLED:
            self.tray.notify(_("Instalación cancelada."))
        elif result.outcome is InstallOutcome.FAILED:
            log.warning("Fallo al instalar el OCR %s (código %s)", result.tag, result.exit_code)
            QMessageBox.warning(
                None, _("OCR de Windows"),
                _("No se pudo instalar el OCR ({tag}).\n\n{instructions}", tag=result.tag,
                  instructions=_(MANUAL_INSTRUCTIONS)),
            )
        elif self.ocr_available():
            self._set_ocr_missing(False)
            self.tray.notify(_("OCR instalado. Ya puedes reconocer con {hotkey}.", hotkey=self.config.hotkey_recognize))
        else:
            self.tray.notify(_("OCR instalado. Reinicia BattleLens para empezar a usarlo."))

    def _set_ocr_missing(self, missing: bool) -> None:
        self._ocr_missing = missing
        self.tray.set_ocr_missing(missing)
        if self._settings is not None:
            self._settings.set_ocr_missing(missing)

    # ---- ajustes (spec app-settings) ----------------------------------------------

    def _profiles_snapshot(self) -> tuple[list[Profile], str | None]:
        return self.profiles.sorted_profiles(), self.profiles.active_id

    def _game_labels(self) -> list[tuple[str, str]]:
        return [(g.id, f"Gen {g.generation} · {g.name(self.config.language)}") for g in self.pokedex.games]

    def show_settings(self, section: str | None = None) -> None:
        """Ventana única y no modal (redesign-settings-window D5)."""
        if self._settings is None:
            w = self._settings = SettingsWindow(self.config, windows.list_windows, lambda: self.target,
                                                self._profiles_snapshot, self._game_labels)
            w.saved.connect(self.apply_config)
            w.window_selected.connect(self.select_window)
            w.profile_selected.connect(self.select_profile)
            w.profile_game_selected.connect(self.set_profile_game)
            w.preset_requested.connect(self.new_profile_from_preset)
            w.calibrate_requested.connect(self.calibrate_new)
            w.region_requested.connect(self.calibrate_region)
            w.region_remove_requested.connect(self.remove_region)
            w.delete_profile_requested.connect(self.delete_profile)
            w.open_data_requested.connect(lambda: os.startfile(self.data_dir))
            w.report_requested.connect(self.show_report)
            w.install_ocr_requested.connect(self.install_ocr)
            w.update_requested.connect(self.open_update)
            w.copy_stream_url_requested.connect(self.copy_stream_url)
            w.expand_sections_requested.connect(self.expand_all_sections)
            w.set_stream(self.config.stream_enabled, self.stream_server.url)
            w.set_update(self.release.version if self.release else None)
            w.set_ocr_missing(self._ocr_missing)
        if section is not None:
            self._settings.show_section(section)
        self._settings.refresh()
        self._settings.show()
        self._settings.raise_()
        self._settings.activateWindow()

    def _refresh_ui(self) -> None:
        """Tras cambiar perfiles o ventana: tooltip de la bandeja y sección Perfiles de Ajustes."""
        self.tray.refresh_tooltip()
        if self._settings is not None:
            self._settings.refresh()

    def _sync_settings(self, name: str, value) -> None:
        """Refleja en Ajustes un cambio hecho desde la bandeja o un atajo, sin marcarlo como pendiente."""
        if self._settings is not None:
            self._settings.sync_value(name, value)

    def apply_config(self, new: Config) -> None:
        """Guarda config.toml y aplica los cambios sin reiniciar (design.md D3)."""
        old = self.config
        save_config(self.data_dir / "config.toml", new)
        self.config = new
        if (new.hotkey_recognize, new.hotkey_calibrate, new.hotkey_hide, new.hotkey_toggle_mode,
                new.hotkey_cycle_form, new.hotkey_toggle_stream) != (
            old.hotkey_recognize, old.hotkey_calibrate, old.hotkey_hide, old.hotkey_toggle_mode, old.hotkey_cycle_form,
            old.hotkey_toggle_stream
        ):
            self.hotkeys.stop()
            bindings, invalid = self._parse_hotkeys(new)
            self.hotkeys = HotkeyManager(bindings)
            self.hotkeys.triggered.connect(self._on_hotkey)
            failed = self.hotkeys.start() + invalid
            self.tray.set_hotkey_hints({name: hk.text for name, hk in bindings.items()})
            if failed:
                self.tray.notify(_("No se pudieron registrar los atajos: {names}.", names=", ".join(failed)), warning=True)
        self.pipeline.matcher.threshold = new.threshold
        self.pipeline.debug_dir = self.data_dir / "debug" if new.debug else None
        self.overlay.language = new.language
        self.overlay.auto_hide_seconds = new.auto_hide_seconds
        sections_changed = (new.hidden_sections_normal, new.hidden_sections_competitive) != (
            old.hidden_sections_normal, old.hidden_sections_competitive)
        self.overlay.hidden = {mode: new.hidden_sections(mode) for mode in ("normal", "competitive")}
        if new.overlay_mode != old.overlay_mode or sections_changed:
            self.overlay.mode = new.overlay_mode
            self.tray.set_mode(new.overlay_mode)
            self._redraw_last_battle()
        if sections_changed:
            self._publish_stream(keep_visibility=True)
        self._watch_timer.setInterval(new.detection_interval_ms)
        self.battle.hide_after_seconds = new.detection_hide_after_seconds
        if new.detection_enabled != old.detection_enabled:
            self.set_auto_detect(new.detection_enabled)
        if new.interface_language != old.interface_language:
            set_language(resolve_language(new.interface_language, _windows_language()))
            self._redraw_last_battle()
            self._publish_stream(keep_visibility=True)
            self.tray.notify(_("Los menús cambiarán de idioma al reiniciar BattleLens."))
        if (new.stream_enabled, new.stream_port) != (old.stream_enabled, old.stream_port):
            self._apply_stream(new)
        if new.stream_card_mode != old.stream_card_mode:
            self.stream_state.mode = new.stream_card_mode
            self._publish_stream(keep_visibility=True)
        self.tray.notify(_("Ajustes guardados."))

    # ---- modo stream (spec stream-mode) -------------------------------------------

    def _apply_stream(self, config: Config) -> None:
        """Arranca, reinicia o para la fuente para OBS según la configuración."""
        if not config.stream_enabled:
            self.stream_server.stop()
        elif not self.stream_server.running or self.stream_server.port != config.stream_port:
            if not self.stream_server.start(config.stream_port):
                self.tray.notify(_("El puerto {port} está ocupado: cámbialo en Ajustes.", port=config.stream_port),
                                 warning=True)
        self.tray.set_stream(config.stream_enabled, self.stream_server.url)
        if self._settings is not None:
            self._settings.set_stream(config.stream_enabled, self.stream_server.url)
        self._sync_settings("stream_enabled", config.stream_enabled)

    def set_stream_enabled(self, enabled: bool) -> None:
        if enabled != self.config.stream_enabled:
            new = replace(self.config, stream_enabled=enabled)
            save_config(self.data_dir / "config.toml", new)
            self.config = new
        self._apply_stream(self.config)
        if enabled and self.stream_server.running:
            self.tray.notify(_("Modo stream activo. Añade en OBS una fuente de navegador con {url}",
                               url=self.stream_server.url))

    def copy_stream_url(self) -> None:
        url = self.stream_server.url
        if url:
            QGuiApplication.clipboard().setText(url)
            self.tray.notify(_("URL copiada: {url}", url=url))

    def _publish_stream(self, keep_visibility: bool = False) -> None:
        """Publica la última ficha en la fuente para OBS, en el modo de ficha del stream."""
        if self._stream_args is None:
            return
        rivals, own, levels, moves, probable = self._stream_args
        visible = self.stream_state.visible
        cards = build_cards(self.pokedex, rivals, own, levels, moves, probable,
                            self.config.stream_card_mode, self.config.language,
                            self.config.hidden_sections(self.config.stream_card_mode))
        self.stream_state.publish(cards)
        if keep_visibility:
            self.stream_state.set_visible(visible)

    def toggle_stream_card(self) -> None:
        self.stream_state.set_visible(not self.stream_state.visible)

    # ---- actualizaciones (spec update-check) ------------------------------------

    def check_for_updates(self, fetch=None) -> None:
        if not self.config.updates_check or not due(self.state.last_update_check):
            return
        task = _Task(check_latest, *(() if fetch is None else (__version__, fetch)))
        task.signals.finished.connect(self._on_update_checked)
        task.signals.failed.connect(lambda exc: log.info("Comprobación de actualizaciones: %s", exc))
        self._pool.start(task)

    def _on_update_checked(self, release: Release | None) -> None:
        self.state.last_update_check = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self._save_state()
        if release is not None:
            self.release = release
            self.tray.show_update(release.version)
            if self._settings is not None:
                self._settings.set_update(release.version)
            self.tray.notify(_("BattleLens {version} disponible. Descárgala desde el menú de la bandeja.",
                               version=release.version))

    def open_update(self) -> None:
        if self.release is not None:
            QDesktopServices.openUrl(QUrl(self.release.url))

    # ---- informe de un problema (spec problem-report) ------------------------------

    def show_report(self) -> None:
        dialog = ReportDialog(self.target is not None)
        self._modal_open = True
        try:
            accepted = dialog.exec()
        finally:
            self._modal_open = False
        if accepted:
            self.create_report(*dialog.values())

    def create_report(self, description: str, include_capture: bool, open_form: bool) -> None:
        self.tray.notify(_("Creando el informe…"))
        target = self.target if include_capture else None
        task = _Task(self._build_report, description, target, self.profiles.active)
        task.signals.finished.connect(lambda result: self._on_report_ready(result, open_form))
        task.signals.failed.connect(
            lambda exc: self.tray.notify(_("No se pudo crear el informe: {error}", error=exc), warning=True))
        self._pool.start(task)

    def _report_summary(self, profile: Profile | None, target) -> dict:
        import platform

        from . import i18n

        try:
            ocr_languages = available_languages()
        except Exception as exc:  # noqa: BLE001 - el informe se crea aunque falle el OCR
            ocr_languages = f"error: {exc}"
        game = self.pokedex.get_game(profile.game) if profile else None
        return {
            "version": __version__,
            "windows": platform.platform(),
            "ocr_idiomas": ocr_languages,
            "idioma_interfaz": i18n.get_language(),
            "idioma_datos": self.config.language,
            "modo_ficha": self.config.overlay_mode,
            "deteccion_automatica": self.auto_detect,
            "modo_stream": self.config.stream_enabled,
            "emulador": {"exe": target.exe, "titulo": target.title} if target else None,
            "perfil": None if profile is None else {
                "nombre": profile.name,
                "juego": profile.game,
                "nombre_juego": game.name("en") if game else None,
                "regiones": {role: vars(region) for role, region in profile.regions().items()},
                "menu_ataques": vars(profile.moves_region) if profile.moves_region else None,
                "idiomas_ocr": list(profile.ocr_languages),
            },
        }

    def _build_report(self, description: str, target, profile: Profile | None):
        """En el pool: captura, recortes, lecturas y ZIP; la captura puede fallar sin impedir el informe."""
        inputs = ReportInputs(self.data_dir, self._report_summary(profile, target), description)
        if target is not None:
            try:
                frame = capture_client(target.hwnd)
                inputs.emulator_image = frame
                if profile is not None:
                    inputs.region_crops = crop_regions(frame, profile)
                    if profile.moves_region is not None:
                        inputs.region_crops["moves"] = crop_region(frame, profile.moves_region)
                    inputs.readings = self._report_readings(inputs.region_crops, profile)
            except CaptureError as exc:
                inputs.capture_error = f"{type(exc).__name__}: {exc}"
        path = write_report(inputs)
        game = self.pokedex.get_game(profile.game) if profile else None
        url = issue_form_url(__version__, target.exe if target else None, game.name("en") if game else None)
        return path, url

    def _report_readings(self, crops: dict, profile: Profile) -> dict:
        readings: dict[str, dict] = {}
        for role, crop in crops.items():
            try:
                if role == "moves":
                    moves = read_moves(crop, recognize, self.move_matcher(), profile.ocr_languages)
                    readings[role] = {"movimientos": [m.identifier for m in moves]}
                    continue
                reading = read_crop(crop, recognize, self.pipeline.matcher, profile.ocr_languages)
                species = reading.match.species_id
                readings[role] = {
                    "texto": reading.match.raw_text,
                    "especie": self.pokedex.get_species(species).identifier if species else None,
                    "puntuacion": round(reading.match.score, 1),
                    "nivel": reading.level,
                    "lecturas": list(reading.readings),
                }
            except Exception as exc:  # noqa: BLE001 - una región ilegible no impide el informe
                readings[role] = {"error": f"{type(exc).__name__}: {exc}"}
        return readings

    def _on_report_ready(self, result, open_form: bool) -> None:
        path, url = result
        self.tray.notify(_("Informe creado: {path}", path=path))
        try:
            subprocess.Popen(["explorer", f"/select,{path}"])
        except OSError as exc:
            log.warning("No se pudo abrir el Explorador: %s", exc)
        if open_form:
            QDesktopServices.openUrl(QUrl(url))

    def _on_hotkey(self, name: str) -> None:
        {
            "recognize": self.recognize,
            "calibrate": self.calibrate_new,
            "hide": self.hide_overlay,
            "toggle_mode": self.toggle_mode,
            "cycle_form": self.cycle_form,
            "toggle_stream": self.toggle_stream_card,
        }[name]()

    # ---- modos de ficha (spec display-modes) ---------------------------------------

    def set_mode(self, mode: str) -> None:
        if mode != self.config.overlay_mode:
            new = replace(self.config, overlay_mode=mode)
            save_config(self.data_dir / "config.toml", new)
            self.config = new
        self.overlay.mode = mode
        self.tray.set_mode(mode)
        self._sync_settings("mode", mode)
        self._redraw_last_battle()

    def toggle_mode(self) -> None:
        mode = "normal" if self.config.overlay_mode == "competitive" else "competitive"
        self.set_mode(mode)
        self.tray.notify(_("Ficha: Competitivo") if mode == "competitive" else _("Ficha: Normal"))

    def _redraw_last_battle(self) -> None:
        if self._last_battle is not None and self.overlay.isVisible():
            key, game, levels = self._last_battle
            self._show_battle(key, game, self._target_rect(), levels)

    def cycle_form(self) -> None:
        """Siguiente forma del primer rival que tenga otras en el juego (spec battle-overlay)."""
        if self._last_battle is None or not self.overlay.isVisible():
            return
        (rival, rival2, _), game, _ = self._last_battle
        for sid in (rival, rival2):
            if sid is None:
                continue
            cycle = self.pokedex.form_cycle(sid, game)
            if len(cycle) > 1:
                current = self._form_choice.get(sid, cycle[0])
                index = cycle.index(current) if current in cycle else 0
                self._form_choice[sid] = cycle[(index + 1) % len(cycle)]
                self._redraw_last_battle()
                return

    def _end_battle(self) -> None:
        """Fin del combate según la detección automática: se ocultan la ficha y la del stream."""
        self.overlay.hide()
        self.stream_state.set_visible(False)

    def hide_overlay(self) -> None:
        self.overlay.hide()
        self.battle.on_hidden_by_user()

    # ---- detección automática ----------------------------------------------

    @property
    def auto_detect(self) -> bool:
        return self._watch_timer.isActive()

    def set_auto_detect(self, enabled: bool) -> None:
        self.state.auto_detect = enabled
        self._save_state()
        self.battle.reset()
        if enabled:
            self._watch_timer.start()
        else:
            self._watch_timer.stop()
        self.tray.set_auto_detect(enabled)
        self._sync_settings("detection_enabled", enabled)

    def _watch_tick(self) -> None:
        if self._watch_busy or self._busy or self._modal_open or self.target is None:
            return
        self._auto_select_profile()
        profile = self.profiles.active
        if profile is None:
            return
        self._watch_busy = True
        task = _Task(self._capture_crop, self.target.hwnd, profile)
        task.signals.finished.connect(self._on_watch_frame)
        task.signals.failed.connect(self._on_watch_error)
        self._pool.start(task)

    @staticmethod
    def _capture_crop(hwnd: int, profile: Profile):
        frame = capture_client(hwnd)
        crops = crop_regions(frame, profile)
        moves_crop = crop_region(frame, profile.moves_region) if profile.moves_region is not None else None
        return crops, combined_fingerprint(crops), profile, moves_crop

    def _on_watch_frame(self, payload) -> None:
        self._watch_busy = False
        crop, fp, profile, moves_crop = payload
        if moves_crop is not None:
            self._watch_moves(moves_crop, profile)
        action = self.battle.on_frame(fp, time.monotonic())
        if action is Action.HIDE:
            self._end_battle()
        elif action is Action.RECOGNIZE and not self._busy:
            self._busy = True
            task = _Task(self._read_auto, crop, fp, profile)
            task.signals.finished.connect(self._on_auto_result)
            task.signals.failed.connect(self._on_auto_failure)
            self._pool.start(task)

    def _read_auto(self, crops, fp, profile: Profile):
        readings = read_regions(crops, recognize, self.pipeline.matcher, profile.ocr_languages)
        key = tuple(readings[r].match.species_id if r in readings else None for r in ("rival", "rival2", "own"))
        return key, fp, profile, levels_of(readings)

    # ---- menú de ataques (spec own-moves) ------------------------------------------

    def move_matcher(self) -> MoveMatcher:
        if self._move_matcher is None:
            self._move_matcher = MoveMatcher(Learnsets.get().all_moves())
        return self._move_matcher

    def _watch_moves(self, moves_crop, profile: Profile) -> None:
        moves_fp = fingerprint(moves_crop)
        if not self.moves_watcher.on_frame(moves_fp) or self._moves_busy:
            return
        self.moves_watcher.attempted(moves_fp)
        self._moves_busy = True
        task = _Task(self._read_moves, moves_crop, profile)
        task.signals.finished.connect(self._on_moves_read)
        task.signals.failed.connect(self._on_moves_failure)
        self._pool.start(task)

    def _read_moves(self, moves_crop, profile: Profile):
        return profile, read_moves(moves_crop, recognize, self.move_matcher(), profile.ocr_languages)

    def _on_moves_read(self, payload) -> None:
        self._moves_busy = False
        profile, moves = payload
        self._remember_moves(profile, moves)

    def _on_moves_failure(self, exc: Exception) -> None:
        self._moves_busy = False
        log.debug("Lectura del menú de ataques omitida: %s", exc)

    def _remember_moves(self, profile: Profile, moves) -> None:
        """Guarda los movimientos leídos para tu Pokémon actual y redibuja si cambian (D4)."""
        own = self._last_battle[0][2] if self._last_battle is not None else None
        if not moves or own is None:
            return
        if self.move_memory.store(profile.id, own, [m.identifier for m in moves]):
            log.info("Movimientos de tu Pokémon %s: %s", own, [m.identifier for m in moves])
            self._redraw_last_battle()

    def _own_moves(self, own_view, own_level):
        """(movimientos, probables): los guardados de tu Pokémon o, si no hay, los probables a su nivel."""
        profile = self.profiles.active
        try:
            learnsets = Learnsets.get()
        except LearnsetsMissingError:
            return [], False
        stored = self.move_memory.get(profile.id, own_view.species_id) if profile else []
        moves = [m for m in (learnsets.move(i) for i in stored) if m is not None]
        if moves:
            return moves, False
        if own_level:
            game = self.pokedex.get_game(own_view.game_id)
            return learnsets.probable_moves(own_view.pokemon or "", own_level, own_view.game_id,
                                            game.generation if game else None), True
        return [], False

    def _on_auto_result(self, payload) -> None:
        self._busy = False
        key, fp, profile, levels = payload
        if self.battle.on_result(key, fp, time.monotonic()) is Action.SHOW:
            log.info("Detección automática: %s (niveles %s)", key, levels)
            self._show_battle(key, profile.game, self._target_rect(), levels)

    def _show_battle(self, key, game: str | None, rect, levels=(None, None, None)) -> None:
        """Muestra las tarjetas de los rivales de la clave (rival, rival2, own) y la comparativa."""
        self._last_battle = (key, game, levels)
        rival, rival2, own = key
        lang = self.config.language
        pairs = [(sid, lvl) for sid, lvl in zip((rival, rival2), levels[:2]) if sid is not None]
        # La forma elegida se olvida cuando la especie deja de estar entre los rivales (add-alternate-forms D4)
        self._form_choice = {sid: f for sid, f in self._form_choice.items() if sid in (rival, rival2)}
        self.overlay.form_hotkey = self.config.hotkey_cycle_form
        rivals = [self.pokedex.view(sid, game, lang, self._form_choice.get(sid)) for sid, _ in pairs]
        own_view = self.pokedex.view(own, game, lang) if own is not None else None
        own_moves, probable = self._own_moves(own_view, levels[2]) if own_view is not None else ([], False)
        self.overlay.show_battle(rivals, own_view, rect, [lvl for _, lvl in pairs], levels[2], own_moves, probable)
        self._stream_args = (rivals, own_view, [lvl for _, lvl in pairs], own_moves, probable)
        self._publish_stream()

    def _on_auto_failure(self, exc: Exception) -> None:
        self._busy = False
        log.warning("Fallo en el reconocimiento automático: %s", exc)

    def _on_watch_error(self, exc: Exception) -> None:
        self._watch_busy = False
        if isinstance(exc, WindowUnavailable):
            self._set_target(None)
            self.tray.notify(str(exc), warning=True)
        elif not isinstance(exc, WindowMinimized):
            log.debug("Ciclo de vigilancia omitido: %s", exc)

    def recognize(self) -> None:
        if self._busy:
            log.info("Reconocimiento en curso; pulsación ignorada")
            return
        if self.target is None:
            self.tray.notify(_("Selecciona primero la ventana del emulador."), warning=True)
            return
        self._auto_select_profile()
        profile = self.profiles.active
        if profile is None:
            self.tray.notify(_("No hay perfiles: calibra primero la región del nombre."), warning=True)
            return
        if profile.moves_region is not None:
            self.pipeline.move_matcher = self.move_matcher()
        self._busy = True
        self._recognition_game = profile.game
        task = _Task(self.pipeline.run, self.target.hwnd, profile)
        task.signals.finished.connect(self._on_result)
        task.signals.failed.connect(self._on_failure)
        self._pool.start(task)

    def _on_result(self, result: RecognitionResult) -> None:
        self._busy = False
        rect = self._target_rect()
        if result.any_rival:
            self._show_battle(result.key, self._recognition_game, rect, result.levels)
            if self.profiles.active is not None:
                self._remember_moves(self.profiles.active, result.moves)
            self.battle.on_manual_result(result.key, result.fingerprint)
        else:
            self.overlay.show_unrecognized(result.match.raw_text, rect)

    def _on_failure(self, exc: Exception) -> None:
        self._busy = False
        if isinstance(exc, WindowUnavailable):
            self._set_target(None)
        if isinstance(exc, (CaptureError, OcrLanguageError)):
            self.tray.notify(str(exc), warning=True)
        else:
            log.error("Error inesperado en el reconocimiento", exc_info=exc)
            self.tray.notify(_("Error inesperado: {error}", error=exc), warning=True)

    def _target_rect(self) -> tuple[int, int, int, int] | None:
        if self.target is None or not windows.is_window(self.target.hwnd):
            return None
        try:
            return windows.client_rect_on_screen(self.target.hwnd)
        except OSError:
            return None

    def select_window(self, info: windows.WindowInfo) -> None:
        self._set_target(info)
        self._auto_select_profile()

    def _current_title(self) -> str | None:
        if self.target is None or not windows.is_window(self.target.hwnd):
            return None
        return windows.window_title(self.target.hwnd) or self.target.title

    def _auto_select_profile(self) -> None:
        """Activa el perfil del juego detectado en el título de la ventana, si existe (game-profiles)."""
        game_id = self.detector.detect(self._current_title())
        if game_id is None:
            return
        profile = self.profiles.find_by_game(game_id)
        if profile is None or profile.id == self.profiles.active_id:
            return
        self.profiles.set_active(profile.id)
        self._save_state()
        self._refresh_ui()
        game = self.pokedex.get_game(game_id)
        self.tray.notify(_("Perfil «{name}» activado ({game}).", name=profile.name, game=game.name(self.config.language)))

    def set_profile_game(self, game_id: str | None) -> None:
        profile = self.profiles.active
        if profile is None:
            return
        self.profiles.save(profile.with_game(game_id), activate=True)
        game = self.pokedex.get_game(game_id)
        label = game.name(self.config.language) if game else _("sin especificar")
        self._refresh_ui()
        self.tray.notify(_("Juego de «{name}»: {game}.", name=profile.name, game=label))

    def _set_target(self, info: windows.WindowInfo | None) -> None:
        self.target = info
        self.state.last_window_exe = info.exe if info else None
        self.state.last_window_title = info.title if info else None
        self._save_state()
        self._refresh_ui()

    def select_profile(self, profile_id: str) -> None:
        self.profiles.set_active(profile_id)
        self._save_state()
        self._refresh_ui()

    def _capture_for_calibration(self):
        if self.target is None:
            self.tray.notify(_("Selecciona primero la ventana del emulador."), warning=True)
            return None
        try:
            return capture_client(self.target.hwnd)
        except CaptureError as exc:
            if isinstance(exc, WindowUnavailable):
                self._set_target(None)
            self.tray.notify(str(exc), warning=True)
            return None

    def calibrate_new(self) -> None:
        image = self._capture_for_calibration()
        if image is None:
            return
        self._modal_open = True
        try:
            self._calibrate_new_with(image)
        finally:
            self._modal_open = False

    # ---- perfiles con preset (spec game-presets) ----------------------------------

    def new_profile_from_preset(self) -> None:
        image = self._capture_for_calibration()
        if image is None:
            return
        self._modal_open = True
        try:
            self._new_profile_from_preset_with(image)
        finally:
            self._modal_open = False

    def _preset_reading(self, role: str, crop) -> str:
        """Lo que lee BattleLens en un recuadro del asistente: especie (o texto) y nivel."""
        profile_languages = self.profiles.active.ocr_languages if self.profiles.active else ("es", "en")
        try:
            if role == "moves":
                moves = read_moves(crop, recognize, self.move_matcher(), profile_languages)
                return ", ".join(m.name(self.config.language) for m in moves)
            reading = read_crop(crop, recognize, self.pipeline.matcher, profile_languages)
        except Exception as exc:  # noqa: BLE001 - el asistente sigue aunque falle una lectura
            return str(exc)
        match = reading.match
        if not match.recognized:
            return match.raw_text.strip()
        name = self.pokedex.get_species(match.species_id).name(self.config.language)
        level = _(" · Nv. {level}", level=reading.level) if reading.level else ""
        return f"{name}{level}"

    def _new_profile_from_preset_with(self, image) -> None:
        lang = self.config.language
        detection = self.detector.detect_version(self._current_title())
        games = [(g.id, g.name(lang)) for g in self.pokedex.games if preset_for(g.id)]
        wizard = PresetWizard(image, games, detection.game_id if detection else None, self._preset_reading)
        if not wizard.exec() or wizard.action is None:
            return
        if wizard.action == "manual":
            self._calibrate_new_with(image)
            return
        game = self.pokedex.get_game(wizard.game_id)
        if detection is not None and detection.game_id == wizard.game_id:
            default_name = f"Pokémon {detection.version_name(lang)}"
        else:
            default_name = f"Pokémon {game.name(lang)}" if game else _("Mi juego")
        answer = ask_profile(default_name, self.pokedex.games, wizard.game_id, lang)
        if answer is None:
            return
        name, game_id = answer
        h, w = image.shape[:2]
        regions = to_profile_regions(wizard.preset, wizard.viewport, w, h)
        profile = Profile(name, regions["rival"], game=game_id, own_region=regions.get("own"),
                          moves_region=regions.get("moves"))
        self.profiles.save(profile, activate=True)
        self.battle.reset()
        self._save_state()
        self._refresh_ui()
        self.tray.notify(_("Perfil «{name}» creado y activo.", name=name))

    def _calibrate_new_with(self, image) -> None:
        dialog = CalibrationDialog(image, _("Calibrar nuevo perfil"))
        if not dialog.exec() or dialog.region is None:
            return
        detection = self.detector.detect_version(self._current_title())
        lang = self.config.language
        if detection is not None:
            default_name = f"Pokémon {detection.version_name(lang)}"
        else:
            default_name = self.target.title if self.target else _("Mi juego")
        answer = ask_profile(default_name, self.pokedex.games, detection.game_id if detection else None, lang)
        if answer is None:
            return
        name, game_id = answer
        profile = Profile(name, dialog.region, game=game_id)
        self.profiles.save(profile, activate=True)
        self._save_state()
        self._refresh_ui()
        self.tray.notify(_("Perfil «{name}» creado y activo.", name=name))

    REGION_TARGETS = {
        "rival": N_("nombre del Pokémon rival"),
        "rival2": N_("nombre del 2.º Pokémon rival"),
        "own": N_("nombre de tu Pokémon"),
        "moves": N_("menú de ataques (los 4 movimientos)"),
    }

    def calibrate_region(self, role: str) -> None:
        profile = self.profiles.active
        if profile is None:
            return
        image = self._capture_for_calibration()
        if image is None:
            return
        target = _(self.REGION_TARGETS[role])
        dialog = CalibrationDialog(image, _("«{name}»: {target}", name=profile.name, target=target), target)
        self._modal_open = True
        try:
            accepted = dialog.exec()
        finally:
            self._modal_open = False
        if accepted and dialog.region is not None:
            self._save_region(profile, role, dialog.region)

    def _save_region(self, profile: Profile, role: str, region) -> None:
        self.profiles.save(profile.with_role_region(role, region), activate=True)
        self.battle.reset()  # la huella cambia de forma al cambiar las regiones
        self.moves_watcher.reset()
        self._refresh_ui()
        self.tray.notify(_("«{name}»: región del {target} guardada.", name=profile.name,
                           target=_(self.REGION_TARGETS[role])))

    def remove_region(self, role: str) -> None:
        profile = self.profiles.active
        if profile is None or role == "rival":
            return
        self.profiles.save(profile.with_role_region(role, None), activate=True)
        self.battle.reset()
        self._refresh_ui()
        self.tray.notify(_("«{name}»: región del {target} quitada.", name=profile.name,
                           target=_(self.REGION_TARGETS[role])))

    def delete_profile(self) -> None:
        profile = self.profiles.active
        if profile is None:
            return
        answer = QMessageBox.question(None, _("Eliminar perfil"), _("¿Eliminar el perfil «{name}»?", name=profile.name))
        if answer == QMessageBox.StandardButton.Yes:
            self.profiles.delete(profile.id)
            self._save_state()
            self._refresh_ui()

    def _on_overlay_collapsed(self) -> None:
        self.state.collapsed_sections = {mode: sorted(keys) for mode, keys in self.overlay.collapsed.items() if keys}
        self._save_state()

    def expand_all_sections(self) -> None:
        """«Desplegar todas las secciones» (improve-card-visuals)."""
        self.overlay.expand_all()  # emite collapsed_changed, que lo guarda en state.json

    def _on_overlay_moved(self, x: int, y: int) -> None:
        self.state.overlay_pos = [x, y]
        self._save_state()

    def _save_state(self) -> None:
        self.state.active_profile = self.profiles.active_id
        try:
            self.state.save(self.state_path)
        except OSError as exc:
            log.warning("No se pudo guardar state.json: %s", exc)

    def quit(self) -> None:
        self._watch_timer.stop()
        self.stream_server.stop()
        self.hotkeys.stop()
        self._save_state()
        if self._settings is not None:
            self._settings.hide()
        self.tray.hide()
        self.app.quit()


def _setup_logging() -> None:
    log_dir = app_data_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    handlers: list[logging.Handler] = [
        RotatingFileHandler(log_dir / "app.log", maxBytes=1_000_000, backupCount=2, encoding="utf-8")
    ]
    if sys.stderr is not None:
        handlers.append(logging.StreamHandler())
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", handlers=handlers
    )


def _fatal(message: str) -> int:
    QMessageBox.critical(None, APP_NAME, message)
    return 1


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="BattleLens", add_help=False)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--self-test-output", type=Path)
    args, _qt_args = parser.parse_known_args(argv)
    return args


def _windows_language() -> str | None:
    try:
        return ui_language_tag()
    except (OSError, AttributeError):  # fuera de Windows o sin la API
        return None


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    if args.self_test:
        from . import selftest

        return selftest.main(args.self_test_output)

    _setup_logging()
    app = QApplication(sys.argv)
    app.setWindowIcon(app_icon())
    # Botones estándar de Qt (Sí/No, Cancelar…) en el idioma del sistema
    translator = QTranslator(app)
    if translator.load(QLocale.system(), "qtbase", "_", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
        app.installTranslator(translator)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)
    set_language(resolve_language("auto", _windows_language()))  # hasta leer config.toml

    instance = SingleInstance()
    if instance.already_running:
        QMessageBox.information(None, APP_NAME, _("La aplicación ya se está ejecutando (mira la bandeja)."))
        return 0

    try:
        config = load_config(app_data_dir() / "config.toml")
        set_language(resolve_language(config.interface_language, _windows_language()))
        pokedex = Pokedex.load()
    except (ConfigError, DatasetMissingError) as exc:
        return _fatal(str(exc))

    controller = Controller(app, config, pokedex)  # noqa: F841 (mantiene vivos los objetos)
    log.info("Aplicación iniciada")
    code = app.exec()
    instance.release()
    return code


if __name__ == "__main__":
    sys.exit(main())
