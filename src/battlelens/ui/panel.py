"""Modo panel: la ficha y la tabla de tipos en una ventana normal, p. ej. en otra pantalla (spec panel-window)."""

from __future__ import annotations

from PyQt6.QtCore import QEvent, QObject, QRect, Qt, pyqtSignal
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ..i18n import _
from . import theme
from .icons import app_icon
from .overlay import Overlay
from .type_chart import MAX_SCALE, MIN_SCALE, TypeChartWindow

GAP = 12


class PanelWindow(QWidget):
    """Ventana con marco: ficha a la izquierda (o «Esperando combate…») y tabla de tipos a la derecha.

    Reutiliza los mismos `Overlay` y `TypeChartWindow` reparentándolos (design D1); fuera de aquí vuelven a ser
    ventanas flotantes con sus flags de siempre.
    """

    geometry_changed = pyqtSignal()

    def __init__(self, overlay: Overlay, chart: TypeChartWindow) -> None:
        super().__init__(None, Qt.WindowType.Window)
        self.setWindowTitle("BattleLens")
        self.setWindowIcon(app_icon())
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # aparece sin quitar el foco al juego
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet(f"PanelWindow {{ background:{theme.PANEL_SOLID}; }}")
        self.setMinimumSize(480, 360)
        self.resize(1100, 720)
        self.overlay, self.chart = overlay, chart
        self._flags = {overlay: overlay.windowFlags(), chart: chart.windowFlags()}

        # Ficha y tabla se colocan a mano dentro de sus huecos, sin layout: con su tamaño fijo, un layout no
        # dejaría encoger la ventana por debajo de ellas y no se volverían a ajustar.
        self._column = QWidget(self)
        self._waiting = QLabel(_("Esperando combate…"), self._column)
        self._waiting.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._waiting.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:14px;")
        self._chart_slot = QWidget(self)
        row = QHBoxLayout(self)
        row.setContentsMargins(GAP, GAP, GAP, GAP)
        row.setSpacing(GAP)
        row.addWidget(self._column)
        row.addWidget(self._chart_slot, 1)
        self.docked = False

    # ---- dentro / fuera del panel ------------------------------------------

    def dock(self) -> None:
        if self.docked:
            return
        self.docked = True
        self._floating_scale = self.chart.scale  # la de la tabla flotante, para devolvérsela al salir
        self.overlay.hide()  # la app vuelve a dibujar la última ficha si la había
        self.chart.hide()
        self.overlay.setParent(self._column, Qt.WindowType.Widget)
        self.overlay.move(0, 0)
        self.chart.setParent(self._chart_slot, Qt.WindowType.Widget)
        self.chart.move(0, 0)
        for widget in (self.overlay, self.chart):
            widget.setCursor(Qt.CursorShape.ArrowCursor)
        for watched in (self.overlay, self._column, self._chart_slot):
            watched.installEventFilter(self)
        self.chart.show()
        self._sync_waiting()
        self.show()

    def undock(self) -> None:
        if not self.docked:
            return
        self.docked = False
        self.hide()
        for watched in (self.overlay, self._column, self._chart_slot):
            watched.removeEventFilter(self)
        for widget in (self.overlay, self.chart):
            widget.hide()
            widget.setParent(None, self._flags[widget])
            widget.setCursor(Qt.CursorShape.OpenHandCursor)
            widget._capture_excluded = False  # HWND nuevo: hay que volver a excluirlo de la captura
        self.chart.set_scale(self._floating_scale)

    # ---- geometría ----------------------------------------------------------

    def restore_geometry(self, geometry) -> None:
        """[x, y, ancho, alto] de state.json (puede venir tocado a mano); se ignora si no cae en ninguna pantalla."""
        if not (isinstance(geometry, list) and len(geometry) == 4 and all(type(v) is int for v in geometry)):
            return
        rect = QRect(*geometry)
        if QGuiApplication.screenAt(rect.center()) is not None:
            self.setGeometry(rect)

    def saved_geometry(self) -> list[int]:
        rect = self.normalGeometry() if self.isMaximized() else self.geometry()
        return [rect.x(), rect.y(), rect.width(), rect.height()]

    def fit_chart(self) -> None:
        """La tabla ocupa el hueco libre a la derecha de la ficha (design D6)."""
        base = self.chart._base
        if base.isEmpty():
            return
        slot = self._chart_slot.size()
        scale = min(slot.width() / base.width(), slot.height() / base.height())
        self.chart.set_scale(min(max(scale, MIN_SCALE), MAX_SCALE))

    # ---- eventos -------------------------------------------------------------

    def _sync_waiting(self) -> None:
        self._waiting.setVisible(not self.overlay.isVisibleTo(self))
        # el hueco de la ficha mide lo que ella; vacío, el ancho de una ficha
        self._column.setFixedWidth(self.overlay.width() if self.overlay.isVisibleTo(self) else self.overlay._base_width)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if obj is self.overlay and event.type() in (QEvent.Type.Show, QEvent.Type.Hide, QEvent.Type.Resize):
            self._sync_waiting()
        elif obj is self._column and event.type() == QEvent.Type.Resize:
            self._waiting.setGeometry(self._column.rect())
            if self.overlay.isVisibleTo(self):
                self.overlay._relayout()  # alto disponible nuevo: con o sin desplazamiento
        elif obj is self._chart_slot and event.type() == QEvent.Type.Resize:
            self.fit_chart()
        return False

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.geometry_changed.emit()

    def moveEvent(self, event) -> None:
        super().moveEvent(event)
        self.geometry_changed.emit()
