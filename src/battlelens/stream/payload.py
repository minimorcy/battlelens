"""Tarjetas de la ficha del stream en datos listos para dibujar (add-stream-mode D4).

El JS de la página no repite ninguna regla del juego: aquí se calculan los multiplicadores,
los textos y los colores con las mismas funciones que la ficha privada.
"""

from __future__ import annotations

from ..core.abilities import multiplier_text
from ..core.card_text import ability_effect_lines, matchup_note
from ..core.learnsets import Move
from ..core.matchup import Verdict, effective_multiplier, matchup
from ..core.pokedex import Pokedex, SpeciesView
from ..i18n import N_, _
from ..ui import theme

EFFECT_GROUPS = (("weaknesses", (4.0, 2.0)), ("resistances", (0.5, 0.25)), ("immunities", (0.0,)))
# Textos en español marcados con N_: se traducen al construir cada tarjeta (add-english-ui D5)
TITLES = {
    "versus": N_("Contra tu {name}"),
    "moves": N_("Tus movimientos"),
    "moves_probable": N_("Tus movimientos (probables)"),
    "weaknesses": N_("Debilidades"),
    "resistances": N_("Resistencias"),
    "immunities": N_("Inmunidades"),
    "stats": N_("Estadísticas base"),
    "evolution": N_("Evolución"),
}
# Clave CSS del veredicto: sale del enum (texto interno en español), no del texto traducido
VERDICT_KEYS = {Verdict.ADVANTAGE.value: "advantage", Verdict.NEUTRAL.value: "neutral",
                Verdict.DISADVANTAGE.value: "disadvantage"}
LABELS = {"you": N_("Tú"), "them": N_("Él"), "total": N_("Total"),
          "effects": N_("Eficacias")}  # textos fijos de card.js
# Campos de la tarjeta que vacía cada sección oculta (claves de config.CARD_SECTIONS)
HIDDEN_FIELDS = {
    "matchup": (("versus", None),),
    "own_moves": (("moves", None),),
    "eff": (("groups", []), ("ability_lines", [])),
    "stats": (("stats", None),),
    "evo": (("evolution", None),),
}
# Tono de cada grupo de eficacias para el jugador (improve-card-visuals D4)
GROUP_TONES = {"weaknesses": "good", "resistances": "bad", "immunities": "neutral"}


def _type(pokedex: Pokedex, type_id: str | None, lang: str) -> dict:
    fill, border = theme.soft_type_colors(type_id)
    return {
        "id": type_id,
        "label": pokedex.type_name(type_id, lang) if type_id else "?",
        "color": theme.TYPE_COLORS.get(type_id or "", "#555555"),
        "dark": type_id in theme.DARK_TEXT_TYPES,
        "soft": {"background": fill, "border": border},  # pastilla suave (improve-card-visuals D2)
    }


def _tone(factor: float, for_player: bool = True) -> str:
    if factor == 1:
        return "neutral"
    return "good" if (factor > 1) == for_player else "bad"


def _card(
    pokedex: Pokedex,
    view: SpeciesView,
    level: int | None,
    own: SpeciesView | None,
    own_moves: list[Move],
    probable: bool,
    competitive: bool,
    lang: str,
) -> dict:
    type_name = lambda t: pokedex.type_name(t, lang)  # noqa: E731
    chart = pokedex.type_chart(view.generation)
    card: dict = {
        "name": view.name,
        "number": f"#{view.species_id:04d}",
        "level": (_("Nv. {level}", level=level) if level else _("Nv. ?")) if competitive else None,
        "types": [_type(pokedex, t, lang) for t in view.types],
        "capture": None,
        "versus": None,
        "moves": None,
        "groups": [],
        "ability_lines": ability_effect_lines(view, type_name, lang),
        "stats": None,
        "evolution": None,
        "labels": {key: _(text) for key, text in LABELS.items()},
    }
    if view.capture_rate is not None:
        card["capture"] = {"text": _("Captura: {rate} · {difficulty}", rate=view.capture_rate,
                                     difficulty=_(view.capture_difficulty or "")),
                           "color": None if competitive else theme.CAPTURE_COLORS.get(view.capture_difficulty or ""),
                           "meter": None if competitive else round(view.capture_rate / 255, 3)}
    if own is not None:
        m = matchup(own, view, chart)

        def side(pairs, effects, mine):
            return [
                {**_type(pokedex, t, lang),
                 "mult": multiplier_text(x) + ("*" if any(not e.certain for e in effects.get(t, ())) else ""),
                 "tone": _tone(x, mine)}
                for t, x in pairs
            ]

        notes = [matchup_note(e, type_name, lang) for found in (*m.offense_effects.values(), *m.defense_effects.values())
                 for e in found]
        card["versus"] = {
            "title": _(TITLES["versus"], name=m.own_name),
            "verdict": {"label": _(m.verdict.value), "key": VERDICT_KEYS[m.verdict.value]},
            "you": side(m.offense, m.offense_effects, True),
            "them": side(m.defense, m.defense_effects, False),
            "notes": notes,
        }
        if own_moves:
            items = []
            for move in own_moves:
                item = {"name": move.name(lang), "type": _type(pokedex, move.type, lang), "mult": _("Estado"), "tone": "status"}
                if move.category != "status" and move.type:
                    factor, effects = effective_multiplier(chart, move.type, view)
                    item["mult"] = multiplier_text(factor) + ("*" if any(not e.certain for e in effects) else "")
                    item["tone"] = "good" if factor > 1 else "bad" if factor < 1 else "neutral"
                items.append(item)
            card["moves"] = {"title": _(TITLES["moves_probable" if probable else "moves"]), "items": items}
    for key, multipliers in EFFECT_GROUPS:
        if key == "resistances" and not competitive:
            continue
        rows = [{"mult": theme.MULTIPLIER_LABELS[m], "tone": GROUP_TONES[key],
                 "types": [_type(pokedex, t, lang) for t in view.matchups[m]]}
                for m in multipliers if view.matchups[m]]
        if rows:
            card["groups"].append({"title": _(TITLES[key]), "rows": rows})
    if competitive:
        values = [view.stats[k] for k in view.stat_keys]
        highest, lowest = max(values), min(values)
        card["stats"] = {
            "title": _(TITLES["stats"]),
            "rows": [{"label": _(theme.STAT_LABELS[k]), "value": view.stats[k], "max": view.stats[k] == highest,
                      "color": theme.stat_bar_color(view.stats[k], highest, lowest)}
                     for k in view.stat_keys],
            "total": view.stat_total,
        }
    else:
        card["total"] = _("Total estadísticas base: {total}", total=view.stat_total)
    if len(view.evolution) > 1:
        stages = [" / ".join(f"{n} ({c})" if c else n for n, c in stage) for stage in view.evolution]
        card["evolution"] = {
            "title": _(TITLES["evolution"]),
            "text": " → ".join(stages),
            # Por etapas, con la especie mostrada marcada (improve-card-visuals D8)
            "stages": [[{"name": n, "condition": c, "current": n == view.name or view.name.startswith(n + " ")}
                        for n, c in stage] for stage in view.evolution],
        }
    return card


def build_cards(
    pokedex: Pokedex,
    rivals: list[SpeciesView],
    own: SpeciesView | None,
    levels: list[int | None],
    own_moves: list[Move] | None = None,
    probable: bool = False,
    mode: str = "normal",
    lang: str = "es",
    hidden: frozenset[str] = frozenset(),
) -> list[dict]:
    """Una tarjeta por rival, como la ficha privada en el modo de ficha del stream y sin las secciones ocultas."""
    levels = list(levels) + [None] * len(rivals)
    competitive = mode == "competitive"
    cards = [_card(pokedex, view, level, own, list(own_moves or []), probable, competitive, lang)
             for view, level in zip(rivals, levels)]
    for card in cards:
        for section, fields in HIDDEN_FIELDS.items():
            if section in hidden:
                for field, empty in fields:
                    card[field] = empty
    return cards
