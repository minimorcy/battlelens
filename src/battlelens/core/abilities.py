"""Habilidades que cambian la eficacia de los ataques recibidos (add-ability-aware-matchups D1)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..i18n import get_language, N_, _

if TYPE_CHECKING:
    from .pokedex import Ability

# Multiplicador que aplica cada habilidad a los ataques de un tipo. Notas especiales en `ABILITY_NOTES`.
ABILITY_TYPE_EFFECTS: dict[str, dict[str, float]] = {
    "levitate": {"ground": 0.0},
    "earth-eater": {"ground": 0.0},
    "flash-fire": {"fire": 0.0},
    "well-baked-body": {"fire": 0.0},
    "water-absorb": {"water": 0.0},
    "storm-drain": {"water": 0.0},
    "dry-skin": {"water": 0.0, "fire": 1.25},
    "volt-absorb": {"electric": 0.0},
    "lightning-rod": {"electric": 0.0},
    "motor-drive": {"electric": 0.0},
    "sap-sipper": {"grass": 0.0},
    "heatproof": {"fire": 0.5},
    "water-bubble": {"fire": 0.5},
    "thick-fat": {"fire": 0.5, "ice": 0.5},
    "purifying-salt": {"ghost": 0.5},
    "fluffy": {"fire": 2.0},
}
WONDER_GUARD = "wonder-guard"
SUPER_EFFECTIVE_REDUCERS = frozenset({"filter", "solid-rock", "prism-armor"})
SUPER_EFFECTIVE_REDUCTION = 0.75
ABILITY_NOTES: dict[str, str] = {
    WONDER_GUARD: N_("Solo le afectan los ataques supereficaces"),
    "filter": N_("Los supereficaces le hacen ×0,75"),
    "solid-rock": N_("Los supereficaces le hacen ×0,75"),
    "prism-armor": N_("Los supereficaces le hacen ×0,75"),
}
_MULTIPLIER_TEXT = {0.0: "×0", 0.25: "×¼", 0.5: "×½", 1.0: "×1", 2.0: "×2", 4.0: "×4"}


def multiplier_text(factor: float) -> str:
    text = _MULTIPLIER_TEXT.get(factor) or f"×{factor:g}"
    return text.replace(".", ",") if get_language() == "es" else text


def ability_effects(identifier: str, type_name) -> list[str]:
    """Textos como «Tierra ×0» para una habilidad; `type_name(tipo)` traduce el tipo."""
    effects = [f"{type_name(t)} {multiplier_text(m)}" for t, m in ABILITY_TYPE_EFFECTS.get(identifier, {}).items()]
    if identifier in ABILITY_NOTES:
        effects.append(_(ABILITY_NOTES[identifier]))
    return effects


def affects_typing(identifier: str) -> bool:
    return identifier in ABILITY_TYPE_EFFECTS or identifier in ABILITY_NOTES


def adjusted_factor(identifier: str, attacking: str, factor: float) -> float:
    """Multiplicador de un ataque de tipo `attacking` tras aplicar la habilidad del que lo recibe."""
    if identifier == WONDER_GUARD:
        return factor if factor > 1 else 0.0
    if identifier in SUPER_EFFECTIVE_REDUCERS:
        return factor * SUPER_EFFECTIVE_REDUCTION if factor > 1 else factor
    return factor * ABILITY_TYPE_EFFECTS.get(identifier, {}).get(attacking, 1.0)


@dataclass(frozen=True)
class AbilityEffect:
    """Cambio de eficacia de un tipo de ataque por una o varias habilidades del que lo recibe."""

    type: str
    base: float  # multiplicador solo por tipos
    factor: float  # multiplicador con la habilidad
    abilities: tuple[Ability, ...]
    certain: bool  # todas sus habilidades posibles lo provocan


def resolve(abilities, attacking: str, base: float) -> tuple[float, tuple[AbilityEffect, ...]]:
    """(multiplicador seguro, efectos) de un tipo de ataque contra un Pokémon con esas habilidades posibles.

    Seguro: todas las habilidades dan el mismo valor, distinto del de los tipos. Posible: solo algunas lo
    cambian; entonces el multiplicador sigue siendo el de los tipos y hay un efecto por cada valor distinto.
    """
    abilities = tuple(abilities)
    if not abilities:
        return base, ()
    outcomes = [(a, adjusted_factor(a.identifier, attacking, base)) for a in abilities]
    values = {f for _, f in outcomes}
    if len(values) == 1:
        (factor,) = values
        if factor == base:
            return base, ()
        return factor, (AbilityEffect(attacking, base, factor, abilities, True),)
    effects = []
    for value in sorted(values - {base}):
        causes = tuple(a for a, f in outcomes if f == value)
        effects.append(AbilityEffect(attacking, base, value, causes, False))
    return base, tuple(effects)
