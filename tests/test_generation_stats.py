"""Estadísticas base y fórmulas de cada generación (add-generation-stats)."""

import pytest

from battlelens.core.competitive import stat_formula, stat_profile, view_ranges
from battlelens.core.pokedex import Pokedex

LETS_GO = "lets-go-pikachu-lets-go-eevee"


@pytest.fixture(scope="module")
def dex():
    return Pokedex.load()


# ---- estadísticas base según la generación ---------------------------------------

def test_pikachu_en_blanco_y_negro(dex):
    stats = dex.view(25, "black-white").stats
    assert stats["defense"] == 30 and stats["special_defense"] == 40


def test_pikachu_actual(dex):
    stats = dex.view(25).stats
    assert stats["defense"] == 40 and stats["special_defense"] == 50


def test_pikachu_en_rojo_y_azul_con_especial(dex):
    view = dex.view(25, "red-blue")
    assert view.stats == {"hp": 35, "attack": 55, "defense": 30, "special": 50, "speed": 90}
    assert view.stat_total == 260
    assert view.stat_keys == ("hp", "attack", "defense", "special", "speed")


def test_gen2_separa_la_especial(dex):
    assert "special" not in dex.view(65, "gold-silver").stats
    assert dex.view(65, "red-blue").stats["special"] == 135


def test_perfil_con_especial(dex):
    assert stat_profile(dex.view(65, "red-blue").stats)[0] == "Atacante especial"  # Alakazam


# ---- fórmulas --------------------------------------------------------------------

@pytest.mark.parametrize(
    ("game", "generation", "formula"),
    [("red-blue", 1, "gen12"), ("crystal", 2, "gen12"), (LETS_GO, 7, "lets-go"),
     ("legends-arceus", 8, "legends-arceus"), ("emerald", 3, "modern"), (None, None, "modern")],
)
def test_formula_por_juego(game, generation, formula):
    assert stat_formula(game, generation) == formula


def test_rangos_gen1(dex):
    ranges = view_ranges(dex.view(25, "red-blue"), 5)
    assert ranges["hp"] == (18, 23) and ranges["speed"] == (14, 18)


def test_rangos_lets_go_rival_y_tuyo(dex):
    view = dex.view(25, LETS_GO)
    rival = view_ranges(view, 5)
    assert rival["hp"] == (18, 20) and rival["speed"] == (12, 17)
    assert view_ranges(view, 5, own=True)["hp"] == (18, 220)  # tus AVs suman hasta 200


def test_rangos_leyendas_arceus(dex):
    assert view_ranges(dex.view(25, "legends-arceus"), 5)["speed"] == (61, 168)


def test_rangos_modernos_sin_cambios(dex):
    ranges = view_ranges(dex.view(445), 50)
    assert ranges["hp"] == (168, 215) and ranges["speed"] == (96, 169)
    assert view_ranges(dex.view(292), 30)["hp"] == (1, 1)  # Shedinja
