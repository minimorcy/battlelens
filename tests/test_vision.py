import sys

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont

from pokemon_stats_live.core.profiles import Region
from pokemon_stats_live.vision.preprocess import (
    PADDING_PX,
    VARIANT_HEIGHTS,
    crop_region,
    preprocess,
    preprocess_variants,
)


def _text_image(text: str, fg, bg, size=(120, 24), font_size=16) -> np.ndarray:
    img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()
    draw.text((4, 2), text, fill=fg, font=font)
    return np.array(img)


def _text_is_dark(binary: np.ndarray) -> bool:
    return np.count_nonzero(binary == 0) < np.count_nonzero(binary == 255)


def test_texto_claro_sobre_oscuro_se_invierte():
    out = preprocess(_text_image("PIDGEY", fg=(255, 255, 255), bg=(20, 20, 40)))
    assert _text_is_dark(out)
    assert set(np.unique(out)) <= {0, 255}


def test_texto_oscuro_sobre_claro_se_mantiene():
    out = preprocess(_text_image("PIDGEY", fg=(30, 30, 30), bg=(248, 248, 216)))
    assert _text_is_dark(out)


def test_variantes_normalizan_altura_sin_interpolar():
    crop = _text_image("AB", fg=(0, 0, 0), bg=(255, 255, 255), size=(40, 16), font_size=12)
    variants = preprocess_variants(crop)
    assert len(variants) == 2 * len(VARIANT_HEIGHTS)
    heights = sorted({v.shape[0] - 2 * PADDING_PX for v in variants})
    assert heights == sorted(VARIANT_HEIGHTS)
    sharp = [preprocess(crop, h, 0.0) for h in VARIANT_HEIGHTS]
    assert all(set(np.unique(v)) <= {0, 255} for v in sharp)  # bordes nítidos sin desenfoque


def test_recorte_por_region_relativa():
    image = np.zeros((640, 960, 3), dtype=np.uint8)
    image[40:64, 480:640] = 255
    crop = crop_region(image, Region.from_pixels(480, 40, 160, 24, 960, 640))
    assert crop.shape == (24, 160, 3)
    assert crop.min() == 255

    big = np.zeros((960, 1440, 3), dtype=np.uint8)
    assert crop_region(big, Region.from_pixels(480, 40, 160, 24, 960, 640)).shape == (36, 240, 3)


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="OCR nativo de Windows")
@pytest.mark.parametrize("colors", [((0, 0, 0), (255, 255, 255)), ((255, 255, 255), (40, 40, 80))])
def test_ocr_de_extremo_a_extremo(colors):
    from pokemon_stats_live.core.matcher import NameMatcher
    from pokemon_stats_live.core.pokedex import Pokedex
    from pokemon_stats_live.platform.ocr import recognize

    fg, bg = colors
    matcher = NameMatcher(Pokedex.load())
    crop = _text_image("PIDGEY", fg=fg, bg=bg)
    results = [matcher.match(recognize(v, ("es", "en")).text) for v in preprocess_variants(crop)]
    best = max(results, key=lambda r: r.score)
    assert best.species_id == 16, [r.raw_text for r in results]
