"""Comparativa de tipos entre tu Pokémon y un rival (spec type-matchup)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

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


def _multiplier(chart: dict[str, dict[str, float]], attacking: str, defending: tuple[str, ...]) -> float:
    factor = 1.0
    for t in defending:
        factor *= chart.get(attacking, {}).get(t, 1.0)
    return factor


def matchup(own: SpeciesView, rival: SpeciesView, chart: dict[str, dict[str, float]]) -> Matchup:
    offense = tuple((t, _multiplier(chart, t, rival.types)) for t in own.types)
    defense = tuple((t, _multiplier(chart, t, own.types)) for t in rival.types)
    best_own = max(m for _, m in offense)
    best_rival = max(m for _, m in defense)
    if best_own > best_rival:
        verdict = Verdict.ADVANTAGE
    elif best_own < best_rival:
        verdict = Verdict.DISADVANTAGE
    else:
        verdict = Verdict.NEUTRAL
    return Matchup(own.name, offense, defense, verdict)
