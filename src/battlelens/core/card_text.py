"""Textos de la ficha que comparten la ventana privada y la fuente para OBS (add-stream-mode D3)."""

from __future__ import annotations

from typing import Callable

from ..i18n import _
from .abilities import ABILITY_NOTES, AbilityEffect, multiplier_text
from .pokedex import SpeciesView

TypeName = Callable[[str], str]


def ability_names(effect: AbilityEffect, lang: str) -> str:
    return " / ".join(a.name(lang) for a in effect.abilities)


def matchup_note(effect: AbilityEffect, type_name: TypeName, lang: str) -> str:
    """«Tierra: ×0 por Levitación» (seguro) o «Tierra: ×0 si tiene Levitación» (posible)."""
    fields = {"type": type_name(effect.type), "mult": multiplier_text(effect.factor),
              "abilities": ability_names(effect, lang)}
    if effect.certain:
        return _("{type}: {mult} por {abilities}", **fields)
    return _("{type}: {mult} si tiene {abilities}", **fields)


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
        detail = _(note) if note else ", ".join(f"{type_name(e.type)} {multiplier_text(e.factor)}" for e in effects)
        if certain:
            lines.append(_("{abilities}: {detail}", abilities=names, detail=detail))
        else:
            lines.append(_("Si tiene {abilities}: {detail}", abilities=names, detail=detail))
    return lines
