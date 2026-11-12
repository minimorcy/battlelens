"""Buscador de Pokémon (spec pokemon-search)."""

from battlelens.core.config import Config
from battlelens.core.matcher import NameMatcher
from battlelens.core.pokedex import Pokedex


def test_atajo_de_busqueda_en_la_configuracion():
    assert Config.from_toml("").hotkey_search == "Ctrl+Alt+B"
    assert Config.from_toml('[hotkeys]\nsearch = "Ctrl+Shift+K"\n').hotkey_search == "Ctrl+Shift+K"


def test_buscador_sugiere_y_resuelve(qapp):
    from battlelens.ui.search import TYPES_ROLE, SearchDialog

    dex = Pokedex.load()
    entries = sorted((n, [(t, t) for t in types], (sid, f)) for n, types, sid, f in dex.search_entries("sword-shield", "es"))
    d = SearchDialog(entries, NameMatcher(dex))
    completer = d.edit.completer()
    completer.setCompletionPrefix("rapidash")
    model = completer.completionModel()
    found = {model.index(i, 0).data(): model.index(i, 0).data(TYPES_ROLE) for i in range(model.rowCount())}
    assert found == {"Rapidash": [("fire", "fire")],  # las dos formas, cada una con sus tipos para las píldoras
                     "Rapidash de Galar": [("psychic", "psychic"), ("fairy", "fairy")]}
    import gc

    gc.collect()  # el delegado que pinta las píldoras debe sobrevivir a la recolección de Python
    assert type(completer.popup().itemDelegate()).__name__ == "_TypesDelegate"

    d.edit.setText("xyzzy")
    d.edit.returnPressed.emit()
    assert d.choice is None and not d.error.isHidden() and d.result() == 0

    d.edit.setText("rapidash de galar")  # una sugerencia: su forma exacta
    d.edit.returnPressed.emit()
    assert d.choice == (78, "rapidash-galar") and d.result() == 1

    d = SearchDialog(entries, NameMatcher(dex))
    d.edit.setText("flabebe")  # fuera de la lista: emparejador aproximado y forma automática
    d.edit.returnPressed.emit()
    assert d.choice == (669, None) and d.result() == 1


def test_sugerencias_por_forma_como_la_ficha():
    dex = Pokedex.load()
    for game in ("sword-shield", "platinum", "x-y", None):
        entries = dex.search_entries(game, "es")
        assert len({name.casefold() for name, *_ in entries}) == len(entries), game  # nombres únicos
        for name, types, sid, form in entries:
            if sid in (6, 78, 128, 479):
                view = dex.view(sid, game, "es", form)
                assert (name, types) == (view.name, view.types)
    names = {name for name, *_ in dex.search_entries("sword-shield", "es")}
    assert {"Rapidash", "Rapidash de Galar", "Rotom Lavado"} <= names and "Mega-Charizard X" not in names
    assert "Mega-Charizard X" in {name for name, *_ in dex.search_entries("x-y", "es")}
