import pytest

from battlelens.core.pokedex import DatasetMissingError, Pokedex


@pytest.fixture(scope="module")
def dex() -> Pokedex:
    return Pokedex.load()


def test_dataset_completo(dex):
    assert len(dex) >= 1025
    assert len(dex.type_efficacy) == 18
    assert all(len(row) == 18 for row in dex.type_efficacy.values())


def test_ficha_charizard(dex):
    s = dex.get_species(6)
    assert s.name("en") == "Charizard"
    assert s.types == ("fire", "flying")
    assert [s.stats[k] for k in ("hp", "attack", "defense", "special_attack", "special_defense", "speed")] == [
        78, 84, 78, 109, 85, 100,
    ]
    assert s.stat_total == 534
    assert [(a.name("es"), a.hidden) for a in s.abilities] == [("Mar Llamas", False), ("Poder Solar", True)]


def test_eficacia_charizard(dex):
    g = dex.defensive_matchups(("fire", "flying"))
    assert g[4.0] == ["rock"]
    assert sorted(g[2.0]) == ["electric", "water"]
    assert sorted(g[0.5]) == ["fairy", "fighting", "fire", "steel"]
    assert sorted(g[0.25]) == ["bug", "grass"]
    assert g[0.0] == ["ground"]


def test_inmunidades_gengar(dex):
    g = dex.defensive_matchups(("ghost", "poison"))
    assert sorted(g[0.0]) == ["fighting", "normal"]


def test_dataset_ausente(tmp_path):
    with pytest.raises(DatasetMissingError, match="build_dataset"):
        Pokedex.load(tmp_path / "no-existe.json")
