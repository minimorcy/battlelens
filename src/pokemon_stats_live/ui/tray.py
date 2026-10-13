"""Icono y menú en la bandeja del sistema."""

from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import QObject, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QActionGroup, QColor, QIcon, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon

from ..core.profiles import Profile
from ..platform.windows import WindowInfo


def pokeball_icon(size: int = 64) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    r = QRectF(2, 2, size - 4, size - 4)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#ffffff"))
    p.drawEllipse(r)
    p.setBrush(QColor("#e3350d"))
    p.drawPie(r, 0, 180 * 16)
    pen = QPen(QColor("#1b1b1b"), size / 16)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(r)
    p.drawLine(int(r.left()), size // 2, int(r.right()), size // 2)
    p.setBrush(QColor("#ffffff"))
    p.drawEllipse(QRectF(size * 0.38, size * 0.38, size * 0.24, size * 0.24))
    p.end()
    return QIcon(pix)


class Tray(QObject):
    recognize_requested = pyqtSignal()
    window_selected = pyqtSignal(object)  # WindowInfo
    profile_selected = pyqtSignal(str)
    calibrate_requested = pyqtSignal()
    recalibrate_requested = pyqtSignal()
    delete_profile_requested = pyqtSignal()
    open_data_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(
        self,
        list_windows: Callable[[], list[WindowInfo]],
        get_target: Callable[[], WindowInfo | None],
        get_profiles: Callable[[], tuple[list[Profile], str | None]],
        hotkey_texts: dict[str, str],
    ) -> None:
        super().__init__()
        self._list_windows = list_windows
        self._get_target = get_target
        self._get_profiles = get_profiles
        self._hotkeys = hotkey_texts

        self.icon = QSystemTrayIcon(pokeball_icon())
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
        self.icon.showMessage("Pokémon Stats Live", message, kind, 4000)

    def refresh_tooltip(self) -> None:
        target = self._get_target()
        profiles, active_id = self._get_profiles()
        active = next((p for p in profiles if p.id == active_id), None)
        lines = ["Pokémon Stats Live"]
        lines.append(f"Ventana: {target.exe if target else '— selecciona una —'}")
        lines.append(f"Perfil: {active.name if active else '— calibra uno —'}")
        self.icon.setToolTip("\n".join(lines))

    def _hint(self, name: str) -> str:
        text = self._hotkeys.get(name)
        return f"\t{text}" if text else ""

    def _build_menu(self) -> None:
        m = self.menu
        recognize = m.addAction("Reconocer ahora" + self._hint("recognize"))
        recognize.triggered.connect(self.recognize_requested)
        m.addSeparator()

        self._windows_menu = m.addMenu("Ventana del emulador")
        self._windows_menu.aboutToShow.connect(self._populate_windows)
        self._profiles_menu = m.addMenu("Perfil activo")
        self._profiles_menu.aboutToShow.connect(self._populate_profiles)

        m.addAction("Calibrar nuevo perfil…" + self._hint("calibrate")).triggered.connect(self.calibrate_requested)
        self._recalibrate = m.addAction("Recalibrar perfil activo")
        self._recalibrate.triggered.connect(self.recalibrate_requested)
        self._delete = m.addAction("Eliminar perfil activo…")
        self._delete.triggered.connect(self.delete_profile_requested)
        m.addSeparator()
        m.addAction("Abrir carpeta de datos").triggered.connect(self.open_data_requested)
        m.addAction("Salir").triggered.connect(self.quit_requested)
        m.aboutToShow.connect(self._update_enabled)

    def _update_enabled(self) -> None:
        _, active_id = self._get_profiles()
        self._recalibrate.setEnabled(active_id is not None)
        self._delete.setEnabled(active_id is not None)

    def _populate_windows(self) -> None:
        menu = self._windows_menu
        menu.clear()
        target = self._get_target()
        group = QActionGroup(menu)
        windows = self._list_windows()
        if not windows:
            menu.addAction("(no hay ventanas)").setEnabled(False)
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
            menu.addAction("(ninguno: calibra uno)").setEnabled(False)
        for profile in profiles:
            action = QAction(profile.name, menu, checkable=True)
            action.setChecked(profile.id == active_id)
            action.triggered.connect(lambda _=False, pid=profile.id: self.profile_selected.emit(pid))
            group.addAction(action)
            menu.addAction(action)

    def _on_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.menu.popup(self.icon.geometry().center())
