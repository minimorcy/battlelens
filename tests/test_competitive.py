import pytest

from battlelens.core.competitive import (
    SpeedVerdict,
    ability_effects,
    compare_speed,
    stat_profile,
    stat_ranges,
    weight_move_power,
)
from battlelens.core.learnsets import Learnsets
from battlelens.core.normalize import extract_level
from battlelens.core.pokedex import Pokedex


@pytest.fixture(scope="module")
def dex():
    return Pokedex.load()


# ---- nivel ---------------------------------------------------------------------

@pytest.mark.parametrize(
    ("readings", "level"),
    [(["Stufful Nv. 10"], 10), (["PIDGEY Lv5"], 5), (["RATTATA :L12"], 12), (["Stufiul 10"], 10),
     (["PIDGEY"], None), (["Stufful Nv. 410"], None), (["", "N. 10"], 10), (["Stufful", "Nv 7"], 7)],
)
def test_extraccion_del_nivel(readings, level):
    assert extract_level(readings) == level


# ---- movimientos probables -------------------------------------------------------

def test_movimientos_de_stufful_nivel_10():
    moves = Learnsets.get().probable_moves("stufful", 10, "sword-shield", 8)
    assert [m.name("es") for m in moves] == ["Placaje", "Malicioso", "Ojitos Tiernos", "Vendetta"]
    assert moves[0].category == "physical" and moves[0].power == 40 and moves[0].type == "normal"


def test_pocos_movimientos_a_nivel_bajo():
    moves = Learnsets.get().probable_moves("stufful", 1, "sword-shield", 8)
    assert [m.name("es") for m in moves] == ["Placaje", "Malicioso"]


def test_juego_sin_datos_usa_su_generacion():
    ls = Learnsets.get()
    assert ls.choose_version_group("stufful", "sword-shield", 8) == "sword-shield"
    # Stufful no existe en Esmeralda: se usa el juego más reciente con datos de una generación ≤ 3… y si no hay, el último
    assert ls.choose_version_group("stufful", "emerald", 3) is not None


def test_forma_regional_tiene_movimientos():
    assert Learnsets.get().probable_moves("zigzagoon-galar", 5, "sword-shield", 8)


# ---- estadísticas a su nivel ------------------------------------------------------

def test_rangos_garchomp_nivel_50(dex):
    r = stat_ranges(dex.get_species(445).stats, 50)
    assert r["hp"] == (168, 215) and r["speed"] == (96, 169)


def test_shedinja_siempre_un_ps(dex):
    assert stat_ranges(dex.get_species(292).stats, 37, "shedinja")["hp"] == (1, 1)


def test_jolteon_mas_rapido_que_snorlax(dex):
    jolteon = stat_ranges(dex.get_species(135).stats, 50)["speed"]
    snorlax = stat_ranges(dex.get_species(143).stats, 50)["speed"]
    assert compare_speed(jolteon, snorlax) is SpeedVerdict.FASTER
    assert compare_speed(snorlax, jolteon) is SpeedVerdict.SLOWER


def test_pikachu_contra_pikachu_depende(dex):
    pika = stat_ranges(dex.get_species(25).stats, 50)["speed"]
    assert compare_speed(pika, pika) is SpeedVerdict.DEPENDS


# ---- habilidades y entrenamiento -----------------------------------------------------

def test_habilidades_de_bronzong(dex):
    names = {"ground": "Tierra", "fire": "Fuego"}
    abilities = {a.identifier for a in dex.view(437).abilities}
    assert {"levitate", "heatproof"} <= abilities
    assert ability_effects("levitate", names.get) == ["Tierra ×0"]
    assert ability_effects("heatproof", names.get) == ["Fuego ×½"]
    assert ability_effects("wonder-guard", names.get) == ["Solo le afectan los ataques supereficaces"]
    assert ability_effects("run-away", names.get) == []


@pytest.mark.parametrize(("kg", "power"), [(6.8, 20), (10, 40), (24.9, 40), (50, 80), (199.9, 100), (460, 120), (None, None)])
def test_patada_baja(kg, power):
    assert weight_move_power(kg) == power


def test_snorlax_entrenamiento(dex):
    v = dex.view(143)
    assert v.ev_yield == {"hp": 2} and v.weight_kg == 460.0
    assert weight_move_power(v.weight_kg) == 120
    assert stat_profile(v.stats) == ["Atacante físico", "defensivo"]


def test_vista_trae_identificador_para_movimientos(dex):
    assert dex.view(263, "sword-shield").pokemon == "zigzagoon-galar"
    assert dex.view(263).pokemon == "zigzagoon"
