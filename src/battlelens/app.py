"""Punto de entrada: une configuración, atajos, pipeline, overlay y bandeja."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from PyQt6.QtCore import QLibraryInfo, QLocale, QObject, QPoint, QRunnable, QThreadPool, QTranslator, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMessageBox

from . import APP_NAME
from .core.config import AppState, Config, ConfigError, load_config
from .core.games import GameDetector
from .core.matcher import NameMatcher
from .core.pokedex import DatasetMissingError, Pokedex
from .core.profiles import Profile, ProfileStore
from .core.storage import app_data_dir
from .pipeline import RecognitionPipeline, RecognitionResult
from .platform import windows
from .platform.capture import CaptureError, WindowUnavailable, capture_client
from .platform.hotkeys import Hotkey, HotkeyManager, HotkeyParseError, parse_hotkey
from .platform.ocr import OcrLanguageError, recognize, resolve_languages
from .platform.ocr_setup import (
    MANUAL_INSTRUCTIONS,
    InstallOutcome,
    InstallResult,
    install_ocr,
    proposed_ocr_tag,
    ui_language_tag,
)
from .platform.single_instance import SingleInstance
from .ui.about import AboutDialog
from .ui.calibrator import CalibrationDialog, ask_profile
from .ui.icons import app_icon
from .ui.overlay import Overlay
from .ui.tray import Tray

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

        self.overlay = Overlay(pokedex, config.language, config.auto_hide_seconds)
        if self.state.overlay_pos:
            self.overlay.saved_pos = QPoint(*self.state.overlay_pos)
        self.overlay.moved.connect(self._on_overlay_moved)

        bindings, invalid = self._parse_hotkeys()
        self.tray = Tray(
            windows.list_windows,
            lambda: self.target,
            lambda: (self.profiles.sorted_profiles(), self.profiles.active_id),
            {name: hk.text for name, hk in bindings.items()},
            lambda: [(g.id, f"Gen {g.generation} · {g.name(config.language)}") for g in pokedex.games],
        )
        self.tray.recognize_requested.connect(self.recognize)
        self.tray.window_selected.connect(self.select_window)
        self.tray.profile_selected.connect(self.select_profile)
        self.tray.profile_game_selected.connect(self.set_profile_game)
        self.tray.calibrate_requested.connect(self.calibrate_new)
        self.tray.recalibrate_requested.connect(self.recalibrate)
        self.tray.delete_profile_requested.connect(self.delete_profile)
        self.tray.open_data_requested.connect(lambda: os.startfile(self.data_dir))
        self.tray.install_ocr_requested.connect(self.install_ocr)
        self.tray.about_requested.connect(self.show_about)
        self._about: AboutDialog | None = None
        self.tray.quit_requested.connect(self.quit)
        self.tray.show()

        self.hotkeys = HotkeyManager(bindings)
        self.hotkeys.triggered.connect(self._on_hotkey)
        failed = self.hotkeys.start() + invalid
        self._startup_notices(failed, bindings)

    # ---- arranque ----------------------------------------------------------

    def _parse_hotkeys(self) -> tuple[dict[str, Hotkey], list[str]]:
        bindings: dict[str, Hotkey] = {}
        invalid: list[str] = []
        for name, text in (
            ("recognize", self.config.hotkey_recognize),
            ("calibrate", self.config.hotkey_calibrate),
            ("hide", self.config.hotkey_hide),
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
            labels = {"recognize": "reconocer", "calibrate": "calibrar", "hide": "ocultar"}
            detail = ", ".join(
                f"{labels[n]} ({bindings[n].text})" if n in bindings else f"{labels[n]} (inválido)" for n in failed
            )
            notices.append(f"No se pudieron registrar los atajos: {detail}. Cámbialos en config.toml.")
        if not self.ocr_available():
            self.tray.set_ocr_missing(True)
            notices.append("Falta el OCR de Windows. Instálalo desde el menú de la bandeja: «Instalar OCR de Windows…».")
        if self.target is None:
            notices.append("Selecciona la ventana del emulador en el menú de la bandeja.")
        elif self.profiles.active is None:
            notices.append("Calibra un perfil para este juego (menú de la bandeja o atajo de calibrar).")
        if notices:
            self.tray.notify("\n".join(notices), warning=bool(failed))
        else:
            self.tray.notify(f"Listo. Pulsa {self.config.hotkey_recognize} en un combate.")

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
            "Instalar OCR de Windows",
            f"Se instalará el reconocimiento de texto de Windows ({tag}).\n\n"
            "Windows pedirá permiso de administrador y la descarga puede tardar unos minutos.",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.tray.notify("Instalando el OCR de Windows… Te aviso al terminar.")
        task = _Task(install_ocr, tag)
        task.signals.finished.connect(self._on_ocr_installed)
        task.signals.failed.connect(
            lambda exc: self._on_ocr_installed(InstallResult(InstallOutcome.FAILED, tag, None))
        )
        self._pool.start(task)

    def _on_ocr_installed(self, result: InstallResult) -> None:
        if result.outcome is InstallOutcome.CANCELLED:
            self.tray.notify("Instalación cancelada.")
        elif result.outcome is InstallOutcome.FAILED:
            log.warning("Fallo al instalar el OCR %s (código %s)", result.tag, result.exit_code)
            QMessageBox.warning(
                None, "OCR de Windows", f"No se pudo instalar el OCR ({result.tag}).\n\n{MANUAL_INSTRUCTIONS}"
            )
        elif self.ocr_available():
            self.tray.set_ocr_missing(False)
            self.tray.notify(f"OCR instalado. Ya puedes reconocer con {self.config.hotkey_recognize}.")
        else:
            self.tray.notify("OCR instalado. Reinicia BattleLens para empezar a usarlo.")

    def show_about(self) -> None:
        self._about = AboutDialog()
        self._about.show()
        self._about.raise_()
        self._about.activateWindow()

    def _on_hotkey(self, name: str) -> None:
        {"recognize": self.recognize, "calibrate": self.calibrate_new, "hide": self.overlay.hide}[name]()

    def recognize(self) -> None:
        if self._busy:
            log.info("Reconocimiento en curso; pulsación ignorada")
            return
        if self.target is None:
            self.tray.notify("Selecciona primero la ventana del emulador.", warning=True)
            return
        self._auto_select_profile()
        profile = self.profiles.active
        if profile is None:
            self.tray.notify("No hay perfiles: calibra primero la región del nombre.", warning=True)
            return
        self._busy = True
        self._recognition_game = profile.game
        task = _Task(self.pipeline.run, self.target.hwnd, profile)
        task.signals.finished.connect(self._on_result)
        task.signals.failed.connect(self._on_failure)
        self._pool.start(task)

    def _on_result(self, result: RecognitionResult) -> None:
        self._busy = False
        rect = self._target_rect()
        if result.recognized:
            self.overlay.show_species(result.species, rect, game=self._recognition_game)
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
            self.tray.notify(f"Error inesperado: {exc}", warning=True)

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
        self.tray.refresh_tooltip()
        game = self.pokedex.get_game(game_id)
        self.tray.notify(f"Perfil «{profile.name}» activado ({game.name(self.config.language)}).")

    def set_profile_game(self, game_id: str | None) -> None:
        profile = self.profiles.active
        if profile is None:
            return
        self.profiles.save(profile.with_game(game_id), activate=True)
        game = self.pokedex.get_game(game_id)
        label = game.name(self.config.language) if game else "sin especificar"
        self.tray.notify(f"Juego de «{profile.name}»: {label}.")

    def _set_target(self, info: windows.WindowInfo | None) -> None:
        self.target = info
        self.state.last_window_exe = info.exe if info else None
        self.state.last_window_title = info.title if info else None
        self._save_state()
        self.tray.refresh_tooltip()

    def select_profile(self, profile_id: str) -> None:
        self.profiles.set_active(profile_id)
        self._save_state()
        self.tray.refresh_tooltip()

    def _capture_for_calibration(self):
        if self.target is None:
            self.tray.notify("Selecciona primero la ventana del emulador.", warning=True)
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
        dialog = CalibrationDialog(image, "Calibrar nuevo perfil")
        if not dialog.exec() or dialog.region is None:
            return
        detection = self.detector.detect_version(self._current_title())
        lang = self.config.language
        if detection is not None:
            default_name = f"Pokémon {detection.version_name(lang)}"
        else:
            default_name = self.target.title if self.target else "Mi juego"
        answer = ask_profile(default_name, self.pokedex.games, detection.game_id if detection else None, lang)
        if answer is None:
            return
        name, game_id = answer
        profile = Profile(name, dialog.region, game=game_id)
        self.profiles.save(profile, activate=True)
        self._save_state()
        self.tray.refresh_tooltip()
        self.tray.notify(f"Perfil «{name}» creado y activo.")

    def recalibrate(self) -> None:
        profile = self.profiles.active
        if profile is None:
            return
        image = self._capture_for_calibration()
        if image is None:
            return
        dialog = CalibrationDialog(image, f"Recalibrar «{profile.name}»")
        if dialog.exec() and dialog.region is not None:
            self.profiles.save(profile.with_region(dialog.region), activate=True)
            self.tray.notify(f"Región de «{profile.name}» actualizada.")

    def delete_profile(self) -> None:
        profile = self.profiles.active
        if profile is None:
            return
        answer = QMessageBox.question(None, "Eliminar perfil", f"¿Eliminar el perfil «{profile.name}»?")
        if answer == QMessageBox.StandardButton.Yes:
            self.profiles.delete(profile.id)
            self._save_state()
            self.tray.refresh_tooltip()

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
        self.hotkeys.stop()
        self._save_state()
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

    instance = SingleInstance()
    if instance.already_running:
        QMessageBox.information(None, APP_NAME, "La aplicación ya se está ejecutando (mira la bandeja).")
        return 0

    try:
        config = load_config(app_data_dir() / "config.toml")
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
