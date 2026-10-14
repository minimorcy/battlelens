"""Presets por juego: regiones del rival, de tu Pokémon y del menú de ataques en fracciones de la imagen
del juego (add-game-presets D1).

Medidas sobre capturas de referencia (capturas-presets/, fuera del repositorio) y holgadas a propósito:
el lector tolera texto de más y un recuadro holgado aguanta las diferencias entre emuladores. El
asistente obliga a confirmarlas a ojo antes de guardar el perfil.
"""

from __future__ import annotations

from dataclasses import dataclass

from .profiles import Region

GAME_BOY = 160 / 144
GBA = 240 / 160
DS_SCREEN = 256 / 192
SWITCH = 16 / 9

Box = tuple[float, float, float, float]  # x, y, ancho, alto en fracciones de la imagen del juego


@dataclass(frozen=True)
class Preset:
    id: str
    games: tuple[str, ...]
    aspect: float
    regions: dict[str, Box]
    ds: bool = False  # las regiones son de la pantalla superior


PRESETS: tuple[Preset, ...] = (
    Preset(
        "gb-gen12",
        ("red-blue", "yellow", "gold-silver", "crystal"),
        GAME_BOY,
        # Rejilla de 8 px: nombre del rival en la fila 0 (toca el borde superior) y nivel debajo; el tuyo a la derecha
        {"rival": (0.0, 0.0, 0.62, 0.115), "own": (0.45, 0.375, 0.55, 0.135)},
    ),
    Preset(
        "gba-gen3",
        ("ruby-sapphire", "emerald", "firered-leafgreen"),
        GBA,
        {"rival": (0.03, 0.07, 0.49, 0.15), "own": (0.53, 0.43, 0.46, 0.15), "moves": (0.02, 0.76, 0.63, 0.22)},
    ),
    Preset(
        "ds-gen4",
        ("diamond-pearl", "platinum", "heartgold-soulsilver"),
        DS_SCREEN,
        {"rival": (0.0, 0.04, 0.52, 0.17), "own": (0.53, 0.48, 0.47, 0.15)},
        ds=True,
    ),
    Preset(
        "ds-gen5",
        ("black-white", "black-2-white-2"),
        DS_SCREEN,
        {"rival": (0.0, 0.10, 0.55, 0.15), "own": (0.50, 0.55, 0.50, 0.15)},
        ds=True,
    ),
    Preset(
        "switch-swsh",
        ("sword-shield",),
        SWITCH,
        {"rival": (0.72, 0.01, 0.275, 0.10), "own": (0.0, 0.85, 0.25, 0.08), "moves": (0.79, 0.54, 0.21, 0.44)},
    ),
)
_BY_GAME = {game: preset for preset in PRESETS for game in preset.games}


def preset_for(game_id: str | None) -> Preset | None:
    return _BY_GAME.get(game_id or "")


def games_with_presets() -> tuple[str, ...]:
    return tuple(_BY_GAME)


def region_pixels(box: Box, viewport) -> tuple[int, int, int, int]:
    """Rectángulo en píxeles del área cliente de una región del preset dentro del viewport."""
    x, y, w, h = box
    return (round(viewport.x + x * viewport.width), round(viewport.y + y * viewport.height),
            round(w * viewport.width), round(h * viewport.height))


def to_profile_regions(preset: Preset, viewport, client_w: int, client_h: int) -> dict[str, Region]:
    """Regiones del preset convertidas a fracciones del área cliente (como las de un perfil calibrado)."""
    regions = {}
    for role, box in preset.regions.items():
        x, y, w, h = region_pixels(box, viewport)
        x, y = max(0, x), max(0, y)
        w, h = min(w, client_w - x), min(h, client_h - y)
        regions[role] = Region(round(x / client_w, 6), round(y / client_h, 6), round(w / client_w, 6), round(h / client_h, 6))
    return regions
