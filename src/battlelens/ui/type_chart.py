"""Tabla de tipos flotante, por generación y con los tipos de la ficha resaltados (spec type-chart)."""

from __future__ import annotations

from collections.abc import Iterable

from PyQt6.QtCore import QPoint, QPointF, QRect, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QGuiApplication, QMouseEvent, QPainter, QPen, QWheelEvent
from PyQt6.QtWidgets import QToolTip, QWidget

from ..i18n import _
from . import theme
from .overlay import MARGIN, _bring_to_top, _exclude_from_capture_and_activation, physical_to_logical

PAD = 12
TITLE_H = 30
ROW_HEAD_W = 84
COL_HEAD_H = 26
CELL = 22
CLOSE = 20
GRIP = 16  # tirador para reescalar, en la esquina inferior derecha
MIN_SCALE, MAX_SCALE = 0.6, 2.0
WHEEL_STEP = 0.1
_DRAG_THRESHOLD = 4
CELL_COLORS = {2.0: theme.GOOD, 0.5: theme.BAD, 0.0: "#3a3d4a"}
CELL_TEXT = {2.0: "#10131a", 0.5: "#ffffff", 0.0: "#e8e8ee"}
RIVAL_TINT = QColor(255, 255, 255, 34)  # columnas: tipos del rival (defiende)
OWN_COLOR = theme.ACCENT  # filas: tipos de tu Pokémon (ataca)


def abbreviation(label: str) -> str:
    return label[:3]


class TypeChartWindow(QWidget):
    """Atacante en filas, defensor en columnas; ×1 vacía. Excluida de la captura, como la ficha.

    Se pinta en coordenadas «base» y se escala entera (tirador o Ctrl+rueda), así que todo crece a la vez.
    """

    changed = pyqtSignal()  # el usuario la ha movido o reescalado (para guardarlo en state.json)

    def __init__(self) -> None:
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
                         | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.types: list[str] = []
        self.labels: dict[str, str] = {}
        self.chart: dict[str, dict[str, float]] = {}
        self.generation = 0
        self.highlight: frozenset[str] = frozenset()  # columnas: tipos de los rivales
        self.highlight_rows: frozenset[str] = frozenset()  # filas: tipos de tu Pokémon
        self.saved_pos: QPoint | None = None
        self.scale = 1.0
        self._base = QRect()
        self._resizing = False
        self._press_scale = 1.0
        self._capture_excluded = False
        self._press_global: QPoint | None = None
        self._press_offset = QPoint()
        self._dragging = False

    # ---- contenido ---------------------------------------------------------

    def set_chart(self, chart: dict[str, dict[str, float]], labels: dict[str, str], generation: int) -> None:
        self.chart, self.labels, self.generation = chart, labels, generation
        self.types = list(chart)
        n = len(self.types)
        self._base = QRect(0, 0, 2 * PAD + ROW_HEAD_W + n * CELL, PAD + TITLE_H + COL_HEAD_H + n * CELL + PAD)
        self.set_scale(self.scale)

    def set_scale(self, scale: float) -> None:
        self.scale = round(min(max(scale, MIN_SCALE), MAX_SCALE), 2)
        self.setFixedSize(round(self._base.width() * self.scale), round(self._base.height() * self.scale))
        self.update()

    def set_highlight(self, defending: Iterable[str], attacking: Iterable[str] = ()) -> None:
        """Columnas de los tipos del rival y filas de los de tu Pokémon; el cruce es tu ataque contra él."""
        self.highlight = frozenset(defending)
        self.highlight_rows = frozenset(attacking)
        self.update()

    def cell(self, attacker: str, defender: str) -> str:
        """Texto de la celda: «×2», «×½», «×0» o vacío para ×1."""
        return theme.MULTIPLIER_LABELS.get(self.chart[attacker][defender], "")

    # ---- ventana -----------------------------------------------------------

    def present(self, target_rect: tuple[int, int, int, int] | None) -> None:
        if self.saved_pos is None:
            self.saved_pos = self._initial_position(target_rect)
        self.move(self._clamp(self.saved_pos))
        self.show()
        if not self._capture_excluded:
            _exclude_from_capture_and_activation(int(self.winId()))
            self._capture_excluded = True
        self.keep_on_top()

    def keep_on_top(self) -> None:
        if self.isVisible():
            _bring_to_top(int(self.winId()))

    def _clamp(self, pos: QPoint) -> QPoint:
        """Dentro de la pantalla (p. ej. si se guardó en un monitor que ya no está)."""
        screen = (QGuiApplication.screenAt(pos) or QGuiApplication.primaryScreen()).availableGeometry()
        x = min(max(pos.x(), screen.left()), max(screen.left(), screen.right() - self.width()))
        y = min(max(pos.y(), screen.top()), max(screen.top(), screen.bottom() - self.height()))
        return QPoint(x, y)

    def _initial_position(self, target_rect: tuple[int, int, int, int] | None) -> QPoint:
        """A la izquierda del emulador si cabe (la ficha va a la derecha); si no, centrada."""
        if target_rect is not None:
            left, top, _w, _h = target_rect
            top_left = physical_to_logical(left, top)
            screen = (QGuiApplication.screenAt(top_left) or QGuiApplication.primaryScreen()).availableGeometry()
            x = top_left.x() - self.width() - MARGIN
            if x >= screen.left():
                return QPoint(x, max(top_left.y(), screen.top()))
        screen = QGuiApplication.primaryScreen().availableGeometry()
        return screen.center() - QPoint(self.width() // 2, self.height() // 2)

    # ---- geometría ---------------------------------------------------------

    def _close_rect(self) -> QRect:
        return QRect(self._base.width() - PAD - CLOSE, PAD + (TITLE_H - CLOSE) // 2 - 2, CLOSE, CLOSE)

    def _grip_rect(self) -> QRect:
        return QRect(self._base.width() - GRIP - 2, self._base.height() - GRIP - 2, GRIP, GRIP)

    def _to_base(self, pos: QPointF) -> QPoint:
        return QPoint(int(pos.x() / self.scale), int(pos.y() / self.scale))

    def _grid_origin(self) -> QPoint:
        return QPoint(PAD + ROW_HEAD_W, PAD + TITLE_H + COL_HEAD_H)

    def _type_at(self, pos: QPoint) -> str | None:
        """Tipo bajo el ratón (en coordenadas base) en las cabeceras, para el nombre completo en el tooltip."""
        origin = self._grid_origin()
        if origin.y() - COL_HEAD_H <= pos.y() < origin.y() and pos.x() >= origin.x():
            index = (pos.x() - origin.x()) // CELL
            return self.types[index] if index < len(self.types) else None
        return None

    # ---- pintado -----------------------------------------------------------

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.scale(self.scale, self.scale)
        p.setPen(QPen(QColor(theme.PANEL_BORDER), 1))
        p.setBrush(QColor(theme.PANEL_SOLID))
        p.drawRoundedRect(QRectF(self._base).adjusted(0.5, 0.5, -0.5, -0.5), 12, 12)

        title = QFont(self.font())
        title.setPixelSize(14)
        title.setWeight(QFont.Weight.Bold)
        p.setFont(title)
        p.setPen(QColor(theme.TEXT))
        p.drawText(QRect(PAD, PAD, self._base.width() - 2 * PAD - CLOSE, TITLE_H - 6),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                   _("Tabla de tipos · Gen {generation}", generation=self.generation))
        p.setPen(QColor(theme.TEXT_MUTED))
        p.drawText(self._close_rect(), Qt.AlignmentFlag.AlignCenter, "✕")
        self._legend(p)

        small = QFont(self.font())
        small.setPixelSize(9)
        small.setWeight(QFont.Weight.DemiBold)
        p.setFont(small)
        origin = self._grid_origin()
        p.drawText(QRect(PAD, origin.y() - COL_HEAD_H, ROW_HEAD_W - 4, COL_HEAD_H),
                   Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, _("Defiende →") + "\n" + _("Ataca ↓"))

        n = len(self.types)
        p.setPen(Qt.PenStyle.NoPen)
        for col, defender in enumerate(self.types):  # columnas resaltadas: los tipos del rival
            if defender in self.highlight:
                x = origin.x() + col * CELL
                p.setBrush(RIVAL_TINT)
                p.drawRoundedRect(QRectF(x, origin.y() - COL_HEAD_H, CELL, COL_HEAD_H + n * CELL + 2), 4, 4)
        for row, attacker in enumerate(self.types):  # filas resaltadas: los tipos de tu Pokémon
            if attacker in self.highlight_rows:
                own = QColor(OWN_COLOR)
                own.setAlpha(40)
                p.setBrush(own)
                p.drawRoundedRect(QRectF(PAD - 4, origin.y() + row * CELL, ROW_HEAD_W - 4 + n * CELL + 6, CELL), 4, 4)

        for col, defender in enumerate(self.types):
            x = origin.x() + col * CELL
            self._pill(p, QRectF(x + 1, origin.y() - COL_HEAD_H + 4, CELL - 2, 16), defender,
                       abbreviation(self.labels.get(defender, defender)),
                       "#ffffff" if defender in self.highlight else None)
        for row, attacker in enumerate(self.types):
            y = origin.y() + row * CELL
            self._pill(p, QRectF(PAD, y + 3, ROW_HEAD_W - 8, CELL - 6), attacker,
                       self.labels.get(attacker, attacker), OWN_COLOR if attacker in self.highlight_rows else None)
            for col, defender in enumerate(self.types):
                rect = QRectF(origin.x() + col * CELL + 1, y + 1, CELL - 2, CELL - 2)
                factor = self.chart[attacker][defender]
                if factor in CELL_COLORS:
                    p.setPen(Qt.PenStyle.NoPen)
                    p.setBrush(QColor(CELL_COLORS[factor]))
                    p.drawRoundedRect(rect, 3, 3)
                    p.setPen(QColor(CELL_TEXT[factor]))
                    p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.cell(attacker, defender))
                else:
                    p.setPen(Qt.PenStyle.NoPen)
                    p.setBrush(QColor(255, 255, 255, 8))
                    p.drawRoundedRect(rect, 3, 3)
                if attacker in self.highlight_rows and defender in self.highlight:  # tu ataque contra el rival
                    p.setPen(QPen(QColor(OWN_COLOR), 2))
                    p.setBrush(Qt.BrushStyle.NoBrush)
                    p.drawRoundedRect(rect.adjusted(-0.5, -0.5, 0.5, 0.5), 3, 3)
        grip = self._grip_rect()  # tres rayas en diagonal, como el tirador de una ventana
        p.setPen(QPen(QColor(theme.TEXT_MUTED), 1.2))
        for offset in (4, 8, 12):
            p.drawLine(grip.right() - offset, grip.bottom(), grip.right(), grip.bottom() - offset)
        p.end()

    def _legend(self, p: QPainter) -> None:
        """«▮ Rival · ▮ Tú» a la derecha del título, solo con algo resaltado."""
        items = []
        if self.highlight:
            items.append((QColor(255, 255, 255, 120), _("Rival")))
        if self.highlight_rows:
            items.append((QColor(OWN_COLOR), _("Tú")))
        if not items:
            return
        font = QFont(self.font())
        font.setPixelSize(10)
        font.setWeight(QFont.Weight.DemiBold)
        p.setFont(font)
        metrics = QFontMetrics(font)
        right = self._close_rect().left() - 10
        y = PAD + (TITLE_H - 6) // 2
        for color, label in reversed(items):
            width = metrics.horizontalAdvance(label)
            p.setPen(QColor(theme.TEXT_MUTED))
            p.drawText(QRect(right - width, y - 8, width, 16), Qt.AlignmentFlag.AlignVCenter, label)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(color)
            p.drawRoundedRect(QRectF(right - width - 14, y - 4, 9, 9), 2, 2)
            right -= width + 26

    @staticmethod
    def _pill(p: QPainter, rect: QRectF, type_id: str, text: str, outline: str | None) -> None:
        p.setPen(QPen(QColor(outline), 1.5) if outline else Qt.PenStyle.NoPen)
        p.setBrush(QColor(theme.TYPE_COLORS.get(type_id, "#555")))
        p.drawRoundedRect(rect, rect.height() / 2, rect.height() / 2)
        p.setPen(QColor("#1b1b1b" if type_id in theme.DARK_TEXT_TYPES else "#ffffff"))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    # ---- ratón: arrastrar para mover, tirador o Ctrl+rueda para reescalar; el ✕ la cierra ----

    def _on_grip(self, pos: QPointF) -> bool:
        return self._grip_rect().adjusted(-4, -4, 4, 4).contains(self._to_base(pos))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_global = event.globalPosition().toPoint()
            self._press_offset = self._press_global - self.frameGeometry().topLeft()
            self._dragging = False
            self._resizing = self._on_grip(event.position())
            self._press_scale = self.scale

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._press_global is None:
            on_grip = self._on_grip(event.position())
            self.setCursor(Qt.CursorShape.SizeFDiagCursor if on_grip else Qt.CursorShape.OpenHandCursor)
            type_id = self._type_at(self._to_base(event.position()))
            if type_id is not None:
                QToolTip.showText(event.globalPosition().toPoint(), self.labels.get(type_id, type_id), self)
            return
        current = event.globalPosition().toPoint()
        if self._resizing:  # manda el ancho: la tabla mantiene su proporción
            self.set_scale(self._press_scale + (current.x() - self._press_global.x()) / self._base.width())
            return
        if not self._dragging and (current - self._press_global).manhattanLength() > _DRAG_THRESHOLD:
            self._dragging = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        if self._dragging:
            self.move(current - self._press_offset)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._press_global is None:
            return
        if self._resizing:
            if self.scale != self._press_scale:
                self.changed.emit()
        elif self._dragging:
            self.saved_pos = self.pos()
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self.changed.emit()
        elif self._close_rect().contains(self._to_base(event.position())):
            self.hide()
        self._press_global = None
        self._dragging = False
        self._resizing = False

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.angleDelta().y():
            self.set_scale(self.scale + (WHEEL_STEP if event.angleDelta().y() > 0 else -WHEEL_STEP))
            self.changed.emit()
