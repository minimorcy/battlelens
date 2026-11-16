"""Nivel leído comparando los dígitos con los de la fuente de los juegos de GBA.

El OCR de Windows no lee bien los dígitos pixelados de GBA (lee «Lv4» como «LVII» y el 6 como «S»),
así que el número que va tras «Lv» se separa en dígitos y cada uno se compara con los patrones de
las dos fuentes de Gen III (pequeña y normal). Solo se acepta un dígito casi idéntico a su patrón.
"""

from __future__ import annotations

import numpy as np
from PIL import Image

from .preprocess import LEVEL_PORTION, otsu_threshold, to_gray

# Dígitos 0-9 de las fuentes latin_small y latin_normal de Gen III (# = tinta)
_FONTS = (
    ('.##.|#..#|#..#|#..#|#..#|#..#|.##.', '.#.|##.|.#.|.#.|.#.|.#.|###', '.##.|#..#|...#|..#.|.#..|#...|####',
     '.##.|#..#|...#|.##.|...#|#..#|.##.', '.##.|#.#.|#.#.|#.#.|#.#.|####|..#.', '####|#...|#...|###.|...#|#..#|.##.',
     '.##.|#..#|#...|###.|#..#|#..#|.##.', '####|...#|...#|..#.|..#.|.#..|.#..', '.##.|#..#|#..#|.##.|#..#|#..#|.##.',
     '.##.|#..#|#..#|.###|...#|#..#|.##.'),
    ('.###.|#...#|#...#|#...#|#...#|#...#|#...#|#...#|.###.', '##.|.#.|.#.|.#.|.#.|.#.|.#.|.#.|###',
     '.###.|#...#|....#|....#|...#.|..#..|.#...|#....|#####', '.###.|#...#|....#|....#|..##.|....#|....#|#...#|.###.',
     '..##.|.#.#.|#..#.|#..#.|#..#.|#..#.|#####|...#.|...#.', '#####|#....|#....|#....|####.|....#|....#|....#|####.',
     '.###.|#...#|#....|#....|####.|#...#|#...#|#...#|.###.', '#####|....#|....#|....#|...#.|...#.|...#.|..#..|..#..',
     '.###.|#...#|#...#|#...#|.###.|#...#|#...#|#...#|.###.', '.###.|#...#|#...#|#...#|.####|....#|....#|#...#|.###.'),
)
TEMPLATES = [(digit, np.array([[c == "#" for c in row] for row in pattern.split("|")]))
             for font in _FONTS for digit, pattern in enumerate(font)]
MAX_ERROR = 0.1  # fracción de celdas distintas del patrón; 0,1 = 2-4 celdas según la fuente
MIN_BAND_ROWS = 7  # una fila de texto de GBA mide al menos 7 px


def _runs(mask: np.ndarray) -> list[tuple[int, int]]:
    """Tramos [inicio, fin) donde `mask` es cierto."""
    edges = np.diff(np.concatenate(([0], mask.astype(np.int8), [0])))
    return list(zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)))


def match_digit(glyph: np.ndarray) -> int | None:
    """Dígito cuyo patrón coincide con `glyph` (máscara de tinta recortada a su contorno), o None."""
    h, w = glyph.shape
    best: tuple[float, int] | None = None
    for digit, template in TEMPLATES:
        th, tw = template.shape
        if abs(w / h - tw / th) > 0.25:
            continue
        cells = np.asarray(Image.fromarray(glyph.astype(np.uint8) * 255).resize((tw, th), Image.Resampling.BOX)) > 127
        error = float(np.mean(cells != template))
        if best is None or error < best[0]:
            best = (error, digit)
    return best[1] if best is not None and best[0] <= MAX_ERROR else None


def read_pixel_level(crop: np.ndarray) -> int | None:
    """Nivel (1-100) de los dígitos con los que acaba la fila de texto, o None si no son de la fuente de GBA."""
    right = to_gray(crop[:, int(crop.shape[1] * (1 - LEVEL_PORTION)):])
    if right.size == 0:
        return None
    ink = right <= otsu_threshold(right)
    if ink.mean() > 0.5:  # texto claro sobre fondo oscuro: no es la caja de combate de GBA
        return None
    band = max(_runs(ink.mean(axis=1) < 0.5), key=lambda r: r[1] - r[0], default=None)
    if band is None or band[1] - band[0] < MIN_BAND_ROWS:
        return None
    ink = ink[band[0]:band[1]].copy()
    ink[:, ink.mean(axis=0) > 0.85] = False  # bordes de la caja
    glyphs = []
    for x0, x1 in _runs(ink.any(axis=0)):
        rows = np.flatnonzero(ink[:, x0:x1].any(axis=1))
        if rows[-1] - rows[0] + 1 < 0.8 * ink.shape[0]:  # lo que ocupa toda la franja es el borde inclinado
            glyphs.append(ink[rows[0]:rows[-1] + 1, x0:x1])
    if not glyphs:
        return None
    full = max(g.shape[0] for g in glyphs)
    digits: list[int] = []
    for glyph in reversed(glyphs):  # de derecha a izquierda hasta la «v» de «Lv», que es más baja
        digit = match_digit(glyph) if glyph.shape[0] >= 0.8 * full else None
        if digit is None:
            break
        digits.insert(0, digit)
    if not 1 <= len(digits) <= 3:
        return None
    value = int("".join(map(str, digits)))
    return value if 1 <= value <= 100 else None
