"""Nivel leído por la forma de los dígitos de la fuente de GBA (fix del nivel en GBA)."""

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont

from battlelens.core.normalize import extract_level
from battlelens.vision.pixel_level import TEMPLATES, read_pixel_level

L_GLYPH = np.array([[c == "#" for c in row] for row in "#...|#...|#...|#...|#...|#...|####".split("|")])
V_GLYPH = np.array([[c == "#" for c in row] for row in "#.#|#.#|#.#|.#.".split("|")])


def _gba_box(level: int, font: int = 0, scale: int = 4) -> np.ndarray:
    """Caja de combate sintética: nombre, «Lv» y dígitos del patrón, fondo claro y borde oscuro."""
    digits = [TEMPLATES[font * 10 + int(d)][1] for d in str(level)]
    height = max(g.shape[0] for g in digits)
    canvas = np.zeros((height + 8, 80), bool)
    x = 40
    for glyph, top in ((L_GLYPH, height - 7), (V_GLYPH, height - 4), *((d, 0) for d in digits)):
        canvas[4 + top:4 + top + glyph.shape[0], x:x + glyph.shape[1]] = glyph
        x += glyph.shape[1] + 1
    canvas[:4 + 2, :30] = True  # trozo de nombre en la mitad izquierda
    canvas[:, -2:] = True  # borde de la caja
    gray = np.where(canvas, 60, 235).astype(np.uint8).repeat(scale, 0).repeat(scale, 1)
    return np.stack([gray] * 3, axis=-1)


@pytest.mark.parametrize("level", [2, 3, 4, 6, 11, 58, 100])
@pytest.mark.parametrize("font", [0, 1])
def test_digitos_de_gba(level, font):
    assert read_pixel_level(_gba_box(level, font)) == level


def test_texto_claro_sobre_oscuro_no_se_lee():
    assert read_pixel_level(255 - _gba_box(4)) is None


def test_fuente_suavizada_no_da_falsos_positivos():
    img = Image.new("RGB", (240, 40), (235, 235, 235))
    ImageDraw.Draw(img).text((10, 5), "Machop Nv. 16", fill=(40, 40, 40), font=ImageFont.load_default(size=24))
    assert read_pixel_level(np.asarray(img)) is None


def test_texto_con_digitos_manda_sobre_la_forma_y_la_forma_sobre_las_confusiones():
    assert extract_level(["Pidgey Lu3"], pixel_level=5) == 3
    assert extract_level(["Sp i narak LVII"], pixel_level=4) == 4
    assert extract_level(["Froak i e, LUS"], pixel_level=None) == 5
