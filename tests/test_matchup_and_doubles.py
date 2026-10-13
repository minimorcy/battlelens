import json

import numpy as np
import pytest

from battlelens.core.detection import Action, BattleDetector
from battlelens.core.matchup import Verdict, matchup
from battlelens.core.pokedex import Pokedex
from battlelens.core.profiles import Profile, ProfileError, ProfileStore, Region
from battlelens.vision.preprocess import fingerprint_distance


@pytest.fixture(scope="module")
def dex():
    return Pokedex.load()


def _m(dex, own_id, rival_id, game=None):
    own, rival = dex.view(own_id, game), dex.view(rival_id, game)
    generation = rival.generation
    return matchup(own, rival, dex.type_chart(generation))


# ---- comparativa de tipos -----------------------------------------------------

def test_charizard_contra_venusaur(dex):
    m = _m(dex, 6, 3)
    assert m.offense == (("fire", 2.0), ("flying", 2.0))
    assert m.defense == (("grass", 0.25), ("poison", 1.0))
    assert m.verdict is Verdict.ADVANTAGE and m.own_name == "Charizard"


def test_charizard_contra_golem(dex):
    m = _m(dex, 6, 76)
    assert max(x for _, x in m.offense) == 0.5  # Roca resiste Fuego y Volador
    assert dict(m.defense)["rock"] == 4.0
    assert m.verdict is Verdict.DISADVANTAGE


def test_rattata_contra_pidgey(dex):
    assert _m(dex, 19, 16).verdict is Verdict.NEUTRAL


def test_comparativa_usa_la_generacion(dex):
    # Gen 1: Fantasma no afecta a Psíquico → Gengar contra Alakazam, sus ataques Fantasma hacen ×0
    m = _m(dex, 94, 65, "red-blue")
    assert dict(m.offense)["ghost"] == 0.0


# ---- perfiles con regiones opcionales ------------------------------------------

R1, R2, OWN = Region(0.6, 0.05, 0.2, 0.05), Region(0.6, 0.15, 0.2, 0.05), Region(0.05, 0.8, 0.2, 0.05)


def test_regiones_en_orden_fijo():
    p = Profile("Dobles", R1).with_role_region("own", OWN).with_role_region("rival2", R2)
    assert list(p.regions()) == ["rival", "rival2", "own"]
    assert list(Profile("Simple", R1).regions()) == ["rival"]


def test_quitar_regiones():
    p = Profile("Dobles", R1, rival2_region=R2, own_region=OWN)
    assert list(p.with_role_region("rival2", None).regions()) == ["rival", "own"]
    with pytest.raises(ProfileError):
        p.with_role_region("rival", None)


def test_regiones_ida_y_vuelta(tmp_path):
    store = ProfileStore(tmp_path)
    p = Profile("Dobles", R1, rival2_region=R2, own_region=OWN)
    store.save(p)
    other = ProfileStore(tmp_path)
    other.load()
    assert other.profiles[p.id] == p


def test_perfil_sin_regiones_opcionales(tmp_path):
    legacy = {
        "name": "Viejo", "region": {"x": 0.1, "y": 0.1, "width": 0.2, "height": 0.05},
        "ocr_languages": ["es"], "id": "old00001", "created_at": "2026-10-13T00:00:00+00:00",
    }
    (tmp_path / "old00001.json").write_text(json.dumps(legacy), encoding="utf-8")
    store = ProfileStore(tmp_path)
    store.load()
    p = store.profiles["old00001"]
    assert p.rival2_region is None and p.own_region is None


# ---- clave de combate ------------------------------------------------------------

def fp(v):
    return np.full((12, 96), v, dtype=np.uint8)


def test_cambia_tu_pokemon_actualiza():
    det = BattleDetector(fingerprint_distance)
    assert det.on_result((3, None, 6), fp(10), 0.0) is Action.SHOW
    assert det.on_result((3, None, 6), fp(10), 1.0) is Action.NONE
    assert det.on_result((3, None, 9), fp(40), 2.0) is Action.SHOW


def test_sin_rival_no_cuenta_como_reconocido():
    det = BattleDetector(fingerprint_distance)
    assert det.on_result((None, None, 6), fp(10), 0.0) is Action.NONE
    assert det.on_result((None, 19, None), fp(10), 0.0) is Action.SHOW  # basta con el 2.º rival
