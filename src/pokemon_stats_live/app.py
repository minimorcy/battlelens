"""Punto de entrada: une configuración, atajos, pipeline, overlay y bandeja."""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from PyQt6.QtCore import QObject, QPoint, QRunnable, QThreadPool, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMessageBox

from .core.config import AppState, Config, ConfigError, load_config
from .core.matcher import NameMatcher
from .core.pokedex import DatasetMissingError, Pokedex
from .core.profiles import Profile, ProfileStore
from .core.storage import app_data_dir
from .pipeline import RecognitionPipeline, RecognitionResult
from .platform import windows
from .platform.capture import CaptureError, WindowUnavailable, capture_client
from .platform.hotkeys import Hotkey, HotkeyManager, HotkeyParseError, parse_hotkey
from .platform.ocr import OcrLanguageError, recognize, resolve_languages
from .platform.single_instance import SingleInstance
from .ui.calibrator import CalibrationDialog, ask_profile_name
from .ui.overlay import Overlay
from .ui.tray import Tray

log = logging.getLogger("pokemon_stats_live")


class _WorkerSignals(QObject):
    finished = pyqtSignal(object)
    failed = pyqtSignal(object)


class _RecognitionTask(QRunnable):
    def __init__(self, pipeline: RecognitionPipeline, hwnd: int, profile: Profile) -> None:
        super().__init__()
        self.signals = _WorkerSignals()
        self._pipeline, self._hwnd, self._profile = pipeline, hwnd, profile

    def run(self) -> None:
        try:
            self.signals.finished.emit(self._pipeline.run(self._hwnd, self._profile))
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
        self._pool = QThreadPool.globalInstance()

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
        )
        self.tray.recognize_requested.connect(self.recognize)
        self.tray.window_selected.connect(self.select_window)
        self.tray.profile_selected.connect(self.select_profile)
        self.tray.calibrate_requested.connect(self.calibrate_new)
        self.tray.recalibrate_requested.connect(self.recalibrate)
        self.tray.delete_profile_requested.connect(self.delete_profile)
        self.tray.open_data_requested.connect(lambda: os.startfile(self.data_dir))
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
        try:
            resolve_languages(("es", "en"))
        except OcrLanguageError as exc:
            notices.append(str(exc))
        if self.target is None:
            notices.append("Selecciona la ventana del emulador en el menú de la bandeja.")
        elif self.profiles.active is None:
            notices.append("Calibra un perfil para este juego (menú de la bandeja o atajo de calibrar).")
        if notices:
            self.tray.notify("\n".join(notices), warning=bool(failed))
        else:
            self.tray.notify(f"Listo. Pulsa {self.config.hotkey_recognize} en un combate.")

    # ---- acciones ----------------------------------------------------------

    def _on_hotkey(self, name: str) -> None:
        {"recognize": self.recognize, "calibrate": self.calibrate_new, "hide": self.overlay.hide}[name]()

    def recognize(self) -> None:
        if self._busy:
            log.info("Reconocimiento en curso; pulsación ignorada")
            return
        if self.target is None:
            self.tray.notify("Selecciona primero la ventana del emulador.", warning=True)
            return
        profile = self.profiles.active
        if profile is None:
            self.tray.notify("No hay perfiles: calibra primero la región del nombre.", warning=True)
            return
        self._busy = True
        task = _RecognitionTask(self.pipeline, self.target.hwnd, profile)
        task.signals.finished.connect(self._on_result)
        task.signals.failed.connect(self._on_failure)
        self._pool.start(task)

    def _on_result(self, result: RecognitionResult) -> None:
        self._busy = False
        rect = self._target_rect()
        if result.recognized:
            self.overlay.show_species(result.species, rect)
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
        default_name = self.target.title if self.target else "Mi juego"
        name = ask_profile_name(default_name)
        if name is None:
            return
        profile = Profile(name, dialog.region)
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
    QMessageBox.critical(None, "Pokémon Stats Live", message)
    return 1


def main() -> int:
    _setup_logging()
    app = QApplication(sys.argv)
    app.setApplicationName("Pokémon Stats Live")
    app.setQuitOnLastWindowClosed(False)

    instance = SingleInstance()
    if instance.already_running:
        QMessageBox.information(None, "Pokémon Stats Live", "La aplicación ya se está ejecutando (mira la bandeja).")
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
