"""Tus movimientos: catálogo, lectura del menú de ataques, memoria y vigilante (add-own-moves)."""

import json
from dataclasses import dataclass

import numpy as np
import pytest

from battlelens.core.detection import RegionWatcher
from battlelens.core.learnsets import Learnsets
from battlelens.core.moves import MoveMatcher, MoveMemory
from battlelens.core.pokedex import Pokedex
from battlelens.core.profiles import Profile, Region
from battlelens.vision.preprocess import fingerprint_distance


@dataclass
class FakeOcr:
    text: str


@pytest.fixture(scope="module")
def matcher():
    return MoveMatcher(Learnsets.get().all_moves())


def _names(moves):
    return [m.name("es") for m in moves]


# ---- catálogo -------------------------------------------------------------------------

def test_catalogo_incluye_movimientos_de_mt():
    move = Learnsets.get().move("double-kick")
    assert move.name("es") == "Doble Patada" and move.type == "fighting"
    assert move.category == "physical" and move.power == 30
    assert Learnsets.get().move("no-existe") is None


# ---- lectura del menú -------------------------------------------------------------------

def test_menu_de_espada(matcher):
    text = "Ascuas PP 25/25 Placaje PP 35/35 Gruñido PP 40/40 Ataque Rápido PP 30/30"
    assert _names(matcher.match(text)) == ["Ascuas", "Placaje", "Gruñido", "Ataque Rápido"]


def test_lectura_con_errores(matcher):
    assert _names(matcher.match("EMBER TACKIE GROWL QUICK ATTAGK")) == ["Ascuas", "Placaje", "Gruñido", "Ataque Rápido"]


@pytest.mark.parametrize("text", ["Machop salvaje usó Patada Baja!", "LUCHAR POKÉMON BOLSA HUIR",
                                  "¡El Scorbunny enemigo se ha debilitado!", "What will SCORBUNNY do?"])
def test_menu_cerrado_no_es_valido(matcher, text):
    from battlelens.pipeline import read_moves

    crop = np.full((40, 120, 3), 255, np.uint8)
    assert read_moves(crop, lambda image, langs: FakeOcr(text), matcher, ("es",)) == ()


def test_read_moves_combina_variantes(matcher):
    from battlelens.pipeline import read_moves

    texts = iter(["Placaje Ataque Rápido", "Placaje", "Ascuas Gruñido Placaje"])
    crop = np.full((40, 120, 3), 255, np.uint8)
    moves = read_moves(crop, lambda image, langs: FakeOcr(next(texts, "")), matcher, ("es",))
    assert _names(moves) == ["Placaje", "Ataque Rápido", "Ascuas", "Gruñido"]  # en orden de aparición


def test_read_moves_prefiere_los_repetidos(matcher):
    from battlelens.pipeline import read_moves

    texts = iter(["Placaje Gruñido", "Placaje Gruñido Ascuas Burbuja", "Placaje Gruñido Ascuas", "Pistola Agua"])
    crop = np.full((40, 120, 3), 255, np.uint8)
    moves = read_moves(crop, lambda image, langs: FakeOcr(next(texts, "")), matcher, ("es",))
    assert _names(moves) == ["Placaje", "Gruñido", "Ascuas", "Burbuja"]


# ---- memoria ------------------------------------------------------------------------------

def test_memoria_guarda_cambia_y_persiste(tmp_path):
    memory = MoveMemory(tmp_path / "moves.json")
    assert memory.get("p1", 813) == []
    assert memory.store("p1", 813, ["ember", "tackle"])
    assert not memory.store("p1", 813, ["ember", "tackle"])  # sin cambios
    assert memory.store("p1", 813, ["ember", "double-kick"])
    again = MoveMemory(tmp_path / "moves.json")
    assert again.get("p1", 813) == ["ember", "double-kick"] and again.get("p2", 813) == []
    assert json.loads((tmp_path / "moves.json").read_text(encoding="utf-8")) == {"p1": {"813": ["ember", "double-kick"]}}


def test_memoria_con_archivo_corrupto(tmp_path):
    (tmp_path / "moves.json").write_text("{no es json", encoding="utf-8")
    assert MoveMemory(tmp_path / "moves.json").get("p1", 1) == []


# ---- vigilante del menú -----------------------------------------------------------------

def test_vigilante_lee_una_vez_cuando_se_estabiliza():
    watcher = RegionWatcher(fingerprint_distance)
    menu = np.full((12, 32), 200, np.uint8)
    scene = np.zeros((12, 32), np.uint8)
    assert [watcher.on_frame(menu) for _ in range(3)] == [False, False, True]
    watcher.attempted(menu)
    assert not any(watcher.on_frame(menu) for _ in range(5))  # sin cambios no se repite
    assert [watcher.on_frame(scene) for _ in range(3)] == [False, False, True]


# ---- perfil -------------------------------------------------------------------------------

def test_region_del_menu_fuera_de_las_regiones_de_nombre():
    profile = Profile("Espada", Region(0.6, 0.05, 0.2, 0.05)).with_role_region("moves", Region(0.7, 0.6, 0.3, 0.3))
    assert set(profile.regions()) == {"rival"} and profile.moves_region is not None
    again = Profile.from_dict(json.loads(json.dumps(profile.to_dict())))
    assert again.moves_region == profile.moves_region
    old = profile.to_dict()
    del old["moves_region"]
    assert Profile.from_dict(old).moves_region is None
    assert profile.with_role_region("moves", None).moves_region is None


def test_pipeline_lee_el_menu(matcher):
    from battlelens.core.matcher import NameMatcher
    from battlelens.pipeline import RecognitionPipeline

    dex = Pokedex.load()
    profile = Profile("Espada", Region(0.6, 0.05, 0.2, 0.05), moves_region=Region(0.6, 0.6, 0.3, 0.3))

    def ocr(image, langs):
        return FakeOcr("Machop Nv. 16" if image.shape[0] < 80 else "Ascuas PP 25/25 Placaje PP 35/35")

    capture = lambda hwnd: np.full((640, 960, 3), 255, np.uint8)
    result = RecognitionPipeline(dex, NameMatcher(dex), capture, ocr, move_matcher=matcher).run(1, profile)
    assert result.species.id == 66 and _names(result.moves) == ["Ascuas", "Placaje"]
    assert result.fingerprint.shape == (12, 32)  # el menú no entra en la huella del combate
