import pytest

from battlelens.core.games import GameDetector
from battlelens.core.pokedex import Pokedex


@pytest.fixture(scope="module")
def dex() -> Pokedex:
    return Pokedex.load()


@pytest.fixture(scope="module")
def detector(dex) -> GameDetector:
    return GameDetector(dex.games)


# ---- catálogo de juegos ------------------------------------------------------

def test_juego_con_forma_regional(dex):
    game = dex.get_game("sword-shield")
    assert game.generation == 8 and game.regional_form == "galar"
    assert game.name("es") == "Espada / Escudo"


def test_lets_go_usa_formas_de_alola(dex):
    assert dex.get_game("lets-go-pikachu-lets-go-eevee").regional_form == "alola"


def test_dlc_no_son_juegos_aparte(dex):
    ids = {g.id for g in dex.games}
    assert "the-isle-of-armor" not in ids and "sword-shield" in ids


# ---- detección por título ----------------------------------------------------

@pytest.mark.parametrize(
    ("title", "game"),
    [
        ("Eden Nightly | 4dc69c06f7-master | Pokémon Espada (64-bit) | 1.3.2", "sword-shield"),
        ("Ryujinx 1.2 - Pokémon Shield v1.3.2", "sword-shield"),
        ("mGBA - Pokemon Rojo Fuego", "firered-leafgreen"),
        ("mGBA - Pokemon - Emerald Version (USA)", "emerald"),
        ("mGBA - POKEMON EMER", "emerald"),
        ("DeSmuME 0.9.13 | POKEMON PL", "platinum"),
        ("Citra | Pokémon X", "x-y"),
        ("Citra | Pokémon Ultrasol", "ultra-sun-ultra-moon"),
        ("Citra | Pokémon Sol", "sun-moon"),
        ("melonDS - Pokémon Blanco 2", "black-2-white-2"),
        ("melonDS - Pokemon Blanco", "black-white"),
        ("Pokémon Escarlata", "scarlet-violet"),
        ("Pokémon Leyendas: Arceus", "legends-arceus"),
    ],
)
def test_deteccion(detector, title, game):
    assert detector.detect(title) == game


@pytest.mark.parametrize("title", ["Bloc de notas - Lista X", "Explorador de archivos", "", None, "Rojo y azul.txt"])
def test_sin_deteccion(detector, title):
    assert detector.detect(title) is None


# ---- tablas de tipos por generación ------------------------------------------

def test_tabla_gen1(dex):
    chart = dex.type_chart(1)
    assert len(chart) == 15 and "dark" not in chart and "steel" not in chart and "fairy" not in chart
    assert chart["ghost"]["psychic"] == 0.0
    assert chart["bug"]["poison"] == 2.0


def test_acero_en_gen5(dex):
    g = dex.defensive_matchups(("steel",), 5)
    assert "ghost" in g[0.5] and "dark" in g[0.5]
    g_now = dex.defensive_matchups(("steel",))
    assert "ghost" not in g_now[0.5] and "dark" not in g_now[0.5]


def test_hada_no_existe_antes_de_gen6(dex):
    assert "fairy" not in dex.damage_multipliers(("dragon",), 5)
    assert dex.damage_multipliers(("dragon",), 6)["fairy"] == 2.0


# ---- vista según el juego ----------------------------------------------------

def test_zigzagoon_en_espada(dex):
    v = dex.view(263, "sword-shield", "es")
    assert v.name == "Zigzagoon de Galar" and v.form == "galar"
    assert v.types == ("dark", "normal")
    assert v.matchups[4.0] == ["fighting"]
    assert sorted(v.matchups[0.0]) == ["ghost", "psychic"]
    assert [(o.name, o.types) for o in v.other_forms] == [("Zigzagoon", ("normal",))]


def test_zigzagoon_en_esmeralda(dex):
    v = dex.view(263, "emerald", "es")
    assert v.name == "Zigzagoon" and v.types == ("normal",) and v.form is None
    assert [(o.name, o.types) for o in v.other_forms] == [("Zigzagoon de Galar", ("dark", "normal"))]


def test_clefairy_por_generacion(dex):
    assert dex.view(35, "black-white").types == ("normal",)
    assert dex.view(35, "x-y").types == ("fairy",)
    assert dex.view(35).types == ("fairy",)


def test_magnemite_en_gen1(dex):
    assert dex.view(81, "red-blue").types == ("electric",)
    assert dex.view(81, "gold-silver").types == ("electric", "steel")


def test_habilidades_por_generacion(dex):
    assert dex.view(6, "red-blue").abilities == ()
    assert [a.hidden for a in dex.view(6, "emerald").abilities] == [False]
    assert any(a.hidden for a in dex.view(6, "black-white").abilities)


def test_tauros_en_escarlata_lista_las_otras_razas(dex):
    v = dex.view(128, "scarlet-violet", "es")
    assert v.form.startswith("paldea") and "fighting" in v.types
    names = [o.name for o in v.other_forms]
    assert names[0] == "Tauros" and len(names) == 3


def test_sin_juego_forma_original_y_generacion_actual(dex):
    v = dex.view(6)
    assert v.name == "Charizard" and v.generation == 9 and v.stat_total == 534
