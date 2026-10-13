"""Habilidades según la generación y su efecto en la eficacia (add-ability-aware-matchups)."""

import pytest

from battlelens.core.abilities import adjusted_factor, multiplier_text, resolve
from battlelens.core.matchup import Verdict, matchup
from battlelens.core.pokedex import Ability, Pokedex

LEVITATE = Ability("levitate", {"es": "Levitación"}, False, slot=1)
HEATPROOF = Ability("heatproof", {"es": "Ignífugo"}, False, slot=2)


@pytest.fixture(scope="module")
def dex():
    return Pokedex.load()


def _effects(view):
    return {(e.type, e.factor, e.certain, tuple(a.identifier for a in e.abilities)) for e in view.ability_effects}


# ---- resolución --------------------------------------------------------------

def test_efecto_seguro_y_posible():
    assert resolve((LEVITATE,), "ground", 2.0)[0] == 0.0
    factor, effects = resolve((LEVITATE, HEATPROOF), "ground", 2.0)
    assert factor == 2.0 and len(effects) == 1 and not effects[0].certain and effects[0].factor == 0.0
    assert resolve((LEVITATE,), "water", 1.0) == (1.0, ())


def test_superguarda_y_filtro():
    assert adjusted_factor("wonder-guard", "normal", 1.0) == 0.0
    assert adjusted_factor("wonder-guard", "fire", 2.0) == 2.0
    assert adjusted_factor("filter", "fire", 2.0) == 1.5
    assert adjusted_factor("filter", "fire", 0.5) == 0.5
    assert multiplier_text(1.5) == "×1,5" and multiplier_text(0.0) == "×0"


# ---- habilidades según la generación --------------------------------------------

def test_gengar_en_platino_tiene_levitacion(dex):
    assert [a.identifier for a in dex.view(94, "platinum").abilities] == ["levitate"]
    assert [a.identifier for a in dex.view(94).abilities] == ["cursed-body"]


# ---- eficacia defensiva con habilidades ------------------------------------------

def test_flygon_inmune_a_tierra(dex):
    view = dex.view(330)
    assert "ground" in view.matchups[0.0]
    assert ("ground", 0.0, True, ("levitate",)) in _effects(view)


def test_bronzong_en_platino_efectos_posibles(dex):
    view = dex.view(437, "platinum")
    assert {"ground", "fire"} <= set(view.matchups[2.0])
    assert _effects(view) == {("ground", 0.0, False, ("levitate",)), ("fire", 1.0, False, ("heatproof",))}


def test_shedinja_solo_supereficaces(dex):
    view = dex.view(292)
    assert sorted(view.matchups[2.0]) == ["dark", "fire", "flying", "ghost", "rock"]
    assert len(view.matchups[0.0]) == 13 and not view.matchups[0.5] and not view.matchups[0.25]


# ---- comparativa ------------------------------------------------------------------

def _m(dex, own_id, rival_id, game=None):
    own, rival = dex.view(own_id, game), dex.view(rival_id, game)
    return matchup(own, rival, dex.type_chart(rival.generation))


def test_habilidad_segura_del_rival(dex):
    m = _m(dex, 445, 330)  # Garchomp contra Flygon
    assert dict(m.offense) == {"dragon": 2.0, "ground": 0.0}
    assert m.offense_effects["ground"][0].certain


def test_habilidad_posible_del_rival(dex):
    m = _m(dex, 445, 437, "platinum")  # Garchomp contra Bronzong
    assert dict(m.offense)["ground"] == 2.0
    (effect,) = m.offense_effects["ground"]
    assert not effect.certain and effect.factor == 0.0


def test_levitacion_en_el_veredicto(dex):
    m = _m(dex, 51, 94, "platinum")  # Dugtrio contra Gengar con Levitación
    assert m.offense == (("ground", 0.0),)
    assert m.verdict is Verdict.DISADVANTAGE
