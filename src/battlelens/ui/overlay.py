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
CATEGORY_LABELS = {"physical": N_("Físico"), "special": N_("Especial"), "status": N_("Estado")}
CAPTURE_COLORS = theme.CAPTURE_COLORS
ABILITY_EFFECT_COLOR = "#3a4a6b"


def card_width(mode: str) -> int:
    return MODE_WIDTHS.get(mode, MODE_WIDTHS["normal"])
VERDICT_COLORS = {
    Verdict.ADVANTAGE: "#2e9d5b",
    Verdict.NEUTRAL: "#5b6274",
    Verdict.DISADVANTAGE: "#c8414b",
}
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
        self._base_width = inner * len(rivals) + CARD_SPACING * (len(rivals) - 1) + 2 * PANEL_PADDING
        levels = list(rival_levels or []) + [None] * len(rivals)
        row = QHBoxLayout()
        row.setSpacing(CARD_SPACING)
        for rival, level in zip(rivals, levels):
            versus = matchup(own, rival, self.pokedex.type_chart(rival.generation)) if own else None
            card = self._card(rival, versus, level=level, own=own, own_level=own_level)
            card.setFixedWidth(inner)
            # Qt no aplica heightForWidth al calcular el tamaño de una ventana de nivel superior:
            # se fija la altura mínima que necesita la tarjeta con ese ancho (textos partidos en líneas).
            card.layout().activate()
            card.setMinimumHeight(card.layout().totalHeightForWidth(inner))
            row.addWidget(card, 0, Qt.AlignmentFlag.AlignTop)
        self._content.addLayout(row)
        self._present(target_rect)

    @property
    def competitive(self) -> bool:
        return self.mode == "competitive"

    def _type_label(self, type_id: str) -> str:
        return self.pokedex.type_name(type_id, self.language)

    def _types_row(self, types) -> QWidget:
        return _FlowRow([_pill(self._type_label(t), t) for t in types])

    def _muted(self, text: str, size: int = 11, name: str | None = None, wrap: bool = True) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:{size}px;")
        label.setWordWrap(wrap)
        if name:
            label.setObjectName(name)
        return label

    def _card(
        self,
        view: SpeciesView,
        versus: Matchup | None = None,
        level: int | None = None,
        own: SpeciesView | None = None,
        own_level: int | None = None,
    ) -> QWidget:
        card = QWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        ranges = view_ranges(view, level) if (self.competitive and level) else None

        self._header(view, level, layout)
        layout.addWidget(self._types_row(view.types))
        self._capture(view, layout)
        if versus is not None:  # lo más consultado en cada turno: justo debajo de los tipos
            self._matchup_section(versus, layout, view, ranges, own, own_level)
            self._own_moves_section(view, layout)
        self._effectiveness(view, layout)
        if self.competitive:
            self._stats_detailed(view, ranges, layout)
            self._abilities_detailed(view, layout)
            self._moves(view, level, own, layout)
            self._training(view, layout)
        else:
            total = QLabel(_("Total estadísticas base: {total}", total=f"<b>{view.stat_total}</b>"))
            total.setObjectName("stat-total")
            total.setTextFormat(Qt.TextFormat.RichText)
            layout.addWidget(total)
        self._evolution(view, layout)
        self._other_forms(view, layout)
        return card

    # ---- secciones comunes ---------------------------------------------------

    def _header(self, view: SpeciesView, level: int | None, layout: QVBoxLayout) -> None:
        header = QHBoxLayout()
        name = QLabel(view.name)
        name.setObjectName("species-name")
        name.setWordWrap(True)
        name.setStyleSheet(f"font-size:{20 if self.competitive else 18}px; font-weight:700;")
        header.addWidget(name, 1)
        if self.competitive:
            lvl = QLabel(_("Nv. {level}", level=level) if level else _("Nv. ?"))
            lvl.setObjectName("level")
            lvl.setStyleSheet(f"color:{theme.ACCENT}; font-size:13px; font-weight:700;")
            header.addWidget(lvl, alignment=Qt.AlignmentFlag.AlignTop)
        number = QLabel(f"#{view.species_id:04d}")
        number.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:13px;")
        header.addWidget(number, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header)

    def _capture(self, view: SpeciesView, layout: QVBoxLayout) -> None:
        if view.capture_rate is None:
            return
        capture = QLabel(_("Captura: {rate} · {difficulty}", rate=view.capture_rate,
                           difficulty=_(view.capture_difficulty or "")))
        capture.setObjectName("capture")
        if self.competitive:
            capture.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:11px;")
        else:  # en modo Normal, la captura es protagonista
            color = CAPTURE_COLORS.get(view.capture_difficulty, theme.TEXT)
            capture.setStyleSheet(f"color:{color}; font-size:13px; font-weight:700;")
        layout.addWidget(capture)

    def _matchup_section(
        self,
        m: Matchup,
        layout: QVBoxLayout,
        rival: SpeciesView,
        rival_ranges: dict[str, tuple[int, int]] | None,
        own: SpeciesView | None,
        own_level: int | None,
    ) -> None:
        header = QHBoxLayout()
        header.addWidget(_section_title(_("Contra tu {name}", name=m.own_name)))
        verdict = _pill(_(m.verdict.value), bg=VERDICT_COLORS[m.verdict])
        verdict.setObjectName("verdict")
        header.addStretch(1)
        header.addWidget(verdict)
        layout.addLayout(header)
        notes: list[str] = []
        for label, pairs, effects in ((_("Tú"), m.offense, m.offense_effects), (_("Él"), m.defense, m.defense_effects)):
            row = QHBoxLayout()
            who = QLabel(label)
            who.setMinimumWidth(26)  # «Them» en inglés no cabe en 26 px
            who.setStyleSheet(f"color:{theme.ACCENT}; font-weight:700;")
            row.addWidget(who, alignment=Qt.AlignmentFlag.AlignTop)
            pills = []
            for t, x in pairs:
                found = effects.get(t, ())
                mark = "*" if any(not e.certain for e in found) else ""
                pills.append(_pill(f"{self._type_label(t)} {multiplier_text(x)}{mark}", t))
                notes += [matchup_note(e, self._type_label, self.language) for e in found]
            row.addWidget(_FlowRow(pills, per_row=2), 1)
            layout.addLayout(row)
        for note in notes:
            layout.addWidget(self._muted(note, size=10, name="matchup-ability-note"))
        if self.competitive and rival_ranges and own is not None and own_level:
            own_speed = view_ranges(own, own_level, own=True)["speed"]
            speed = compare_speed(own_speed, rival_ranges["speed"])
            text = _("Velocidad: {verdict} (tú {own_min}-{own_max}, él {rival_min}-{rival_max})",
                     verdict=_(speed.value), own_min=own_speed[0], own_max=own_speed[1],
                     rival_min=rival_ranges["speed"][0], rival_max=rival_ranges["speed"][1])
            layout.addWidget(self._muted(text, name="speed"))

    def _own_moves_section(self, rival: SpeciesView, layout: QVBoxLayout) -> None:
        """«Tus movimientos»: los leídos del menú (o los probables) con su multiplicador contra el rival."""
        moves, probable = self._own_moves
        if not moves:
            return
        layout.addWidget(_section_title(_("Tus movimientos (probables)") if probable else _("Tus movimientos")))
        chart = self.pokedex.type_chart(rival.generation)
        grid = QGridLayout()
        grid.setVerticalSpacing(3)
        for i, move in enumerate(moves):
            grid.addWidget(_pill(self._type_label(move.type) if move.type else "?", move.type), i, 0)
            name = QLabel(move.name(self.language))
            name.setObjectName("own-move")
            grid.addWidget(name, i, 1)
            if move.category == "status" or not move.type:
                mult = self._muted(_("Estado"), wrap=False)
            else:
                factor, effects = effective_multiplier(chart, move.type, rival)
                mark = "*" if any(not e.certain for e in effects) else ""
                mult = QLabel(multiplier_text(factor) + mark)
                color = "#3ddc97" if factor > 1 else "#e5484d" if factor < 1 else theme.TEXT
                mult.setStyleSheet(f"color:{color}; font-weight:700;")
            mult.setObjectName("own-move-vs-rival")
            grid.addWidget(mult, i, 2)
        grid.setColumnStretch(1, 1)
        layout.addLayout(grid)

    def _effectiveness(self, view: SpeciesView, layout: QVBoxLayout) -> None:
        groups = view.matchups
        sections = [(_("Debilidades"), (4.0, 2.0))]
        if self.competitive:
            sections.append((_("Resistencias"), (0.5, 0.25)))
        sections.append((_("Inmunidades"), (0.0,)))
        for title, multipliers in sections:
            if not any(groups[m] for m in multipliers):
                continue
            layout.addWidget(_section_title(title))
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
        for line in ability_effect_lines(view, self._type_label, self.language):
            layout.addWidget(self._muted(line, size=10, name="ability-effect-line"))

    def _evolution(self, view: SpeciesView, layout: QVBoxLayout) -> None:
        if len(view.evolution) <= 1:
            return
        layout.addWidget(_section_title(_("Evolución")))
        stages = [" / ".join(f"{n} ({c})" if c else n for n, c in stage) for stage in view.evolution]
        evolution = QLabel(" → ".join(stages))
        evolution.setObjectName("evolution")
        evolution.setWordWrap(True)
        layout.addWidget(evolution)

    def _other_forms(self, view: SpeciesView, layout: QVBoxLayout) -> None:
        if not view.other_forms:
            return
        layout.addWidget(_section_title(_("Otras formas")))
        for other in view.other_forms:
            row = QHBoxLayout()
            label = QLabel(other.name)
            label.setStyleSheet(f"color:{theme.TEXT_MUTED};")
            row.addWidget(label)
            row.addWidget(self._types_row(other.types), 1)
            layout.addLayout(row)
        if self.form_hotkey:
            layout.addWidget(self._muted(_("{hotkey}: cambiar de forma", hotkey=self.form_hotkey), size=10, name="form-hint"))

    # ---- secciones del modo Competitivo -----------------------------------------

    def _stats_detailed(self, view: SpeciesView, ranges, layout: QVBoxLayout) -> None:
        title = _("Estadísticas base · rango a su nivel") if ranges else _("Estadísticas base")
        layout.addWidget(_section_title(title))
        stats = QGridLayout()
        stats.setVerticalSpacing(2)
        for i, key in enumerate(view.stat_keys):
            value = view.stats[key]
            label = QLabel(_(theme.STAT_LABELS[key]))
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
            if ranges:
                low, high = ranges[key]
                rng = self._muted(f"{low}-{high}", wrap=False, name=f"range-{key}")
                rng.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                stats.addWidget(rng, i, 3)
        total_label = QLabel(_("Total"))
        total_label.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-weight:700;")
        total = QLabel(str(view.stat_total))
        total.setObjectName("stat-total")
        total.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        total.setStyleSheet("font-weight:700;")
        stats.addWidget(total_label, len(view.stat_keys), 0)
        stats.addWidget(total, len(view.stat_keys), 1)
        stats.setColumnMinimumWidth(1, 30)
        stats.setColumnStretch(2, 1)
        layout.addLayout(stats)

    def _abilities_detailed(self, view: SpeciesView, layout: QVBoxLayout) -> None:
        if not view.abilities:
            return
        layout.addWidget(_section_title(_("Habilidades")))
        for ability in view.abilities:
            hidden = f"  <i style='color:{theme.TEXT_MUTED}'>{_('(oculta)')}</i>" if ability.hidden else ""
            name = QLabel(f"<b>{ability.name(self.language)}</b>{hidden}")
            name.setTextFormat(Qt.TextFormat.RichText)
            description = ability.description(self.language)
            if description:
                name.setToolTip(description)
            layout.addWidget(name)
            effects = ability_effects(ability.identifier, self._type_label)
            if effects:
                chips = [_pill(e, bg=ABILITY_EFFECT_COLOR) for e in effects]
                for chip in chips:
                    chip.setObjectName("ability-effect")
                layout.addWidget(_FlowRow(chips, per_row=2))
            if description:
                layout.addWidget(self._muted(description, size=10, name="ability-description"))

    def _moves(self, view: SpeciesView, level: int | None, own: SpeciesView | None, layout: QVBoxLayout) -> None:
        layout.addWidget(_section_title(_("Movimientos probables")))
        if not level:
            layout.addWidget(self._muted(
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
            layout.addWidget(self._muted(str(exc), name="moves-hint"))
            return
        if not moves:
            layout.addWidget(self._muted(_("Sin datos de movimientos para este Pokémon."), name="moves-hint"))
            return
        chart = self.pokedex.type_chart(view.generation)
        grid = QGridLayout()
        grid.setVerticalSpacing(3)
        for i, move in enumerate(moves):
            type_pill = _pill(self._type_label(move.type) if move.type else "?", move.type)
            name = QLabel(move.name(self.language))
            name.setObjectName("move")
            category = _(CATEGORY_LABELS[move.category]) if move.category in CATEGORY_LABELS else ""
            detail = f"{category} · {move.power or '—'}"
            info = self._muted(detail, wrap=False)
            grid.addWidget(type_pill, i, 0)
            grid.addWidget(name, i, 1)
            grid.addWidget(info, i, 2)
            if own is not None and move.type and move.category != "status":
                factor, _effects = effective_multiplier(chart, move.type, own)
                if factor != 1.0:
                    mult = QLabel(multiplier_text(factor))
                    mult.setObjectName("move-vs-you")
                    color = "#e5484d" if factor > 1 else theme.TEXT_MUTED
                    mult.setStyleSheet(f"color:{color}; font-weight:700;")
                    grid.addWidget(mult, i, 3)
        grid.setColumnStretch(1, 1)
        layout.addLayout(grid)

    def _training(self, view: SpeciesView, layout: QVBoxLayout) -> None:
        layout.addWidget(_section_title(_("Entrenamiento")))
        evs = ", ".join(f"{n} {_(theme.STAT_LABELS[s])}" for s, n in view.ev_yield.items()) or "—"
        lines = [_("EVs que da: {evs}", evs=evs)]
        if view.weight_kg is not None:
            weight = f"{view.weight_kg:g}"
            if get_language() == "es":  # coma decimal en español, punto en inglés
                weight = weight.replace(".", ",")
            lines.append(_("Peso: {weight} kg (Patada Baja/Hierba Lazo: {power})",
                           weight=weight, power=weight_move_power(view.weight_kg)))
        lines.append(_("Perfil: {profile}", profile=", ".join(_(p) for p in stat_profile(view.stats))))
        layout.addWidget(self._muted("<br>".join(lines), name="training"))

    def show_unrecognized(self, raw_text: str, target_rect: tuple[int, int, int, int] | None) -> None:
        self._clear()
        self._base_width = card_width(self.mode)
        title = QLabel(_("No reconocido"))
        title.setStyleSheet("font-size:16px; font-weight:700;")
        self._content.addWidget(title)
        read = raw_text.strip() or _("(vacío)")
        detail = QLabel(
            _("Texto leído: {text}", text=f"<b>{_escape(read)}</b>") + "<br>"
            f"<span style='color:{theme.TEXT_MUTED}'>"
            + _("Si el texto no es el nombre del rival, recalibra la región del perfil desde la bandeja del sistema.")
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

        clear_layout(self._content)

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
