"""Comparativa de tipos entre tu Pokémon y un rival (spec type-matchup)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .abilities import AbilityEffect
from .pokedex import SpeciesView


class Verdict(Enum):
    ADVANTAGE = "Ventaja"
    NEUTRAL = "Neutral"
    DISADVANTAGE = "Desventaja"


@dataclass(frozen=True)
class Matchup:
    own_name: str
    offense: tuple[tuple[str, float], ...]  # tus tipos → multiplicador contra el rival
    defense: tuple[tuple[str, float], ...]  # tipos del rival → multiplicador contra ti
    verdict: Verdict
    # Efectos de habilidades por tipo de ataque: los del rival en tus ataques, los tuyos en los suyos
    offense_effects: dict[str, tuple[AbilityEffect, ...]] = field(default_factory=dict)
    defense_effects: dict[str, tuple[AbilityEffect, ...]] = field(default_factory=dict)


def _multiplier(chart: dict[str, dict[str, float]], attacking: str, defending: tuple[str, ...]) -> float:
    factor = 1.0
    for t in defending:
        factor *= chart.get(attacking, {}).get(t, 1.0)
    return factor


def effective_multiplier(
    chart: dict[str, dict[str, float]], attacking: str, target: SpeciesView
) -> tuple[float, tuple[AbilityEffect, ...]]:
    """Multiplicador contra `target` con sus habilidades seguras, y sus efectos sobre ese tipo (D4)."""
    effects = target.effects_against(attacking)
    certain = next((e for e in effects if e.certain), None)
    return (certain.factor if certain else _multiplier(chart, attacking, target.types)), effects


def _side(chart, attacking_types, target: SpeciesView):
    pairs, effects = [], {}
    for t in attacking_types:
        factor, found = effective_multiplier(chart, t, target)
        pairs.append((t, factor))
        if found:
            effects[t] = found
    return tuple(pairs), effects


def matchup(own: SpeciesView, rival: SpeciesView, chart: dict[str, dict[str, float]]) -> Matchup:
    offense, offense_effects = _side(chart, own.types, rival)
    defense, defense_effects = _side(chart, rival.types, own)
    best_own = max(m for _, m in offense)
    best_rival = max(m for _, m in defense)
    if best_own > best_rival:
        verdict = Verdict.ADVANTAGE
    elif best_own < best_rival:
        verdict = Verdict.DISADVANTAGE
    else:
        verdict = Verdict.NEUTRAL
    return Matchup(own.name, offense, defense, verdict, offense_effects, defense_effects)
