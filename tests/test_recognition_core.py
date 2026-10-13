import pytest

from pokemon_stats_live.core.matcher import NameMatcher
from pokemon_stats_live.core.normalize import normalize_name
from pokemon_stats_live.core.pokedex import Pokedex


@pytest.fixture(scope="module")
def matcher() -> NameMatcher:
    return NameMatcher(Pokedex.load())


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Farfetch'd", "FARFETCHD"),
        ("FARFETCH D", "FARFETCHD"),
        ("PIDGEY Nv5", "PIDGEY"),
        ("PIDGEY Lv.5", "PIDGEY"),
        ("PIDGEY :L5", "PIDGEY"),
        ("PIDGEY ♂", "PIDGEY"),
        ("PIDGEY ♀ Nv. 12", "PIDGEY"),
        ("NIDORAN♀", "NIDORANF"),
        ("Salamèche", "SALAMECHE"),
        ("Mr. Mime", "MRMIME"),
        ("Porygon2", "PORYGON2"),
    ],
)
def test_normalizacion(raw, expected):
    assert normalize_name(raw) == expected


@pytest.mark.parametrize(
    ("raw", "species_id"),
    [
        ("PIDGEY", 16),
        ("P1DGEY", 16),
        ("PIDGEY ♂ Lv5", 16),
        ("NIDORAN♀", 29),
        ("NIDORAN♂", 32),
        ("SALAMÈCHE", 4),
        ("Glurak", 6),
        ("MEW", 151),
        ("MEWTWO", 150),
        ("PORYGON2", 233),
    ],
)
def test_coincidencia(matcher, raw, species_id):
    result = matcher.match(raw)
    assert result.recognized
    assert result.species_id == species_id
    assert result.score >= 80


@pytest.mark.parametrize("raw", ["", "   ", "~~ ##", "XQZWVKJ"])
def test_no_reconocido(matcher, raw):
    result = matcher.match(raw)
    assert not result.recognized
    assert result.raw_text == raw


def test_umbral_configurable():
    strict = NameMatcher(Pokedex.load(), threshold=95)
    assert not strict.match("P1DGEY").recognized
