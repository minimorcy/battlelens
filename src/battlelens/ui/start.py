"""Pantalla de inicio (add-start-screen): ventana del emulador, perfil y modo de la ficha antes de jugar."""

from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QComboBox, QDialog, QHBoxLayout, QVBoxLayout, QWidget

from ..core.config import MODES
from ..core.profiles import Profile
from ..i18n import _
from ..platform.windows import WindowInfo
from .icons import app_icon, arrow_images
from .settings import MODE_LABELS, Toggle, _button, _Card, _label, fill_window_combo
from .theme import TEXT_MUTED, settings_qss


class StartDialog(QDialog):
    """Al aceptar («Empezar»), lo elegido queda en `profile_id`, `mode`, `auto_detect` y `show_at_start`.

    La ventana se aplica al momento (`window_selected`), como en Ajustes: el perfil puede activarse solo
    por el juego del título y el asistente de presets necesita capturarla.
    """

    window_selected = pyqtSignal(object)
    preset_requested = pyqtSignal()

    def __init__(
        self,
        list_windows: Callable[[], list[WindowInfo]],
        get_target: Callable[[], WindowInfo | None],
        get_profiles: Callable[[], tuple[list[Profile], str | None]],
        mode: str,
        auto_detect: bool,
        show_at_start: bool,
    ) -> None:
        super().__init__(None, Qt.WindowType.WindowStaysOnTopHint)
        self.setObjectName("settings-window")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        arrows = arrow_images(TEXT_MUTED)
        self.setStyleSheet(settings_qss(arrows["down"], arrows["up"]))
        self.setWindowTitle("BattleLens")
        self.setWindowIcon(app_icon())
        self.setMinimumWidth(560)
        self._list_windows = list_windows
        self._get_target = get_target
        self._get_profiles = get_profiles

        self.window_combo = QComboBox()
        self.window_combo.setMinimumWidth(240)
        self.window_combo.activated.connect(self._on_window_activated)
        refresh = _button("↻")
        refresh.setToolTip(_("Actualizar la lista de ventanas"))
        refresh.clicked.connect(self._populate_windows)
        window_row = QWidget()
        row = QHBoxLayout(window_row)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(self.window_combo)
        row.addWidget(refresh)

        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(240)
        preset = _button(_("Nuevo perfil con un preset…"))
        preset.clicked.connect(self.preset_requested)

        self.mode_combo = QComboBox()
        for code in MODES:
            self.mode_combo.addItem(_(MODE_LABELS[code]), code)
        self.mode_combo.setCurrentIndex(max(self.mode_combo.findData(mode), 0))
        self.auto_toggle = Toggle(_("Detección automática"))
        self.auto_toggle.setChecked(auto_detect)

        card = _Card()
        card.add_row(_("Ventana del emulador"), window_row, _("La ventana en la que se ve el juego."))
        card.add_row(_("Perfil"), self.profile_combo, _("Dónde están los nombres en la pantalla de tu juego."),
                     below=preset)
        card.add_row(_("Modo de la ficha"), self.mode_combo)
        card.add_row(_("Detección automática"), self.auto_toggle, _("La ficha aparece sola en cada combate."))

        self.show_toggle = Toggle(_("Mostrar al abrir la app"))
        self.show_toggle.setChecked(show_at_start)
        start = _button(_("Empezar"), "primary")
        start.setDefault(True)
        start.clicked.connect(self.accept)
        footer = QHBoxLayout()
        footer.addWidget(self.show_toggle)
        footer.addWidget(_label(_("Mostrar al abrir la app"), "row-hint"), 1)
        footer.addWidget(start)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)
        layout.addWidget(_label(_("Antes de jugar"), "page-title"))
        layout.addWidget(_label(_("Elige el emulador y el perfil de tu juego. Puedes cambiarlo luego desde la "
                                  "bandeja o en Ajustes."), "page-subtitle", wrap=True))
        layout.addWidget(card)
        layout.addLayout(footer)

        self._populate_windows()
        self.refresh_profiles()

    def _populate_windows(self) -> None:
        fill_window_combo(self.window_combo, self._list_windows(), self._get_target())

    def _on_window_activated(self, index: int) -> None:
        info = self.window_combo.itemData(index)
        if info is not None:
            self.window_selected.emit(info)
            self.refresh_profiles()  # el juego del título puede haber activado otro perfil

    def refresh_profiles(self) -> None:
        profiles, active_id = self._get_profiles()
        self.profile_combo.clear()
        if not profiles:
            self.profile_combo.addItem(_("(sin perfiles: crea uno con un preset)"), None)
        for profile in profiles:
            self.profile_combo.addItem(profile.name, profile.id)
        self.profile_combo.setCurrentIndex(max(self.profile_combo.findData(active_id), 0))

    @property
    def profile_id(self) -> str | None:
        return self.profile_combo.currentData()

    @property
    def mode(self) -> str:
        return self.mode_combo.currentData()

    @property
    def auto_detect(self) -> bool:
        return self.auto_toggle.isChecked()

    @property
    def show_at_start(self) -> bool:
        return self.show_toggle.isChecked()
