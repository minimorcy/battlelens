"""Cálculos del modo competitivo (spec competitive-data): estadísticas a un nivel, velocidad,
habilidades que cambian la eficacia y datos de entrenamiento."""

from __future__ import annotations

import math
from enum import Enum

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


# Habilidades que cambian la eficacia de los ataques recibidos (D6). Notas especiales en `ABILITY_NOTES`.
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
ABILITY_NOTES: dict[str, str] = {
    "wonder-guard": "Solo le afectan los ataques supereficaces",
    "filter": "Los supereficaces le hacen ×0,75",
    "solid-rock": "Los supereficaces le hacen ×0,75",
    "prism-armor": "Los supereficaces le hacen ×0,75",
}
_MULTIPLIER_TEXT = {0.0: "×0", 0.5: "×½", 1.25: "×1,25", 2.0: "×2"}


def ability_effects(identifier: str, type_name) -> list[str]:
    """Textos como «Tierra ×0» para una habilidad; `type_name(tipo)` traduce el tipo."""
    effects = [f"{type_name(t)} {_MULTIPLIER_TEXT.get(m, f'×{m}')}" for t, m in ABILITY_TYPE_EFFECTS.get(identifier, {}).items()]
    if identifier in ABILITY_NOTES:
        effects.append(ABILITY_NOTES[identifier])
    return effects


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
