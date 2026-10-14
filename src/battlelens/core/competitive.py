"""Cálculos del modo competitivo (spec competitive-data): estadísticas a un nivel, velocidad,
habilidades que cambian la eficacia y datos de entrenamiento."""

from __future__ import annotations

import math
from enum import Enum

from ..i18n import N_
from .abilities import ABILITY_NOTES, ABILITY_TYPE_EFFECTS, ability_effects  # noqa: F401 (reexportadas)
from .pokedex import STAT_DISPLAY_ORDER, SpeciesView

SHEDINJA = "shedinja"
LETS_GO = "lets-go-pikachu-lets-go-eevee"
LEGENDS_ARCEUS = "legends-arceus"
LETS_GO_MAX_AV = 200
GEN12_MAX_DV = 15
GEN12_MAX_EXP_TERM = 64  # ⌊⌈√65535⌉ / 4⌋
# Multiplicador del bonus por nivel de esfuerzo 0-10 en Leyendas: Arceus
ARCEUS_EFFORT_MULTIPLIER = (0, 2, 3, 4, 7, 8, 9, 14, 15, 16, 25)


def stat_value(stat: str, base: int, level: int, iv: int, ev: int, nature: float) -> int:
    """Fórmula de la Gen 3 en adelante (add-display-modes D5)."""
    core = math.floor((2 * base + iv + ev // 4) * level / 100)
    if stat == "hp":
        return core + level + 10
    return math.floor((core + 5) * nature)


def gen12_stat_value(stat: str, base: int, level: int, dv: int, exp_term: int) -> int:
    """Gen 1-2: DV 0-15 y ⌊⌈√experiencia⌉ / 4⌋ (0-64), sin naturaleza (add-generation-stats D4)."""
    core = ((base + dv) * 2 + exp_term) * level // 100
    return core + level + 10 if stat == "hp" else core + 5


def lets_go_stat_value(stat: str, base: int, level: int, iv: int, av: int, nature10: int, friendship10: int) -> int:
    """Let's Go: naturaleza y amistad en décimas (9-11 y 10-11) y AVs sumados al final."""
    core = (2 * base + iv) * level // 100
    if stat == "hp":
        return core + level + 10 + av
    return (core + 5) * nature10 // 10 * friendship10 // 10 + av


def arceus_stat_value(stat: str, base: int, level: int, effort_level: int, nature10: int) -> int:
    """Leyendas: Arceus: nivel de esfuerzo 0-10 y naturaleza en décimas."""
    bonus = math.floor((math.sqrt(base) * ARCEUS_EFFORT_MULTIPLIER[effort_level] + level) / 2.5)
    if stat == "hp":
        return (level + 100) * base // 100 + level + bonus
    return (level + 50) * base // 75 * nature10 // 10 + bonus


def stat_formula(game_id: str | None, generation: int | None) -> str:
    if game_id == LETS_GO:
        return "lets-go"
    if game_id == LEGENDS_ARCEUS:
        return "legends-arceus"
    if generation is not None and generation <= 2:
        return "gen12"
    return "modern"


def stat_ranges(
    stats: dict[str, int], level: int, pokemon: str | None = None, formula: str = "modern", own: bool = False
) -> dict[str, tuple[int, int]]:
    """Mínimo y máximo de cada estadística con la fórmula del juego (spec competitive-data).

    Moderna: IV 0/EV 0/naturaleza desfavorable frente a IV 31/EV 252/favorable. Let's Go: los AVs solo
    cuentan para tu Pokémon (`own`), porque los rivales no tienen.
    """
    ranges = {}
    for stat in (k for k in STAT_DISPLAY_ORDER if k in stats):
        base = stats[stat]
        if stat == "hp" and pokemon == SHEDINJA:
            ranges[stat] = (1, 1)
        elif formula == "gen12":
            ranges[stat] = (gen12_stat_value(stat, base, level, 0, 0),
                            gen12_stat_value(stat, base, level, GEN12_MAX_DV, GEN12_MAX_EXP_TERM))
        elif formula == "lets-go":
            ranges[stat] = (lets_go_stat_value(stat, base, level, 0, 0, 9, 10),
                            lets_go_stat_value(stat, base, level, 31, LETS_GO_MAX_AV if own else 0, 11, 11))
        elif formula == "legends-arceus":
            ranges[stat] = (arceus_stat_value(stat, base, level, 0, 9),
                            arceus_stat_value(stat, base, level, len(ARCEUS_EFFORT_MULTIPLIER) - 1, 11))
        else:
            ranges[stat] = (stat_value(stat, base, level, 0, 0, 0.9), stat_value(stat, base, level, 31, 252, 1.1))
    return ranges


def view_ranges(view: SpeciesView, level: int, own: bool = False) -> dict[str, tuple[int, int]]:
    """Rangos de una vista con la fórmula de su juego (add-generation-stats D5)."""
    return stat_ranges(view.stats, level, view.pokemon, stat_formula(view.game_id, view.generation), own)


class SpeedVerdict(Enum):
    FASTER = N_("Eres más rápido")
    SLOWER = N_("Es más rápido")
    DEPENDS = N_("Depende de IVs/EVs")


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
    atk = stats["attack"]
    spa = stats.get("special_attack", stats.get("special", 0))
    spd = stats.get("special_defense", stats.get("special", 0))
    if atk - spa >= 20:
        profile.append(N_("Atacante físico"))
    elif spa - atk >= 20:
        profile.append(N_("Atacante especial"))
    else:
        profile.append(N_("Atacante mixto"))
    bulk = stats["hp"] + stats["defense"] + spd
    if bulk - (atk + spa + stats["speed"]) >= 40:
        profile.append(N_("defensivo"))
    if stats["speed"] >= 100:
        profile.append(N_("rápido"))
    return profile
