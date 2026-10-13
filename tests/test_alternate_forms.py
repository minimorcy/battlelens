"""Formas alternativas: disponibilidad por juego, vista de una forma y secuencia (add-alternate-forms)."""

import pytest

from battlelens.core.pokedex import Pokedex


@pytest.fixture(scope="module")
def dex():
    return Pokedex.load()


def test_rotom_en_platino(dex):
    cycle = dex.form_cycle(479, "platinum")
    assert cycle == ("rotom", "rotom-heat", "rotom-wash", "rotom-frost", "rotom-fan", "rotom-mow")
    second = {f: dex.view(479, "platinum", form=f).types[1] for f in cycle[1:]}
    assert second == {"rotom-heat": "fire", "rotom-wash": "water", "rotom-frost": "ice",
                      "rotom-fan": "flying", "rotom-mow": "grass"}


def test_megas_solo_en_sus_juegos(dex):
    assert dex.form_cycle(6, "sword-shield") == ("charizard",)
    assert not dex.view(6, "sword-shield").other_forms
    others = {o.name: o.types for o in dex.view(6, "x-y").other_forms}
    assert others == {"Mega-Charizard X": ("fire", "dragon"), "Mega-Charizard Y": ("fire", "flying")}


def test_formas_posteriores_al_juego(dex):
    assert "giratina-origin" not in dex.form_cycle(487, "diamond-pearl")
    assert "giratina-origin" in dex.form_cycle(487, "platinum")


def test_formas_cosmeticas_descartadas(dex):
    assert dex.get_species(201).forms == ()  # Unown


def test_rotom_lavado(dex):
    view = dex.view(479, "platinum", form="rotom-wash")
    assert view.name == "Rotom Lavado" and view.types == ("electric", "water")
    assert view.matchups[2.0] == ["grass"] and "ground" in view.matchups[0.0]
    assert view.form_id == "rotom-wash" and view.base_pokemon == "rotom"


def test_secuencia_de_zigzagoon_en_espada(dex):
    assert dex.form_cycle(263, "sword-shield") == ("zigzagoon-galar", "zigzagoon")
    assert dex.view(263, "sword-shield", form="zigzagoon").types == ("normal",)


def test_forma_no_disponible_usa_la_automatica(dex):
    assert dex.view(6, "sword-shield", form="charizard-mega-x").name == "Charizard"
