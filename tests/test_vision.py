import sys

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont

from battlelens.core.profiles import Region
from battlelens.vision.preprocess import (
    GRAY_HEIGHTS,
    PADDING_PX,
    VARIANT_HEIGHTS,
    crop_region,
    otsu_threshold,
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
    assert len(variants) == 1 + len(GRAY_HEIGHTS) + 2 * len(VARIANT_HEIGHTS)
    assert variants[0].shape == crop.shape  # la primera es el recorte original
    binarized = variants[1 + len(GRAY_HEIGHTS):]
    assert sorted({v.shape[0] - 2 * PADDING_PX for v in binarized}) == sorted(VARIANT_HEIGHTS)
    gray = variants[1 : 1 + len(GRAY_HEIGHTS)]
    assert [v.shape[0] - 2 * PADDING_PX for v in gray] == list(GRAY_HEIGHTS)
    sharp = [preprocess(crop, h, 0.0) for h in VARIANT_HEIGHTS]
    assert all(set(np.unique(v)) <= {0, 255} for v in sharp)  # bordes nítidos sin desenfoque


def test_otsu_separa_histograma_bimodal():
    gray = np.concatenate([np.full(600, 40), np.full(400, 200)]).astype(np.uint8).reshape(25, 40)
    t = otsu_threshold(gray)
    assert 40 <= t < 200
    noisy = np.clip(gray.astype(int) + np.random.default_rng(0).integers(-15, 16, gray.shape), 0, 255).astype(np.uint8)
    t2 = otsu_threshold(noisy)
    assert 55 <= t2 < 185


def test_region_holgada_con_fondo_mixto(requires_ocr):
    """Caja clara con el nombre sobre un fondo de hierba texturizado (caso real de Pokémon Espada)."""
    from battlelens.core.matcher import NameMatcher
    from battlelens.core.pokedex import Pokedex
    from battlelens.pipeline import read_crop
    from battlelens.platform.ocr import recognize

    rng = np.random.default_rng(1)
    grass = np.stack([rng.integers(40, 90, (120, 320)), rng.integers(110, 170, (120, 320)), rng.integers(30, 70, (120, 320))], axis=2)
    img = Image.fromarray(grass.astype(np.uint8))
    draw = ImageDraw.Draw(img)
    draw.polygon([(60, 25), (320, 25), (320, 90), (40, 90)], fill=(250, 250, 250))
    font = ImageFont.truetype("arial.ttf", 22)
    draw.text((95, 32), "Stufful", fill=(30, 30, 30), font=font)
    draw.text((240, 32), "Nv. 10", fill=(30, 30, 30), font=font)
    draw.rectangle((95, 66, 300, 74), fill=(20, 220, 20))
    reading = read_crop(np.array(img), recognize, NameMatcher(Pokedex.load()), ("es", "en"))
    assert reading.match.species_id == 759, reading.readings


def test_otsu_imagen_uniforme_no_falla():
    assert 0 <= otsu_threshold(np.full((10, 10), 128, dtype=np.uint8)) <= 255


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
def test_ocr_de_extremo_a_extremo(colors, requires_ocr):
    from battlelens.core.matcher import NameMatcher
    from battlelens.core.pokedex import Pokedex
    from battlelens.platform.ocr import recognize

    fg, bg = colors
    matcher = NameMatcher(Pokedex.load())
    crop = _text_image("PIDGEY", fg=fg, bg=bg)
    results = [matcher.match(recognize(v, ("es", "en")).text) for v in preprocess_variants(crop)]
    best = max(results, key=lambda r: r.score)
    assert best.species_id == 16, [r.raw_text for r in results]
