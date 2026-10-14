"""Icono y menú en la bandeja del sistema."""

from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QAction, QActionGroup
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon

from .. import APP_NAME
from ..i18n import N_, _
from ..core.profiles import Profile
from ..platform.windows import WindowInfo
from .icons import app_icon


class Tray(QObject):
    recognize_requested = pyqtSignal()
    auto_detect_toggled = pyqtSignal(bool)
    mode_selected = pyqtSignal(str)  # "normal" | "competitive"
    window_selected = pyqtSignal(object)  # WindowInfo
    profile_selected = pyqtSignal(str)
    profile_game_selected = pyqtSignal(object)  # id de juego o None
    calibrate_requested = pyqtSignal()
    recalibrate_requested = pyqtSignal()
    region_requested = pyqtSignal(str)  # calibrar "rival", "rival2", "own" o "moves"
    region_remove_requested = pyqtSignal(str)
    stream_toggled = pyqtSignal(bool)
    copy_stream_url_requested = pyqtSignal()
    delete_profile_requested = pyqtSignal()
    open_data_requested = pyqtSignal()
    install_ocr_requested = pyqtSignal()
    about_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    update_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(
        self,
        list_windows: Callable[[], list[WindowInfo]],
        get_target: Callable[[], WindowInfo | None],
        get_profiles: Callable[[], tuple[list[Profile], str | None]],
        hotkey_texts: dict[str, str],
        get_games: Callable[[], list[tuple[str, str]]] = lambda: [],
    ) -> None:
        super().__init__()
        self._list_windows = list_windows
        self._get_target = get_target
        self._get_profiles = get_profiles
        self._hotkeys = hotkey_texts
        self._get_games = get_games  # [(id, etiqueta)] ordenados por generación

        self.icon = QSystemTrayIcon(app_icon())
        self.menu = QMenu()
        self._build_menu()
        self.icon.setContextMenu(self.menu)
        self.icon.activated.connect(self._on_activated)
        self.refresh_tooltip()

    def show(self) -> None:
        self.icon.show()

    def hide(self) -> None:
        self.icon.hide()

    def notify(self, message: str, warning: bool = False) -> None:
        kind = QSystemTrayIcon.MessageIcon.Warning if warning else QSystemTrayIcon.MessageIcon.Information
        self.icon.showMessage(APP_NAME, message, kind, 4000)

    def set_hotkey_hints(self, hotkey_texts: dict[str, str]) -> None:
        self._hotkeys = hotkey_texts
        self._recognize_action.setText(_("Reconocer ahora") + self._hint("recognize"))
        self._calibrate_action.setText(_("Calibrar nuevo perfil…") + self._hint("calibrate"))

    def show_update(self, version: str) -> None:
        self.update_action.setText(_("Descargar BattleLens {version}…", version=version))
        self.update_action.setVisible(True)

    def set_mode(self, mode: str) -> None:
        for name, action in self.mode_actions.items():
            action.setChecked(name == mode)

    def set_stream(self, enabled: bool, url: str | None) -> None:
        self.stream_action.blockSignals(True)
        self.stream_action.setChecked(enabled)
        self.stream_action.blockSignals(False)
        self.copy_url_action.setEnabled(url is not None)
        self.copy_url_action.setText(_("Copiar URL para OBS ({url})", url=url) if url else _("Copiar URL para OBS"))

    def set_auto_detect(self, enabled: bool) -> None:
        self.auto_detect_action.blockSignals(True)
        self.auto_detect_action.setChecked(enabled)
        self.auto_detect_action.blockSignals(False)

    def set_ocr_missing(self, missing: bool) -> None:
        self.install_ocr_action.setVisible(missing)

    def refresh_tooltip(self) -> None:
        target = self._get_target()
        profiles, active_id = self._get_profiles()
        active = next((p for p in profiles if p.id == active_id), None)
        lines = [APP_NAME]
        lines.append(_("Ventana: {window}", window=target.exe if target else _("— selecciona una —")))
        lines.append(_("Perfil: {profile}", profile=active.name if active else _("— calibra uno —")))
        self.icon.setToolTip("\n".join(lines))

    def _hint(self, name: str) -> str:
        text = self._hotkeys.get(name)
        return f"\t{text}" if text else ""

    def _build_menu(self) -> None:
        m = self.menu
        recognize = self._recognize_action = m.addAction(_("Reconocer ahora") + self._hint("recognize"))
        recognize.triggered.connect(self.recognize_requested)
        self.auto_detect_action = m.addAction(_("Detección automática"))
        self.auto_detect_action.setCheckable(True)
        self.auto_detect_action.toggled.connect(self.auto_detect_toggled)
        self._mode_menu = m.addMenu(_("Modo de la ficha"))
        self._mode_group = QActionGroup(self._mode_menu)
        self.mode_actions: dict[str, QAction] = {}
        for mode, label in (("normal", _("Normal (aventura y captura)")), ("competitive", _("Competitivo (combate)"))):
            action = QAction(label + self._hint("toggle_mode"), self._mode_menu, checkable=True)
            action.triggered.connect(lambda _=False, md=mode: self.mode_selected.emit(md))
            self._mode_group.addAction(action)
            self._mode_menu.addAction(action)
            self.mode_actions[mode] = action
        self.stream_action = m.addAction(_("Modo stream (OBS)"))
        self.stream_action.setCheckable(True)
        self.stream_action.toggled.connect(self.stream_toggled)
        self.copy_url_action = m.addAction(_("Copiar URL para OBS"))
        self.copy_url_action.triggered.connect(self.copy_stream_url_requested)
        self.copy_url_action.setEnabled(False)
        m.addSeparator()

        self._windows_menu = m.addMenu(_("Ventana del emulador"))
        self._windows_menu.aboutToShow.connect(self._populate_windows)
        self._profiles_menu = m.addMenu(_("Perfil activo"))
        self._profiles_menu.aboutToShow.connect(self._populate_profiles)
        self._game_menu = m.addMenu(_("Juego del perfil activo"))
        self._game_menu.aboutToShow.connect(self._populate_games)

        self._calibrate_action = m.addAction(_("Calibrar nuevo perfil…") + self._hint("calibrate"))
        self._calibrate_action.triggered.connect(self.calibrate_requested)
        self._regions_menu = m.addMenu(_("Regiones del perfil"))
        self._regions_menu.aboutToShow.connect(self._populate_regions)
        self._delete = m.addAction(_("Eliminar perfil activo…"))
        self._delete.triggered.connect(self.delete_profile_requested)
        m.addSeparator()
        self.install_ocr_action = m.addAction(_("Instalar OCR de Windows…"))
        self.install_ocr_action.triggered.connect(self.install_ocr_requested)
        self.install_ocr_action.setVisible(False)
        m.addAction(_("Ajustes…")).triggered.connect(self.settings_requested)
        m.addAction(_("Abrir carpeta de datos")).triggered.connect(self.open_data_requested)
        self.update_action = m.addAction(_("Descargar versión nueva…"))
        self.update_action.triggered.connect(self.update_requested)
        self.update_action.setVisible(False)
        m.addAction(_("Acerca de…")).triggered.connect(self.about_requested)
        m.addAction(_("Salir")).triggered.connect(self.quit_requested)
        m.aboutToShow.connect(self._update_enabled)

    def _update_enabled(self) -> None:
        _profiles, active_id = self._get_profiles()
        self._regions_menu.setEnabled(active_id is not None)
        self._game_menu.setEnabled(active_id is not None)
        self._delete.setEnabled(active_id is not None)

    def _populate_windows(self) -> None:
        menu = self._windows_menu
        menu.clear()
        target = self._get_target()
        group = QActionGroup(menu)
        windows = self._list_windows()
        if not windows:
            menu.addAction(_("(no hay ventanas)")).setEnabled(False)
        for info in windows:
            action = QAction(info.label, menu, checkable=True)
            action.setChecked(target is not None and target.hwnd == info.hwnd)
            action.triggered.connect(lambda _=False, i=info: self.window_selected.emit(i))
            group.addAction(action)
            menu.addAction(action)

    def _populate_profiles(self) -> None:
        menu = self._profiles_menu
        menu.clear()
        profiles, active_id = self._get_profiles()
        group = QActionGroup(menu)
        if not profiles:
            menu.addAction(_("(ninguno: calibra uno)")).setEnabled(False)
        for profile in profiles:
            action = QAction(profile.name, menu, checkable=True)
            action.setChecked(profile.id == active_id)
            action.triggered.connect(lambda _=False, pid=profile.id: self.profile_selected.emit(pid))
            group.addAction(action)
            menu.addAction(action)

    def _populate_regions(self) -> None:
        menu = self._regions_menu
        menu.clear()
        profiles, active_id = self._get_profiles()
        active = next((p for p in profiles if p.id == active_id), None)
        if active is None:
            return
        menu.addAction(_("Recalibrar rival")).triggered.connect(lambda: self.recalibrate_requested.emit())
        for role, label, current in (
            ("rival2", N_("2.º rival (combates dobles)"), active.rival2_region),
            ("own", N_("tu Pokémon"), active.own_region),
            ("moves", N_("menú de ataques"), active.moves_region),
        ):
            text = _("Recalibrar {label}…", label=_(label)) if current else _("Calibrar {label}…", label=_(label))
            menu.addAction(text).triggered.connect(lambda _=False, r=role: self.region_requested.emit(r))
            if current:
                menu.addAction(_("Quitar {label}", label=_(label))).triggered.connect(
                    lambda _=False, r=role: self.region_remove_requested.emit(r)
                )

    def _populate_games(self) -> None:
        menu = self._game_menu
        menu.clear()
        profiles, active_id = self._get_profiles()
        active = next((p for p in profiles if p.id == active_id), None)
        current = active.game if active else None
        group = QActionGroup(menu)
        for game_id, label in [(None, _("Sin especificar")), *self._get_games()]:
            action = QAction(label, menu, checkable=True)
            action.setChecked(game_id == current)
            action.triggered.connect(lambda _=False, g=game_id: self.profile_game_selected.emit(g))
            group.addAction(action)
            menu.addAction(action)

    def _on_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.menu.popup(self.icon.geometry().center())
