"""Ventana superpuesta con la ficha del Pokémon rival."""

from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes

from PyQt6.QtCore import QCoreApplication, QEvent, QPoint, QRect, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QGuiApplication, QMouseEvent
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..core.abilities import ability_effects, multiplier_text
from ..core.card_text import ability_effect_lines, matchup_note
from ..core.competitive import (
    compare_speed,
    stat_profile,
    view_ranges,
    weight_move_power,
)
from ..core.learnsets import Learnsets, LearnsetsMissingError, Move
from ..core.pokedex import Pokedex, Species, SpeciesView
from ..core.matchup import Matchup, Verdict, effective_multiplier, matchup
from ..i18n import N_, _, get_language
from . import theme

WIDTH = 320  # ancho histórico; cada modo define el suyo en card_width()
MODE_WIDTHS = {"normal": 300, "competitive": 360}
CARD_SPACING = 14
PANEL_PADDING = 14  # margen interior izquierdo/derecho del panel
SCROLLBAR_WIDTH = 8  # barra de desplazamiento cuando la ficha no cabe en la pantalla
# Categoría abreviada de los movimientos (improve-card-visuals D8)
CATEGORY_LABELS = {"physical": N_("Fís."), "special": N_("Esp."), "status": N_("Est.")}
CAPTURE_COLORS = theme.CAPTURE_COLORS
MOVE_TYPE_WIDTH = 78  # ancho fijo de la pastilla de tipo en las listas de movimientos
# Claves de los bloques plegables (improve-card-visuals D11)
BLOCK_KEYS = ("matchup", "own_moves", "eff", "stats", "abilities", "moves", "training", "evo", "forms")


def card_width(mode: str) -> int:
    return MODE_WIDTHS.get(mode, MODE_WIDTHS["normal"])
VERDICT_KEYS = {Verdict.ADVANTAGE: "advantage", Verdict.NEUTRAL: "neutral", Verdict.DISADVANTAGE: "disadvantage"}
VERDICT_COLORS = {verdict: theme.VERDICT_COLORS[key] for verdict, key in VERDICT_KEYS.items()}
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


def _pill(text: str, type_id: str | None = None, bg: str | None = None, solid: bool = False) -> QLabel:
    """Pastilla de tipo: sólida (tipos del propio Pokémon, veredicto) o suave (el resto, D2)."""
    label = QLabel(text)
    if solid or bg:
        color = bg or theme.TYPE_COLORS.get(type_id or "", "#555")
        fg = "#1b1b1b" if type_id in theme.DARK_TEXT_TYPES else "#ffffff"
        label.setProperty("pill", "solid")
        label.setStyleSheet(
            f"background:{color}; color:{fg}; border-radius:8px; padding:2px 9px; font-weight:600; font-size:11px;"
        )
    else:
        fill, border = theme.soft_type_colors(type_id)
        label.setProperty("pill", "soft")
        label.setStyleSheet(
            f"background:{fill}; color:{theme.TEXT}; border:1px solid {border}; border-radius:7px;"
            " padding:1px 7px; font-weight:600; font-size:11px;"
        )
    return label


def _outline(text: str) -> QLabel:
    """Insignia neutra con contorno (efectos de habilidad, D8)."""
    label = QLabel(text)
    label.setStyleSheet(
        f"color:{theme.TEXT_MUTED}; background:{theme.SURFACE}; border:1px solid {theme.SURFACE_BORDER};"
        " border-radius:7px; padding:1px 7px; font-weight:600; font-size:11px;"
    )
    return label


def _mult(text: str, tone: str, name: str | None = None) -> QLabel:
    """Multiplicador con color semántico para el jugador: good, bad o neutral (D4)."""
    color = theme.tone_color(tone)
    label = QLabel(text)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setMinimumWidth(26)
    label.setProperty("tone", tone)
    label.setStyleSheet(
        f"color:{color}; background:{theme.rgba(color, 0.15)}; border-radius:5px; padding:1px 4px;"
        " font-weight:700; font-size:11px;"
    )
    if name:
        label.setObjectName(name)
    return label


def _tone(factor: float, for_player: bool = True) -> str:
    """Tono de un multiplicador: `for_player` si el ataque es tuyo; si no, es del rival contra ti."""
    if factor == 1:
        return "neutral"
    return "good" if (factor > 1) == for_player else "bad"


def _sub_title(text: str) -> QLabel:
    label = QLabel(text.upper())
    label.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:10px; font-weight:600; letter-spacing:0.6px;")
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


class _Typed(QWidget):
    """Pastilla suave de un tipo con su multiplicador como insignia aparte (D4)."""

    def __init__(self, type_label: str, type_id: str | None, mult: str, tone: str) -> None:
        super().__init__()
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(3)
        row.addWidget(_pill(type_label, type_id))
        row.addWidget(_mult(mult, tone, "matchup-mult"))


class _Block(QFrame):
    """Bloque con fondo sutil y título que lo pliega o despliega (D3, D11)."""

    def __init__(self, key: str, title: str, extra: QWidget | None = None, accent: str | None = None) -> None:
        super().__init__()
        self.key = key
        self.setObjectName("block")
        border = f"border-left:3px solid {accent};" if accent else ""
        self.setStyleSheet(
            f"#block {{ background:{theme.SURFACE}; border:1px solid {theme.SURFACE_BORDER}; border-radius:8px; {border} }}"
        )
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        self._margins = (8 if accent else 10, 7, 10, 8)
        layout.setContentsMargins(*self._margins)
        self.header = QWidget()
        self.header.setObjectName("block-header")
        self.header.setProperty("block_key", key)
        self.header.setCursor(Qt.CursorShape.PointingHandCursor)
        head = QHBoxLayout(self.header)
        head.setContentsMargins(0, 0, 0, 0)
        head.setSpacing(6)
        self.arrow = QLabel()
        self.arrow.setObjectName("block-arrow")
        self.arrow.setFixedWidth(9)
        self.arrow.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:9px;")
        head.addWidget(self.arrow)
        self.title = QLabel(title.upper())
        self.title.setObjectName("block-title")
        self.title.setWordWrap(True)
        self.title.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:10px; font-weight:700; letter-spacing:0.8px;")
        head.addWidget(self.title, 1)
        if extra is not None:
            head.addWidget(extra, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.header)
        self.body = QWidget()
        self.content = QVBoxLayout(self.body)
        self.content.setContentsMargins(0, 0, 0, 0)
        self.content.setSpacing(4)
        layout.addWidget(self.body)
        self.collapsed = False
        self.set_collapsed(False)

    def add(self, item) -> None:
        if isinstance(item, QWidget):
            self.content.addWidget(item)
        else:
            self.content.addLayout(item)

    def set_collapsed(self, collapsed: bool) -> None:
        self.collapsed = collapsed
        self.body.setHidden(collapsed)
        self.arrow.setText("▸" if collapsed else "▾")
        left, top, right, bottom = self._margins
        self.layout().setContentsMargins(left, 5 if collapsed else top, right, 5 if collapsed else bottom)


class Overlay(QWidget):
    moved = pyqtSignal(int, int)
    dismissed = pyqtSignal()  # el usuario la ha cerrado con el botón ✕
    collapsed_changed = pyqtSignal()  # se ha plegado o desplegado un bloque (guardar en state.json)

    def __init__(
        self, pokedex: Pokedex, language: str = "es", auto_hide_seconds: float = 0, mode: str = "normal"
    ) -> None:
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus,
        )
        self.pokedex = pokedex
        self.language = language
        self.mode = mode
        self.form_hotkey = ""  # atajo «Cambiar de forma», para la pista de «Otras formas»
        self._own_moves: tuple[list[Move], bool] = ([], False)  # «Tus movimientos» (spec own-moves)
        # Bloques plegados por modo de ficha (improve-card-visuals D11)
        self.collapsed: dict[str, set[str]] = {"normal": set(), "competitive": set()}
        # Secciones ocultas por modo, elegidas en Ajustes › Ficha (redesign-settings-window D8)
        self.hidden: dict[str, frozenset[str]] = {"normal": frozenset(), "competitive": frozenset()}
        self._cards: list[QWidget] = []
        self._card_inner = 0
        self._target_rect: tuple[int, int, int, int] | None = None
        self.saved_pos: QPoint | None = None
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(card_width(mode))
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
        # El contenido va dentro de un área desplazable: si la ficha es más alta que la pantalla
        # (p. ej. modo Competitivo en una pantalla de 720 px), se limita y se desplaza con la rueda.
        panel_layout = QVBoxLayout(self._panel)
        panel_layout.setContentsMargins(1, 1, 1, 1)
        self._scroll = QScrollArea(self._panel)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setStyleSheet(
            "QScrollArea, #inner { background: transparent; }"
            f"QScrollBar:vertical {{ background: transparent; width: {SCROLLBAR_WIDTH}px; margin: 6px 2px 6px 0; }}"
            "QScrollBar::handle:vertical { background: #4a5268; border-radius: 3px; min-height: 30px; }"
            "QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page "
            "{ background: none; height: 0; }"
        )
        self._scroll.viewport().setAutoFillBackground(False)
        self._inner = QWidget()
        self._inner.setObjectName("inner")
        self._scroll.setWidget(self._inner)
        panel_layout.addWidget(self._scroll)
        self._content = QVBoxLayout(self._inner)
        self._content.setContentsMargins(PANEL_PADDING, 12, PANEL_PADDING, 12)
        self._content.setSpacing(6)
        self._base_width = card_width(mode)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)
        self.auto_hide_seconds = auto_hide_seconds

        self._press_global: QPoint | None = None
        self._press_offset = QPoint()
        self._press_block: str | None = None
        self._dragging = False
        self._capture_excluded = False

    # ---- contenido ---------------------------------------------------------

    def show_species(
        self,
        species: Species,
        target_rect: tuple[int, int, int, int] | None,
        game: str | None = None,
        level: int | None = None,
    ) -> None:
        self.show_battle([self.pokedex.view(species.id, game, self.language)], None, target_rect, [level])

    def show_view(self, view: SpeciesView, target_rect: tuple[int, int, int, int] | None) -> None:
        self.show_battle([view], None, target_rect)

    def show_battle(
        self,
        rivals: list[SpeciesView],
        own: SpeciesView | None,
        target_rect: tuple[int, int, int, int] | None,
        rival_levels: list[int | None] | None = None,
        own_level: int | None = None,
        own_moves: list[Move] | None = None,
        own_moves_probable: bool = False,
    ) -> None:
        """Una tarjeta por rival (dos en combates dobles), según el modo (spec display-modes)."""
        self._own_moves = (list(own_moves or []), own_moves_probable)
        self._clear()
        # Ancho fijo por tarjeta (descontando los márgenes del panel): así el texto se parte
        # en líneas con el ancho real y no se recorta en los combates dobles.
        inner = card_width(self.mode) - 2 * PANEL_PADDING
        self._card_inner = inner
        self._base_width = inner * len(rivals) + CARD_SPACING * (len(rivals) - 1) + 2 * PANEL_PADDING
        levels = list(rival_levels or []) + [None] * len(rivals)
        row = QHBoxLayout()
        row.setSpacing(CARD_SPACING)
        for index, (rival, level) in enumerate(zip(rivals, levels)):
            versus = matchup(own, rival, self.pokedex.type_chart(rival.generation)) if own else None
            closable = index == len(rivals) - 1  # un solo ✕, en la tarjeta de la derecha
            card = self._card(rival, versus, level=level, own=own, own_level=own_level, closable=closable)
            card.setFixedWidth(inner)
            self._cards.append(card)
            row.addWidget(card, 0, Qt.AlignmentFlag.AlignTop)
        self._fit_cards()
        self._content.addLayout(row)
        self._present(target_rect)

    def _fit_cards(self) -> None:
        # Qt no aplica heightForWidth al calcular el tamaño de una ventana de nivel superior:
        # se fija la altura mínima que necesita cada tarjeta con su ancho (textos partidos en líneas).
        # Tras plegar un bloque, Qt recalcula los layouts en el siguiente ciclo de eventos: sin procesarlos
        # ya, se reutiliza la altura de antes y el sobrante se reparte entre los bloques plegados.
        QCoreApplication.sendPostedEvents(None, QEvent.Type.LayoutRequest.value)
        for card in self._cards:
            card.setMinimumHeight(0)
            card.layout().activate()
            card.setMinimumHeight(card.layout().totalHeightForWidth(self._card_inner))

    @property
    def competitive(self) -> bool:
        return self.mode == "competitive"

    def _type_label(self, type_id: str) -> str:
        return self.pokedex.type_name(type_id, self.language)

    def _types_row(self, types, solid: bool = False) -> QWidget:
        return _FlowRow([_pill(self._type_label(t), t, solid=solid) for t in types])

    def _muted(self, text: str, size: int = 11, name: str | None = None, wrap: bool = True) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:{size}px;")
        label.setWordWrap(wrap)
        if name:
            label.setObjectName(name)
        return label

    def _block(self, key: str, title: str, layout: QVBoxLayout, extra: QWidget | None = None,
               accent: str | None = None) -> _Block:
        block = _Block(key, title, extra, accent)
        block.set_collapsed(key in self.collapsed.get(self.mode, set()))
        layout.addWidget(block)
        if key in self.hidden.get(self.mode, frozenset()):
            block.hide()  # se construye igual (el resto de la sección le añade contenido) pero no ocupa sitio
        return block

    def _card(
        self,
        view: SpeciesView,
        versus: Matchup | None = None,
        level: int | None = None,
        own: SpeciesView | None = None,
        own_level: int | None = None,
        closable: bool = False,
    ) -> QWidget:
        card = QWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        ranges = view_ranges(view, level) if (self.competitive and level) else None

        self._header(view, level, layout, closable)
        if versus is not None:  # lo más consultado en cada turno: justo debajo de la cabecera
            self._matchup_section(versus, layout, view, ranges, own, own_level)
            self._own_moves_section(view, layout)
        self._effectiveness(view, layout)
        if self.competitive:
            self._stats_detailed(view, ranges, layout)
            self._abilities_detailed(view, layout)
            self._moves(view, level, own, layout)
            self._training(view, layout)
        self._evolution(view, layout)
        self._other_forms(view, layout)
        return card

    # ---- secciones comunes ---------------------------------------------------

    def _close_button(self) -> QPushButton:
        """✕ para cerrar la ficha: el resto de la ficha ya no la cierra con un clic (redesign-settings-window)."""
        button = QPushButton("✕")
        button.setObjectName("close-button")
        button.setToolTip(_("Cerrar"))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFixedSize(22, 22)
        button.setStyleSheet(
            f"#close-button {{ color:{theme.TEXT_MUTED}; background:transparent; border:none; border-radius:11px;"
            " font-size:12px; font-weight:700; padding:0; }"
            f"#close-button:hover {{ color:{theme.TEXT}; background:{theme.rgba('#e5484d', 0.55)}; }}"
        )
        button.clicked.connect(self.close_by_user)
        return button

    def close_by_user(self) -> None:
        self.hide()
        self.dismissed.emit()

    def _header(self, view: SpeciesView, level: int | None, layout: QVBoxLayout, closable: bool = False) -> None:
        """Cabecera teñida con el primer tipo: nombre, nivel, número, tipos sólidos y captura."""
        head = QFrame()
        head.setObjectName("card-head")
        tint = theme.TYPE_COLORS.get(view.types[0] if view.types else "", theme.NEUTRAL)
        head.setStyleSheet(
            "#card-head { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
            f"stop:0 {theme.rgba(tint, 0.20)}, stop:1 {theme.rgba(tint, 0.04)}); "
            f"border:1px solid {theme.rgba(tint, 0.28)}; border-radius:10px; }}"
        )
        box = QVBoxLayout(head)
        box.setContentsMargins(10, 9, 10, 9)
        box.setSpacing(6)
        top = QHBoxLayout()
        top.setSpacing(8)
        name = QLabel(view.name)
        name.setObjectName("species-name")
        name.setWordWrap(True)
        name.setStyleSheet(f"font-size:{20 if self.competitive else 18}px; font-weight:700;")
        top.addWidget(name, 1)
        if self.competitive:
            lvl = QLabel(_("Nv. {level}", level=level) if level else _("Nv. ?"))
            lvl.setObjectName("level")
            lvl.setStyleSheet(f"color:{theme.ACCENT}; font-size:13px; font-weight:700;")
            top.addWidget(lvl, alignment=Qt.AlignmentFlag.AlignTop)
        number = QLabel(f"#{view.species_id:04d}")
        number.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:12px;")
        top.addWidget(number, alignment=Qt.AlignmentFlag.AlignTop)
        if closable:
            top.addWidget(self._close_button(), alignment=Qt.AlignmentFlag.AlignTop)
        box.addLayout(top)
        box.addWidget(self._types_row(view.types, solid=True))
        self._capture(view, box)
        if not self.competitive:
            total = QLabel(_("Total estadísticas base: {total}", total=f"<b>{view.stat_total}</b>"))
            total.setObjectName("stat-total")
            total.setTextFormat(Qt.TextFormat.RichText)
            total.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:11px;")
            box.addWidget(total)
        layout.addWidget(head)

    def _capture(self, view: SpeciesView, layout: QVBoxLayout) -> None:
        if view.capture_rate is None:
            return
        capture = QLabel(_("Captura: {rate} · {difficulty}", rate=view.capture_rate,
                           difficulty=_(view.capture_difficulty or "")))
        capture.setObjectName("capture")
        if self.competitive:
            capture.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:11px;")
            layout.addWidget(capture)
            return
        # En modo Normal, la captura es protagonista: texto en el color de la dificultad y medidor (D6)
        color = CAPTURE_COLORS.get(view.capture_difficulty, theme.TEXT)
        capture.setStyleSheet(f"color:{color}; font-size:12px; font-weight:700;")
        meter = QProgressBar()
        meter.setObjectName("capture-meter")
        meter.setRange(0, 255)
        meter.setValue(view.capture_rate)
        meter.setTextVisible(False)
        meter.setFixedHeight(6)
        meter.setStyleSheet(
            "QProgressBar { background:rgba(255, 255, 255, 20); border:none; border-radius:3px; }"
            f"QProgressBar::chunk {{ background:{color}; border-radius:3px; }}"
        )
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(capture)
        row.addWidget(meter, 1)
        layout.addLayout(row)

    def _matchup_section(
        self,
        m: Matchup,
        layout: QVBoxLayout,
        rival: SpeciesView,
        rival_ranges: dict[str, tuple[int, int]] | None,
        own: SpeciesView | None,
        own_level: int | None,
    ) -> None:
        verdict = _pill(_(m.verdict.value), bg=VERDICT_COLORS[m.verdict])
        verdict.setObjectName("verdict")
        block = self._block("matchup", _("Contra tu {name}", name=m.own_name), layout, verdict,
                            accent=VERDICT_COLORS[m.verdict])
        notes: list[str] = []
        grid = QGridLayout()
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(4)
        sides = ((_("Tú"), m.offense, m.offense_effects, True), (_("Él"), m.defense, m.defense_effects, False))
        for i, (label, pairs, effects, mine) in enumerate(sides):
            who = QLabel(label)
            who.setMinimumWidth(26)  # «Them» en inglés no cabe en 26 px
            who.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:11px;")
            grid.addWidget(who, i, 0, Qt.AlignmentFlag.AlignTop)
            typed = []
            for t, x in pairs:
                found = effects.get(t, ())
                mark = "*" if any(not e.certain for e in found) else ""
                typed.append(_Typed(self._type_label(t), t, multiplier_text(x) + mark, _tone(x, mine)))
                notes += [matchup_note(e, self._type_label, self.language) for e in found]
            grid.addWidget(_FlowRow(typed, per_row=2), i, 1)
        grid.setColumnStretch(1, 1)
        block.add(grid)
        for note in notes:
            block.add(self._muted(note, size=10, name="matchup-ability-note"))
        if self.competitive and rival_ranges and own is not None and own_level:
            own_speed = view_ranges(own, own_level, own=True)["speed"]
            speed = compare_speed(own_speed, rival_ranges["speed"])
            text = _("Velocidad: {verdict} (tú {own_min}-{own_max}, él {rival_min}-{rival_max})",
                     verdict=_(speed.value), own_min=own_speed[0], own_max=own_speed[1],
                     rival_min=rival_ranges["speed"][0], rival_max=rival_ranges["speed"][1])
            block.add(self._muted(text, name="speed"))

    def _own_moves_section(self, rival: SpeciesView, layout: QVBoxLayout) -> None:
        """«Tus movimientos»: los leídos del menú (o los probables) con su multiplicador contra el rival."""
        moves, probable = self._own_moves
        if not moves:
            return
        block = self._block("own_moves", _("Tus movimientos (probables)") if probable else _("Tus movimientos"), layout)
        chart = self.pokedex.type_chart(rival.generation)
        grid = QGridLayout()
        grid.setVerticalSpacing(4)
        for i, move in enumerate(moves):
            pill = _pill(self._type_label(move.type) if move.type else "?", move.type)
            pill.setFixedWidth(MOVE_TYPE_WIDTH)
            pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(pill, i, 0)
            name = QLabel(move.name(self.language))
            name.setObjectName("own-move")
            grid.addWidget(name, i, 1)
            if move.category == "status" or not move.type:
                mult = self._muted(_("Estado"), wrap=False, name="own-move-vs-rival")
            else:
                factor, effects = effective_multiplier(chart, move.type, rival)
                mark = "*" if any(not e.certain for e in effects) else ""
                mult = _mult(multiplier_text(factor) + mark, _tone(factor), "own-move-vs-rival")
            grid.addWidget(mult, i, 2, Qt.AlignmentFlag.AlignRight)
        grid.setColumnStretch(1, 1)
        block.add(grid)

    def _effectiveness(self, view: SpeciesView, layout: QVBoxLayout) -> None:
        """Debilidades (verde: bueno para ti), resistencias (rojo) e inmunidades (gris) en un bloque (D4)."""
        groups = view.matchups
        sections = [(_("Debilidades"), (4.0, 2.0), "good")]
        if self.competitive:
            sections.append((_("Resistencias"), (0.5, 0.25), "bad"))
        sections.append((_("Inmunidades"), (0.0,), "neutral"))
        lines = ability_effect_lines(view, self._type_label, self.language)
        present = [s for s in sections if any(groups[m] for m in s[1])]
        if not present and not lines:
            return
        block = self._block("eff", _("Eficacias"), layout)
        for title, multipliers, tone in present:
            block.add(_sub_title(title))
            for m in multipliers:
                if not groups[m]:
                    continue
                row = QHBoxLayout()
                row.setSpacing(6)
                mult = _mult(theme.MULTIPLIER_LABELS[m], tone, "eff-mult")
                mult.setFixedWidth(30)
                row.addWidget(mult, alignment=Qt.AlignmentFlag.AlignTop)
                # Dentro del bloque y con la columna del multiplicador, en Normal (300 px) caben 3 por fila
                pills = [_pill(self._type_label(t), t) for t in groups[m]]
                row.addWidget(_FlowRow(pills, per_row=4 if self.competitive else 3), 1)
                block.add(row)
        for line in lines:
            block.add(self._muted(line, size=10, name="ability-effect-line"))

    def _evolution(self, view: SpeciesView, layout: QVBoxLayout) -> None:
        if len(view.evolution) <= 1:
            return
        block = self._block("evo", _("Evolución"), layout)
        muted = theme.TEXT_MUTED

        def stage_html(stage) -> str:
            parts = []
            for n, c in stage:
                current = n == view.name or view.name.startswith(n + " ")
                name = f"<b>{_escape(n)}</b>" if current else f"<span style='color:{muted}'>{_escape(n)}</span>"
                cond = f" <span style='color:{muted}; font-size:10px'>({_escape(c)})</span>" if c else ""
                parts.append(name + cond)
            return " / ".join(parts)

        arrow = f" <span style='color:{muted}'>→</span> "
        evolution = QLabel(arrow.join(stage_html(stage) for stage in view.evolution))
        evolution.setObjectName("evolution")
        evolution.setTextFormat(Qt.TextFormat.RichText)
        evolution.setWordWrap(True)
        block.add(evolution)

    def _other_forms(self, view: SpeciesView, layout: QVBoxLayout) -> None:
        if not view.other_forms:
            return
        block = self._block("forms", _("Otras formas"), layout)
        for other in view.other_forms:
            row = QHBoxLayout()
            label = QLabel(other.name)
            label.setStyleSheet(f"color:{theme.TEXT_MUTED};")
            row.addWidget(label)
            row.addWidget(self._types_row(other.types), 1)
            block.add(row)
        if self.form_hotkey:
            block.add(self._muted(_("{hotkey}: cambiar de forma", hotkey=self.form_hotkey), size=10, name="form-hint"))

    # ---- secciones del modo Competitivo -----------------------------------------

    def _stats_detailed(self, view: SpeciesView, ranges, layout: QVBoxLayout) -> None:
        title = _("Estadísticas base · rango a su nivel") if ranges else _("Estadísticas base")
        block = self._block("stats", title, layout)
        stats = QGridLayout()
        stats.setVerticalSpacing(3)
        stats.setHorizontalSpacing(8)
        values = [view.stats[k] for k in view.stat_keys]
        highest, lowest = max(values), min(values)
        for i, key in enumerate(view.stat_keys):
            value = view.stats[key]
            label = QLabel(_(theme.STAT_LABELS[key]))
            label.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:12px;")
            val = QLabel(str(value))
            val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            val_color = theme.STAT_BAR_MAX if value == highest else theme.TEXT
            val.setStyleSheet(f"font-weight:600; font-size:12px; color:{val_color};")
            bar = QProgressBar()
            bar.setRange(0, 255)
            bar.setValue(value)
            bar.setTextVisible(False)
            bar.setFixedHeight(7)
            bar.setStyleSheet(
                "QProgressBar { background:rgba(255, 255, 255, 15); border:none; border-radius:3px; }"
                f"QProgressBar::chunk {{ background:{theme.stat_bar_color(value, highest, lowest)}; border-radius:3px; }}"
            )
            stats.addWidget(label, i, 0)
            stats.addWidget(val, i, 1)
            stats.addWidget(bar, i, 2)
            if ranges:
                low, high = ranges[key]
                rng = self._muted(f"{low}-{high}", wrap=False, name=f"range-{key}")
                rng.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                stats.addWidget(rng, i, 3)
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background:{theme.SURFACE_BORDER}; border:none;")
        row = len(view.stat_keys)
        stats.addWidget(separator, row, 0, 1, 4 if ranges else 3)
        total_label = QLabel(_("Total"))
        total_label.setStyleSheet("font-weight:700; font-size:12px;")
        total = QLabel(str(view.stat_total))
        total.setObjectName("stat-total")
        total.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        total.setStyleSheet("font-weight:700; font-size:12px;")
        stats.addWidget(total_label, row + 1, 0)
        stats.addWidget(total, row + 1, 1)
        stats.setColumnMinimumWidth(1, 28)
        stats.setColumnStretch(2, 1)
        block.add(stats)

    def _abilities_detailed(self, view: SpeciesView, layout: QVBoxLayout) -> None:
        if not view.abilities:
            return
        block = self._block("abilities", _("Habilidades"), layout)
        for ability in view.abilities:
            hidden = f"  <i style='color:{theme.TEXT_MUTED}'>{_('(oculta)')}</i>" if ability.hidden else ""
            name = QLabel(f"<b>{ability.name(self.language)}</b>{hidden}")
            name.setTextFormat(Qt.TextFormat.RichText)
            description = ability.description(self.language)
            if description:
                name.setToolTip(description)
            block.add(name)
            effects = ability_effects(ability.identifier, self._type_label)
            if effects:
                chips = [_outline(e) for e in effects]
                for chip in chips:
                    chip.setObjectName("ability-effect")
                block.add(_FlowRow(chips, per_row=2))
            if description:
                block.add(self._muted(description, size=10, name="ability-description"))

    def _moves(self, view: SpeciesView, level: int | None, own: SpeciesView | None, layout: QVBoxLayout) -> None:
        block = self._block("moves", _("Movimientos probables"), layout)
        if not level:
            block.add(self._muted(
                _("Nivel no leído: recalibra la región del rival incluyendo el nivel para ver sus movimientos."),
                name="moves-hint",
            ))
            return
        try:
            game = self.pokedex.get_game(view.game_id)
            learnsets = Learnsets.get()
            generation = game.generation if game else None
            moves = learnsets.probable_moves(view.pokemon or "", level, view.game_id, generation)
            if not moves and view.base_pokemon and view.base_pokemon != view.pokemon:  # megas: los de la base
                moves = learnsets.probable_moves(view.base_pokemon, level, view.game_id, generation)
        except LearnsetsMissingError as exc:
            block.add(self._muted(str(exc), name="moves-hint"))
            return
        if not moves:
            block.add(self._muted(_("Sin datos de movimientos para este Pokémon."), name="moves-hint"))
            return
        chart = self.pokedex.type_chart(view.generation)
        grid = QGridLayout()
        grid.setVerticalSpacing(4)
        grid.setHorizontalSpacing(8)
        for i, move in enumerate(moves):
            type_pill = _pill(self._type_label(move.type) if move.type else "?", move.type)
            type_pill.setFixedWidth(MOVE_TYPE_WIDTH)
            type_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name = QLabel(move.name(self.language))
            name.setObjectName("move")
            category = _(CATEGORY_LABELS[move.category]) if move.category in CATEGORY_LABELS else ""
            detail = f"{category} · {move.power or '—'}"
            info = self._muted(detail, wrap=False)
            info.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            grid.addWidget(type_pill, i, 0)
            grid.addWidget(name, i, 1)
            grid.addWidget(info, i, 2)
            if own is not None and move.type and move.category != "status":
                factor, _effects = effective_multiplier(chart, move.type, own)
                if factor != 1.0:  # contra ti: más de ×1 es malo para ti
                    grid.addWidget(_mult(multiplier_text(factor), _tone(factor, for_player=False), "move-vs-you"), i, 3)
        grid.setColumnStretch(1, 1)
        block.add(grid)

    def _training(self, view: SpeciesView, layout: QVBoxLayout) -> None:
        block = self._block("training", _("Entrenamiento"), layout)
        evs = ", ".join(f"{n} {_(theme.STAT_LABELS[s])}" for s, n in view.ev_yield.items()) or "—"
        lines = [_("EVs que da: {evs}", evs=evs)]
        if view.weight_kg is not None:
            weight = f"{view.weight_kg:g}"
            if get_language() == "es":  # coma decimal en español, punto en inglés
                weight = weight.replace(".", ",")
            lines.append(_("Peso: {weight} kg (Patada Baja/Hierba Lazo: {power})",
                           weight=weight, power=weight_move_power(view.weight_kg)))
        lines.append(_("Perfil: {profile}", profile=", ".join(_(p) for p in stat_profile(view.stats))))
        # Pares etiqueta/valor en dos columnas (D8): cada línea se parte por su primer «: »
        rows = []
        for line in lines:
            key, sep, value = line.partition(": ")
            if not sep:
                key, value = "", line
            rows.append(f"<tr><td style='color:{theme.TEXT_MUTED}; padding-right:10px'>{_escape(key)}</td>"
                        f"<td>{_escape(value)}</td></tr>")
        training = QLabel(f"<table cellspacing='0' cellpadding='1'>{''.join(rows)}</table>")
        training.setObjectName("training")
        training.setTextFormat(Qt.TextFormat.RichText)
        training.setWordWrap(True)
        training.setStyleSheet("font-size:12px;")
        block.add(training)

    def show_unrecognized(self, raw_text: str, target_rect: tuple[int, int, int, int] | None) -> None:
        self._clear()
        self._base_width = card_width(self.mode)
        title = QLabel(_("No reconocido"))
        title.setStyleSheet("font-size:16px; font-weight:700;")
        top = QHBoxLayout()
        top.addWidget(title, 1)
        top.addWidget(self._close_button(), alignment=Qt.AlignmentFlag.AlignTop)
        self._content.addLayout(top)
        read = raw_text.strip() or _("(vacío)")
        detail = QLabel(
            _("Texto leído: {text}", text=f"<b>{_escape(read)}</b>") + "<br>"
            f"<span style='color:{theme.TEXT_MUTED}'>"
            + _("Si el texto no es el nombre del rival, recalibra la región del rival en Ajustes › Perfiles.")
            + "</span>"
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

        self._cards = []
        clear_layout(self._content)

    # ---- bloques plegables (improve-card-visuals D11) -------------------------------

    def blocks(self, key: str | None = None) -> list[_Block]:
        found = self._inner.findChildren(_Block)
        return [b for b in found if key is None or b.key == key]

    def toggle_block(self, key: str) -> None:
        """Pliega o despliega un bloque en todas las tarjetas y lo recuerda para este modo."""
        collapsed = self.collapsed.setdefault(self.mode, set())
        if key in collapsed:
            collapsed.discard(key)
        else:
            collapsed.add(key)
        for block in self.blocks(key):
            block.set_collapsed(key in collapsed)
        self._relayout()
        self.collapsed_changed.emit()

    def expand_all(self) -> None:
        """«Desplegar todas las secciones»: olvida lo plegado en los dos modos."""
        self.collapsed = {"normal": set(), "competitive": set()}
        for block in self.blocks():
            block.set_collapsed(False)
        self._relayout()
        self.collapsed_changed.emit()

    def _relayout(self) -> None:
        """Nueva altura tras plegar o desplegar, sin mover la ficha de su sitio."""
        if not self._cards:
            return
        self._fit_cards()
        top_left = self.pos()
        self._fit_to_screen(self._target_rect)
        self.move(self._clamp(top_left, self.size()))

    def _block_at(self, pos: QPoint) -> str | None:
        widget = self.childAt(pos)
        while widget is not None and widget is not self:
            key = widget.property("block_key")
            if key:
                return key
            widget = widget.parentWidget()
        return None

    # ---- posición y visibilidad -------------------------------------------

    def _available_height(self, target_rect: tuple[int, int, int, int] | None) -> int:
        point = physical_to_logical(target_rect[0], target_rect[1]) if target_rect else None
        screen = (QGuiApplication.screenAt(point) if point else None) or QGuiApplication.primaryScreen()
        return screen.availableGeometry().height() - 2 * MARGIN

    def _chrome(self) -> tuple[int, int]:
        """Ancho y alto que ocupan el borde del panel y sus márgenes alrededor del área desplazable."""
        frame = self._panel.contentsMargins()
        layout = self._panel.layout().contentsMargins()
        return (frame.left() + frame.right() + layout.left() + layout.right(),
                frame.top() + frame.bottom() + layout.top() + layout.bottom())

    def _fit_to_screen(self, target_rect: tuple[int, int, int, int] | None) -> None:
        """Tamaño final: alto del contenido, sin pasar del de la pantalla (con desplazamiento si no cabe)."""
        chrome_w, chrome_h = self._chrome()
        inner_width = self._base_width - chrome_w
        self._inner.setFixedWidth(inner_width)
        # Con la ficha ya visible (cambio de modo, de forma o movimientos leídos), Qt no muestra los
        # widgets nuevos hasta el siguiente ciclo de eventos y el layout no los mide: se muestran ya.
        for child in self._inner.findChildren(QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly):
            child.show()
        self._content.invalidate()
        self._content.activate()
        hint = self._content.totalSizeHint().height()
        if self._content.hasHeightForWidth():  # textos partidos en líneas (ver show_battle)
            hint = max(hint, self._content.totalHeightForWidth(inner_width))
        content_height = hint + chrome_h
        available = self._available_height(target_rect)
        scrolling = content_height > available
        self.setFixedSize(self._base_width + (SCROLLBAR_WIDTH if scrolling else 0), min(content_height, available))
        self._scroll.verticalScrollBar().setValue(0)

    @property
    def scrollable(self) -> bool:
        return self._scroll.verticalScrollBar().maximum() > 0

    def _present(self, target_rect: tuple[int, int, int, int] | None) -> None:
        self._target_rect = target_rect
        self._fit_to_screen(target_rect)
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

    # ---- ratón: arrastrar para mover, clic en un título para plegar; el ✕ la cierra ----

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_global = event.globalPosition().toPoint()
            self._press_offset = self._press_global - self.frameGeometry().topLeft()
            self._press_block = self._block_at(event.position().toPoint())
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
        elif self._press_block:
            self.toggle_block(self._press_block)
        # un clic en el resto de la ficha no hace nada: se cierra con el ✕
        self._press_global = None
        self._press_block = None
        self._dragging = False


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
