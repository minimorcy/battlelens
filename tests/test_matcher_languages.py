"""El idioma del juego pesa al emparejar el nombre leído por el OCR."""

from battlelens.core.matcher import NameMatcher
from battlelens.core.pokedex import Pokedex


def test_nombre_de_otro_idioma_no_gana_a_una_mala_lectura():
    matcher = NameMatcher(Pokedex.load())
    assert matcher.match("lanask*").species_id == 274  # sin idioma: «Blanas» (Nuzleaf en alemán)
    assert not matcher.match("lanask*", ("es", "en")).recognized  # juego en español: mejor nada que Nuzleaf
    assert matcher.match("Yamask", ("es", "en")).species_id == 562
    assert matcher.match("Blanas", ("de",)).species_id == 274
    assert matcher.match("Pikachu", ("es-ES",)).species_id == 25  # nombre igual en todos los idiomas
