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
    readings = iter(["~~", "P1DGEY Nv. 5", "PIDGEY Nv. 5", "RATTATA"])
    calls = []

    def ocr(image, langs):
        calls.append(1)
        return FakeOcr(next(readings))

    p = RecognitionPipeline(dex, NameMatcher(dex), lambda h: np.full((640, 960, 3), 255, np.uint8), ocr)
    result = p.run(1, profile)
    assert result.species.id == 16 and result.match.score == 100
    assert len(calls) == 3  # parada temprana al llegar a 100 con el nivel leído


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


def test_tres_regiones_desde_una_captura(dex):
    from battlelens.core.profiles import Region

    captures = []
    texts = ["PIDGEY Nv. 5", "RATTATA Nv. 3"]  # después, el propio con apodo ("MiPerrito"): no reconocido

    def capture(hwnd):
        captures.append(hwnd)
        return np.full((640, 960, 3), 255, dtype=np.uint8)

    def ocr(image, langs):
        return FakeOcr(texts.pop(0) if texts else "MiPerrito")

    profile = Profile("Dobles", Region(0.6, 0.05, 0.2, 0.05),
                      rival2_region=Region(0.6, 0.15, 0.2, 0.05), own_region=Region(0.05, 0.8, 0.2, 0.05))
    result = RecognitionPipeline(dex, NameMatcher(dex), capture, ocr).run(7, profile)
    assert captures == [7]
    assert result.species.id == 16 and result.rival2.species_id == 19
    assert result.own is not None and not result.own.recognized
    assert result.key == (16, 19, None)
    assert result.fingerprint.shape == (12, 96)


def test_perfil_de_una_region_sin_cambios(dex, profile):
    p, _ = _pipeline(dex, "PIDGEY")
    result = p.run(1, profile)
    assert result.rival2 is None and result.own is None
    assert result.key == (16, None, None) and result.fingerprint.shape == (12, 32)


def test_niveles_por_region(dex):
    from battlelens.core.profiles import Region

    texts = ["Stufful Nv. 10", "Scorbunny Nv. 14"]

    def ocr(image, langs):
        return FakeOcr(texts.pop(0) if texts else "")

    profile = Profile("Espada", Region(0.6, 0.05, 0.2, 0.05), own_region=Region(0.05, 0.8, 0.2, 0.05))
    result = RecognitionPipeline(dex, NameMatcher(dex), lambda h: np.full((640, 960, 3), 255, np.uint8), ocr).run(1, profile)
    assert result.key == (759, None, 813)
    assert result.levels == (10, None, 14)


# ---- búsqueda adicional del nivel (improve-level-reading) ---------------------------------

def _read(texts, crop=None):
    from battlelens.pipeline import read_crop

    calls = []

    def ocr(image, langs):
        calls.append(image.shape)
        return FakeOcr(texts.pop(0) if texts else "")

    crop = crop if crop is not None else np.full((30, 200, 3), 255, np.uint8)
    dex = Pokedex.load()
    return read_crop(crop, ocr, NameMatcher(dex), ("es",)), calls


def test_nivel_en_otra_variante():
    reading, calls = _read(["Machop", "Machop Nv. 16", "Machop Nv. 99"])
    assert reading.match.species_id == 66 and reading.level == 16
    assert len(calls) == 2  # para en cuanto aparece el nivel


def test_nivel_solo_en_la_mitad_derecha():
    reading, calls = _read(["Machop", "", "", "", "Nv. 16", ""])
    assert reading.match.species_id == 66 and reading.level == 16
    assert calls[-2][0] == 48 + 20  # mitad derecha ampliada a 48 px (más el margen)


def test_region_sin_nivel_lecturas_acotadas():
    reading, calls = _read(["PIDGEY"])
    assert reading.match.species_id == 16 and reading.level is None
    assert len(calls) == 1 + 3 + 2


def test_sin_reconocer_no_busca_el_nivel():
    reading, calls = _read([])
    assert not reading.match.recognized and len(calls) == 18  # todas las variantes, sin extras
