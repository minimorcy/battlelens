import json
from dataclasses import dataclass

import numpy as np
import pytest

from battlelens.core.matcher import NameMatcher
from battlelens.core.pokedex import Pokedex
from battlelens.core.profiles import Profile, Region
from battlelens.pipeline import RecognitionPipeline


class FakeCaptureError(RuntimeError):
    pass


@dataclass
class FakeOcr:
    text: str


@pytest.fixture(scope="module")
def dex():
    return Pokedex.load()


@pytest.fixture
def profile():
    return Profile("Test", Region(0.5, 0.0625, 0.1667, 0.0375), ("es",))


def _pipeline(dex, text, debug_dir=None, capture=None):
    seen = {}

    def fake_capture(hwnd):
        seen["hwnd"] = hwnd
        return np.full((640, 960, 3), 255, dtype=np.uint8)

    def fake_ocr(image, langs):
        seen["shape"], seen["langs"] = image.shape, langs
        return FakeOcr(text)

    p = RecognitionPipeline(dex, NameMatcher(dex), capture or fake_capture, fake_ocr, debug_dir)
    return p, seen


def test_reconocimiento_correcto(dex, profile):
    p, seen = _pipeline(dex, "CHARIZARD Nv36")
    result = p.run(1234, profile)
    assert result.recognized and result.species.id == 6
    assert seen["hwnd"] == 1234 and seen["langs"] == ("es",)
    assert set(result.timings_ms) == {"captura", "recorte", "ocr", "total"}


def test_se_queda_con_la_mejor_variante(dex, profile):
    readings = iter(["~~", "P1DGEY", "PIDGEY", "RATTATA"])
    calls = []

    def ocr(image, langs):
        calls.append(1)
        return FakeOcr(next(readings))

    p = RecognitionPipeline(dex, NameMatcher(dex), lambda h: np.full((640, 960, 3), 255, np.uint8), ocr)
    result = p.run(1, profile)
    assert result.species.id == 16 and result.match.score == 100
    assert len(calls) == 3  # parada temprana al llegar a 100


def test_no_reconocido(dex, profile):
    p, _ = _pipeline(dex, "~~##")
    result = p.run(1, profile)
    assert not result.recognized
    assert result.match.raw_text == "~~##"


def test_error_de_captura_se_propaga(dex, profile):
    def broken(hwnd):
        raise FakeCaptureError("ventana no disponible")

    p, _ = _pipeline(dex, "PIDGEY", capture=broken)
    with pytest.raises(FakeCaptureError):
        p.run(1, profile)


def test_volcado_de_depuracion(dex, profile, tmp_path):
    p, _ = _pipeline(dex, "PIDGEY", debug_dir=tmp_path / "debug")
    p.run(1, profile)
    files = sorted(f.name for f in (tmp_path / "debug").iterdir())
    assert len(files) == 3
    stamps = {f.split("-recorte")[0].split("-preprocesado")[0].removesuffix(".json") for f in files}
    assert len(stamps) == 1
    data = json.loads(next((tmp_path / "debug").glob("*.json")).read_text(encoding="utf-8"))
    assert data["especie"] == 16 and data["ocr"] == "PIDGEY"


def test_sin_depuracion_no_escribe(dex, profile, tmp_path):
    p, _ = _pipeline(dex, "PIDGEY", debug_dir=None)
    p.run(1, profile)
    assert not any(tmp_path.iterdir())
