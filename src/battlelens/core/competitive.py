"""Cálculos del modo competitivo (spec competitive-data): estadísticas a un nivel, velocidad,
habilidades que cambian la eficacia y datos de entrenamiento."""

from __future__ import annotations

import math
from enum import Enum

from .abilities import ABILITY_NOTES, ABILITY_TYPE_EFFECTS, ability_effects  # noqa: F401 (reexportadas)
from .pokedex import STAT_ORDER

SHEDINJA = "shedinja"


def stat_value(stat: str, base: int, level: int, iv: int, ev: int, nature: float) -> int:
    """Fórmula de la Gen 3 en adelante (add-display-modes D5)."""
    core = math.floor((2 * base + iv + ev // 4) * level / 100)
    if stat == "hp":
        return core + level + 10
    return math.floor((core + 5) * nature)


def stat_ranges(stats: dict[str, int], level: int, pokemon: str | None = None) -> dict[str, tuple[int, int]]:
    """Mínimo (IV 0, EV 0, naturaleza desfavorable) y máximo (IV 31, EV 252, favorable) de cada estadística."""
    ranges = {}
    for stat in STAT_ORDER:
        if stat == "hp" and pokemon == SHEDINJA:
            ranges[stat] = (1, 1)
            continue
        low = stat_value(stat, stats[stat], level, 0, 0, 0.9)
        high = stat_value(stat, stats[stat], level, 31, 252, 1.1)
        ranges[stat] = (low, high)
    return ranges


class SpeedVerdict(Enum):
    FASTER = "Eres más rápido"
    SLOWER = "Es más rápido"
    DEPENDS = "Depende de IVs/EVs"


def compare_speed(own: tuple[int, int], rival: tuple[int, int]) -> SpeedVerdict:
    if own[0] > rival[1]:
        return SpeedVerdict.FASTER
    if rival[0] > own[1]:
        return SpeedVerdict.SLOWER
    return SpeedVerdict.DEPENDS


def weight_move_power(weight_kg: float | None) -> int | None:
    """Potencia de Patada Baja y Hierba Lazo contra un Pokémon de ese peso."""
    if weight_kg is None:
        return None
    for limit, power in ((10, 20), (25, 40), (50, 60), (100, 80), (200, 100)):
        if weight_kg < limit:
            return power
    return 120


def stat_profile(stats: dict[str, int]) -> list[str]:
    profile = []
    atk, spa = stats["attack"], stats["special_attack"]
    if atk - spa >= 20:
        profile.append("Atacante físico")
    elif spa - atk >= 20:
        profile.append("Atacante especial")
    else:
        profile.append("Atacante mixto")
    bulk = stats["hp"] + stats["defense"] + stats["special_defense"]
    if bulk - (atk + spa + stats["speed"]) >= 40:
        profile.append("defensivo")
    if stats["speed"] >= 100:
        profile.append("rápido")
    return profile
