"""Banco de pruebas de precisión del OCR con nombres pixelados sintéticos de estilo GBA.

Referencia (design.md D6 de add-battle-overlay-mvp): 35/36 con OpenCV. Umbral de aceptación: ≥ 34/36.
"""

import sys

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont

pytestmark = [pytest.mark.windows, pytest.mark.skipif(sys.platform != "win32", reason="OCR nativo de Windows")]

NAMES = [
    "ZIGZAGOON", "POOCHYENA", "WURMPLE", "TAILLOW", "GEODUDE", "TENTACOOL",
    "PIDGEY", "RATTATA", "MACHOP", "WINGULL", "NIDORAN♀", "MAKUHITA",
]
# (tamaño de fuente, escala del emulador)
RENDERINGS = [(10, 3), (10, 2), (11, 3)]
MIN_CORRECT = 34


def _pixel_crop(name: str, font_size: int, scale: int) -> np.ndarray:
    img = Image.new("RGB", (70, 13), (248, 248, 216))
    draw = ImageDraw.Draw(img)
    draw.fontmode = "1"  # sin antialias, como una fuente bitmap
    draw.text((2, 1), name, fill=(64, 64, 64), font=ImageFont.truetype("consola.ttf", font_size))
    return np.array(img.resize((70 * scale, 13 * scale), Image.NEAREST))


def test_precision_ocr(requires_ocr):
    from battlelens.core.matcher import NameMatcher
    from battlelens.core.pokedex import Pokedex
    from battlelens.pipeline import read_crop
    from battlelens.platform.ocr import recognize

    matcher = NameMatcher(Pokedex.load())
    correct, failures = 0, []
    for name in NAMES:
        expected = matcher.match(name).species_id
        for font_size, scale in RENDERINGS:
            reading = read_crop(_pixel_crop(name, font_size, scale), recognize, matcher, ("es", "en"))
            if reading.match.species_id == expected:
                correct += 1
            else:
                failures.append((name, font_size, scale, reading.match.raw_text))
    total = len(NAMES) * len(RENDERINGS)
    print(f"\nPrecisión OCR: {correct}/{total}")
    assert correct >= MIN_CORRECT, f"{correct}/{total}; fallos: {failures}"
