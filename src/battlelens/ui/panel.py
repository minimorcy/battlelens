"""Modo panel: la ficha y la tabla de tipos en una ventana normal, p. ej. en otra pantalla (spec panel-window)."""

from __future__ import annotations

from PyQt6.QtCore import QEvent, QObject, QRect, Qt, pyqtSignal
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..i18n import _
from . import theme
from .icons import app_icon
from .overlay import Overlay
from .type_chart import MAX_SCALE, MIN_SCALE, TypeChartWindow

GAP = 12


class PanelWindow(QWidget):
    """Ventana con marco en tres columnas: ficha del rival (o «Esperando combate…»), tablas de tipos y naturalezas,
    y el buscador con la ficha buscada debajo (search-own-card D4).

    Reutiliza los mismos `Overlay` y `TypeChartWindow` reparentándolos (design D1); fuera de aquí vuelven a ser
    ventanas flotantes con sus flags de siempre.
    """

    geometry_changed = pyqtSignal()

    def __init__(self, overlay: Overlay, chart: TypeChartWindow, natures: TypeChartWindow | None = None,
                 search_card: Overlay | None = None, search_field: QWidget | None = None) -> None:
        super().__init__(None, Qt.WindowType.Window)
        self.setWindowTitle("BattleLens")
        self.setWindowIcon(app_icon())
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # aparece sin quitar el foco al juego
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet(
            f"PanelWindow {{ background:{theme.PANEL_SOLID}; }}"
            f"QLineEdit {{ background:{theme.SETTINGS_FIELD}; color:{theme.TEXT}; border:1px solid {theme.PANEL_BORDER};"
            f" border-radius:7px; padding:6px 10px; font-size:13px; selection-background-color:{theme.ACCENT}; }}"
            f"QLineEdit:focus {{ border-color:{theme.ACCENT}; }}"
            f"#field-error {{ color:{theme.DANGER}; }}"
        )
        self.setMinimumSize(760, 400)
        self.resize(1440, 760)  # dos fichas y la tabla; manda la geometría guardada
        self.overlay, self.chart, self.natures = overlay, chart, natures
        self.search_card, self.search_field = search_card, search_field
        self.charts = [c for c in (chart, natures) if c is not None]  # apiladas en el hueco central
        self.cards = [c for c in (overlay, search_card) if c is not None]
        self._flags = {w: w.windowFlags() for w in (*self.cards, *self.charts)}

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
        self._search_slot = None
        if search_card is not None:
            # Columna derecha: el buscador arriba y la ficha buscada, colocada a mano como la del rival, debajo
            self._search_column = QWidget(self)
            column = QVBoxLayout(self._search_column)
            column.setContentsMargins(0, 0, 0, 0)
            column.setSpacing(GAP)
            if search_field is not None:
                column.addWidget(search_field)
            self._search_slot = QWidget(self._search_column)
            column.addWidget(self._search_slot, 1)
            self._search_column.setFixedWidth(search_card._base_width)
            row.addWidget(self._search_column)
        self.docked = False

    # ---- dentro / fuera del panel ------------------------------------------

    def dock(self) -> None:
        if self.docked:
            return
        self.docked = True
        self._floating_scale = {c: c.scale for c in self.charts}  # las de las tablas flotantes, para devolvérselas
        self.overlay.hide()  # la app vuelve a dibujar la última ficha si la había
        self.overlay.setParent(self._column, Qt.WindowType.Widget)
        self.overlay.move(0, 0)
        self.overlay.setCursor(Qt.CursorShape.ArrowCursor)
        for chart in self.charts:
            chart.hide()
            chart.setParent(self._chart_slot, Qt.WindowType.Widget)
            chart.setCursor(Qt.CursorShape.ArrowCursor)
        if self.search_card is not None:
            self.search_card.hide()
            self.search_card.setParent(self._search_slot, Qt.WindowType.Widget)
            self.search_card.move(0, 0)
            self.search_card.setCursor(Qt.CursorShape.ArrowCursor)
        for watched in self._watched():
            watched.installEventFilter(self)
        for chart in self.charts:  # chuletas siempre a mano en el panel
            chart.show()
        self._sync_waiting()
        self.show()

    def undock(self) -> None:
        if not self.docked:
            return
        self.docked = False
        self.hide()
        for watched in self._watched():
            watched.removeEventFilter(self)
        for widget in (*self.cards, *self.charts):
            widget.hide()
            widget.setParent(None, self._flags[widget])
            widget.setCursor(Qt.CursorShape.OpenHandCursor)
            widget._capture_excluded = False  # HWND nuevo: hay que volver a excluirlo de la captura
        for chart in self.charts:
            chart.set_scale(self._floating_scale[chart])

    def _watched(self) -> list[QWidget]:
        extra = [self.search_card, self._search_slot] if self.search_card is not None else []
        return [self.overlay, self._column, self._chart_slot, *self.charts, *extra]

    def focus_search(self) -> None:
        """Atajo «Buscar Pokémon» en modo panel: el panel delante y el foco en su buscador (search-own-card D5)."""
        self.showNormal() if self.isMinimized() else self.show()
        self.raise_()
        self.activateWindow()
        if self.search_field is not None:
            self.search_field.edit.setFocus()

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
        """Las tablas visibles ocupan el hueco libre a la derecha de la ficha (design D6): apiladas o una al lado
        de la otra, lo que las deje más grandes con la forma actual de la ventana."""
        shown = [c for c in self.charts if c.isVisibleTo(self) and not c._base.isEmpty()]
        if not shown:
            return
        slot = self._chart_slot.size()
        gaps = (GAP + 1) * (len(shown) - 1) + 1  # el hueco entre tablas no escala; +1 px por redondeo
        widths, heights = [c._base.width() for c in shown], [c._base.height() for c in shown]
        stacked = min(slot.width() / max(widths), (slot.height() - gaps) / sum(heights))
        side = min((slot.width() - gaps) / sum(widths), slot.height() / max(heights))
        self.side_by_side = side > stacked
        scale = min(max(max(stacked, side), MIN_SCALE), MAX_SCALE)
        offset = 0
        for chart in shown:
            chart.set_scale(scale)
            chart.move(offset, 0) if self.side_by_side else chart.move(0, offset)
            offset += (chart.width() if self.side_by_side else chart.height()) + GAP

    # ---- eventos -------------------------------------------------------------

    def _sync_waiting(self) -> None:
        self._waiting.setVisible(not self.overlay.isVisibleTo(self))
        # el hueco de la ficha mide lo que ella; vacío, el ancho de una ficha
        self._column.setFixedWidth(self.overlay.width() if self.overlay.isVisibleTo(self) else self.overlay._base_width)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if obj is self.overlay and event.type() in (QEvent.Type.Show, QEvent.Type.Hide, QEvent.Type.Resize):
            self._sync_waiting()
        elif obj is self.search_card and event.type() == QEvent.Type.Resize:
            self._search_column.setFixedWidth(max(self.search_card.width(), self.search_card._base_width))
        elif obj is self._search_slot and event.type() == QEvent.Type.Resize:
            if self.search_card.isVisibleTo(self):
                self.search_card._relayout()  # alto disponible nuevo: con o sin desplazamiento
        elif obj is self._column and event.type() == QEvent.Type.Resize:
            self._waiting.setGeometry(self._column.rect())
            if self.overlay.isVisibleTo(self):
                self.overlay._relayout()  # alto disponible nuevo: con o sin desplazamiento
        elif obj is self._chart_slot and event.type() == QEvent.Type.Resize:
            self.fit_chart()
        elif obj in self.charts and event.type() in (QEvent.Type.Show, QEvent.Type.Hide):
            self.fit_chart()
        return False

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.geometry_changed.emit()

    def moveEvent(self, event) -> None:
        super().moveEvent(event)
        self.geometry_changed.emit()
