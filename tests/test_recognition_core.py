import pytest

from battlelens.core.matcher import NameMatcher
from battlelens.core.normalize import normalize_name
from battlelens.core.pokedex import Pokedex


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


@pytest.mark.parametrize(
    ("raw", "species_id"),
    [("Stufiul 10", 759), ("StuffulO", 759), ("StutfulO", 759), ("Stuffu16", 759), ("~~ Stufful ##", 759),
     ("Mr. Mime", 122), ("Mime Jr.", 439)],
)
def test_texto_con_ruido(matcher, raw, species_id):
    result = matcher.match(raw)
    assert result.species_id == species_id
    assert result.score >= 82  # con margen sobre el umbral de 80


def test_palabra_corta_no_da_falso_positivo(matcher):
    # "PII" es el nombre alemán de Cleffa: una palabra suelta tan corta no debe bastar.
    assert not matcher.match("PII NG").recognized


def test_letras_confundidas_en_fuentes_pixeladas():
    from battlelens.core.matcher import NameMatcher
    from battlelens.core.pokedex import Pokedex

    matcher = NameMatcher(Pokedex.load())
    for text, species in (("RRTTRTR", 19), ("CHRRIZRRD", 6), ("GROUOON", 383)):
        result = matcher.match(text)
        assert result.species_id == species and result.score == 97
    assert matcher.match("PIDGEY").score == 100  # lo exacto sigue ganando
