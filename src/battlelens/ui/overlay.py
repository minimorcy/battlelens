"""Ventana superpuesta con la ficha del Pokémon rival."""

from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes

from PyQt6.QtCore import QPoint, QRect, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QGuiApplication, QMouseEvent
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from ..core.pokedex import STAT_ORDER, Pokedex, Species, SpeciesView
from . import theme

WIDTH = 320
MARGIN = 8
_DRAG_THRESHOLD = 4
_WDA_EXCLUDEFROMCAPTURE = 0x11
_GWL_EXSTYLE = -20
_WS_EX_NOACTIVATE = 0x08000000


def _exclude_from_capture_and_activation(hwnd: int) -> None:
    if sys.platform != "win32":
        return
    user32 = ctypes.windll.user32
    user32.SetWindowDisplayAffinity(wintypes.HWND(hwnd), _WDA_EXCLUDEFROMCAPTURE)
    user32.GetWindowLongW.restype = ctypes.c_long
    style = user32.GetWindowLongW(wintypes.HWND(hwnd), _GWL_EXSTYLE)
    user32.SetWindowLongW(wintypes.HWND(hwnd), _GWL_EXSTYLE, style | _WS_EX_NOACTIVATE)


def physical_to_logical(x: int, y: int) -> QPoint:
    """Convierte un punto en píxeles físicos (Win32) a coordenadas lógicas de Qt."""
    for screen in QGuiApplication.screens():
        geo = screen.geometry()
        dpr = screen.devicePixelRatio()
        native = QRect(geo.topLeft(), geo.size() * dpr)
        if native.contains(x, y):
            return QPoint(geo.x() + round((x - geo.x()) / dpr), geo.y() + round((y - geo.y()) / dpr))
    return QPoint(x, y)


def _pill(text: str, type_id: str | None = None, bg: str | None = None) -> QLabel:
    label = QLabel(text)
    color = bg or theme.TYPE_COLORS.get(type_id or "", "#555")
    fg = "#1b1b1b" if type_id in theme.DARK_TEXT_TYPES else "#ffffff"
    label.setStyleSheet(
        f"background:{color}; color:{fg}; border-radius:8px; padding:2px 8px; font-weight:600; font-size:11px;"
    )
    return label


def _section_title(text: str) -> QLabel:
    label = QLabel(text.upper())
    label.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:10px; font-weight:700; letter-spacing:1px;")
    return label


class _FlowRow(QWidget):
    """Fila de pastillas que salta de línea cuando no caben."""

    def __init__(self, widgets: list[QWidget], per_row: int = 4) -> None:
        super().__init__()
        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(4)
        for i, w in enumerate(widgets):
            grid.addWidget(w, i // per_row, i % per_row)
        grid.setColumnStretch(per_row, 1)


class Overlay(QWidget):
    moved = pyqtSignal(int, int)
    dismissed = pyqtSignal()  # el usuario la ha cerrado con un clic

    def __init__(self, pokedex: Pokedex, language: str = "es", auto_hide_seconds: float = 0) -> None:
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus,
        )
        self.pokedex = pokedex
        self.language = language
        self.saved_pos: QPoint | None = None
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(WIDTH)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

        self._panel = QFrame(self)
        self._panel.setObjectName("panel")
        self._panel.setStyleSheet(
            f"#panel {{ background:{theme.PANEL_BG}; border:1px solid {theme.PANEL_BORDER}; border-radius:12px; }}"
            f"QLabel {{ color:{theme.TEXT}; background:transparent; }}"
        )
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._panel)
        self._content = QVBoxLayout(self._panel)
        self._content.setContentsMargins(14, 12, 14, 12)
        self._content.setSpacing(6)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)
        self.auto_hide_seconds = auto_hide_seconds

        self._press_global: QPoint | None = None
        self._press_offset = QPoint()
        self._dragging = False
        self._capture_excluded = False

    # ---- contenido ---------------------------------------------------------

    def show_species(
        self, species: Species, target_rect: tuple[int, int, int, int] | None, game: str | None = None
    ) -> None:
        self.show_view(self.pokedex.view(species.id, game, self.language), target_rect)

    def show_view(self, view: SpeciesView, target_rect: tuple[int, int, int, int] | None) -> None:
        self._clear()
        self._content.addWidget(self._card(view))
        self._present(target_rect)

    def _types_row(self, types) -> QWidget:
        return _FlowRow([_pill(self.pokedex.type_name(t, self.language), t) for t in types])

    def _card(self, view: SpeciesView) -> QWidget:
        """Ficha de una especie (un widget, para poder mostrar varias en el futuro)."""
        card = QWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        add = layout.addWidget

        header = QHBoxLayout()
        name = QLabel(view.name)
        name.setObjectName("species-name")
        name.setWordWrap(True)
        name.setStyleSheet("font-size:20px; font-weight:700;")
        number = QLabel(f"#{view.species_id:04d}")
        number.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:13px;")
        header.addWidget(name, 1)
        header.addWidget(number, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header)
        add(self._types_row(view.types))

        groups = view.matchups
        sections = (
            ("Debilidades", (4.0, 2.0)),
            ("Resistencias", (0.5, 0.25)),
            ("Inmunidades", (0.0,)),
        )
        for title, multipliers in sections:
            if not any(groups[m] for m in multipliers):
                continue
            add(_section_title(title))
            for m in multipliers:
                if not groups[m]:
                    continue
                row = QHBoxLayout()
                mult = QLabel(theme.MULTIPLIER_LABELS[m])
                mult.setFixedWidth(26)
                mult.setStyleSheet(f"color:{theme.ACCENT}; font-weight:700;")
                row.addWidget(mult, alignment=Qt.AlignmentFlag.AlignTop)
                row.addWidget(self._types_row(groups[m]), 1)
                layout.addLayout(row)

        add(_section_title("Estadísticas base"))
        stats = QGridLayout()
        stats.setVerticalSpacing(2)
        for i, key in enumerate(STAT_ORDER):
            value = view.stats[key]
            label = QLabel(theme.STAT_LABELS[key])
            label.setStyleSheet(f"color:{theme.TEXT_MUTED};")
            val = QLabel(str(value))
            val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            val.setStyleSheet("font-weight:600;")
            bar = QProgressBar()
            bar.setRange(0, 255)
            bar.setValue(value)
            bar.setTextVisible(False)
            bar.setFixedHeight(8)
            bar.setStyleSheet(
                "QProgressBar { background:#2c3040; border:none; border-radius:4px; }"
                f"QProgressBar::chunk {{ background:{theme.stat_color(value)}; border-radius:4px; }}"
            )
            stats.addWidget(label, i, 0)
            stats.addWidget(val, i, 1)
            stats.addWidget(bar, i, 2)
        total_label = QLabel("Total")
        total_label.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-weight:700;")
        total = QLabel(str(view.stat_total))
        total.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        total.setStyleSheet("font-weight:700;")
        stats.addWidget(total_label, len(STAT_ORDER), 0)
        stats.addWidget(total, len(STAT_ORDER), 1)
        stats.setColumnMinimumWidth(1, 30)
        stats.setColumnStretch(2, 1)
        layout.addLayout(stats)

        if view.abilities:
            add(_section_title("Habilidades"))
            for ability in view.abilities:
                hidden = f"  <i style='color:{theme.TEXT_MUTED}'>(oculta)</i>" if ability.hidden else ""
                label = QLabel(ability.name(self.language) + hidden)
                label.setTextFormat(Qt.TextFormat.RichText)
                add(label)

        if view.other_forms:
            add(_section_title("Otras formas"))
            for other in view.other_forms:
                row = QHBoxLayout()
                label = QLabel(other.name)
                label.setStyleSheet(f"color:{theme.TEXT_MUTED};")
                row.addWidget(label)
                row.addWidget(self._types_row(other.types), 1)
                layout.addLayout(row)
        return card

    def show_unrecognized(self, raw_text: str, target_rect: tuple[int, int, int, int] | None) -> None:
        self._clear()
        title = QLabel("No reconocido")
        title.setStyleSheet("font-size:16px; font-weight:700;")
        self._content.addWidget(title)
        read = raw_text.strip() or "(vacío)"
        detail = QLabel(
            f"Texto leído: <b>{_escape(read)}</b><br>"
            f"<span style='color:{theme.TEXT_MUTED}'>Si el texto no es el nombre del rival, "
            "recalibra la región del perfil desde la bandeja del sistema.</span>"
        )
        detail.setTextFormat(Qt.TextFormat.RichText)
        detail.setWordWrap(True)
        self._content.addWidget(detail)
        self._present(target_rect)

    def _clear(self) -> None:
        def clear_layout(layout):
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                    widget.deleteLater()
                elif item.layout():
                    clear_layout(item.layout())

        clear_layout(self._content)

    # ---- posición y visibilidad -------------------------------------------

    def _present(self, target_rect: tuple[int, int, int, int] | None) -> None:
        self.adjustSize()
        self.move(self._position(target_rect))
        self.show()
        if not self._capture_excluded:
            _exclude_from_capture_and_activation(int(self.winId()))
            self._capture_excluded = True
        self.raise_()
        if self.auto_hide_seconds > 0:
            self._hide_timer.start(int(self.auto_hide_seconds * 1000))

    def _position(self, target_rect: tuple[int, int, int, int] | None) -> QPoint:
        size = self.size()
        if self.saved_pos is not None:
            return self._clamp(self.saved_pos, size)
        if target_rect is None:
            screen = QGuiApplication.primaryScreen().availableGeometry()
            return QPoint(screen.right() - size.width() - MARGIN, screen.top() + MARGIN)

        left, top, width, height = target_rect
        top_left = physical_to_logical(left, top)
        bottom_right = physical_to_logical(left + width, top + height)
        screen = (QGuiApplication.screenAt(top_left) or QGuiApplication.primaryScreen()).availableGeometry()
        x = bottom_right.x() + MARGIN
        if x + size.width() > screen.right():
            # No cabe a la derecha: esquina superior derecha de la pantalla.
            return QPoint(screen.right() - size.width() - MARGIN, screen.top() + MARGIN)
        return self._clamp(QPoint(x, max(top_left.y(), screen.top())), size)

    def _clamp(self, pos: QPoint, size) -> QPoint:
        screen = (QGuiApplication.screenAt(pos) or QGuiApplication.primaryScreen()).availableGeometry()
        x = min(max(pos.x(), screen.left()), screen.right() - size.width())
        y = min(max(pos.y(), screen.top()), screen.bottom() - size.height())
        return QPoint(x, y)

    # ---- ratón: arrastrar para mover, clic para ocultar ---------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_global = event.globalPosition().toPoint()
            self._press_offset = self._press_global - self.frameGeometry().topLeft()
            self._dragging = False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._press_global is None:
            return
        current = event.globalPosition().toPoint()
        if not self._dragging and (current - self._press_global).manhattanLength() > _DRAG_THRESHOLD:
            self._dragging = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        if self._dragging:
            self.move(current - self._press_offset)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._press_global is None:
            return
        if self._dragging:
            self.saved_pos = self.pos()
            self.moved.emit(self.x(), self.y())
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.hide()
            self.dismissed.emit()
        self._press_global = None
        self._dragging = False


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
