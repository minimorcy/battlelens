"""Textos de la ficha que comparten la ventana privada y la fuente para OBS (add-stream-mode D3)."""

from __future__ import annotations

from typing import Callable

from .abilities import ABILITY_NOTES, AbilityEffect, multiplier_text
from .pokedex import SpeciesView

TypeName = Callable[[str], str]


def ability_names(effect: AbilityEffect, lang: str) -> str:
    return " / ".join(a.name(lang) for a in effect.abilities)


def matchup_note(effect: AbilityEffect, type_name: TypeName, lang: str) -> str:
    """«Tierra: ×0 por Levitación» (seguro) o «Tierra: ×0 si tiene Levitación» (posible)."""
    link = "por" if effect.certain else "si tiene"
    return f"{type_name(effect.type)}: {multiplier_text(effect.factor)} {link} {ability_names(effect, lang)}"


def ability_effect_lines(view: SpeciesView, type_name: TypeName, lang: str) -> list[str]:
    """Una línea por habilidad: «Levitación: Tierra ×0» o «Si tiene Levitación: Tierra ×0»."""
    grouped: dict[tuple[bool, tuple[str, ...]], list[AbilityEffect]] = {}
    for effect in view.ability_effects:
        key = (effect.certain, tuple(a.identifier for a in effect.abilities))
        grouped.setdefault(key, []).append(effect)
    lines = []
    for (certain, identifiers), effects in grouped.items():
        names = ability_names(effects[0], lang)
        note = next((ABILITY_NOTES[i] for i in identifiers if i in ABILITY_NOTES), None)
        detail = note or ", ".join(f"{type_name(e.type)} {multiplier_text(e.factor)}" for e in effects)
        lines.append(f"{names}: {detail}" if certain else f"Si tiene {names}: {detail}")
    return lines
