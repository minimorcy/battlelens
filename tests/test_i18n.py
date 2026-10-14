"""Idioma de la interfaz y cobertura de la traducción (add-english-ui)."""

import ast
import re
import string
from pathlib import Path

import pytest

import battlelens.i18n as i18n
from battlelens.i18n import CATALOG_EN, _, resolve_language

SRC = Path(__file__).resolve().parent.parent / "src" / "battlelens"


def _marked_texts() -> dict[str, str]:
    """Literales de `_()` y `N_()` en el código, con el archivo donde aparecen."""
    found: dict[str, str] = {}
    for path in SRC.rglob("*.py"):
        if "i18n" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("_", "N_")
                    and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
                found.setdefault(node.args[0].value, path.relative_to(SRC).as_posix())
    return found


def _fields(text: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


def test_todos_los_textos_tienen_traduccion():
    missing = {text: where for text, where in _marked_texts().items() if text not in CATALOG_EN}
    assert not missing, f"Textos sin traducir al inglés: {missing}"


def test_sin_claves_repetidas_entre_catalogos():
    from battlelens.i18n import en_app, en_card, en_menus

    seen: dict[str, str] = {}
    repeated = []
    for name, catalog in (("app", en_app.EN), ("menus", en_menus.EN), ("card", en_card.EN)):
        for key in catalog:
            if key in seen:
                repeated.append((key, seen[key], name))
            seen[key] = name
    assert not repeated, f"Textos en más de un catálogo: {repeated}"


def test_marcadores_iguales_en_los_dos_idiomas():
    wrong = {es: en for es, en in CATALOG_EN.items() if _fields(es) != _fields(en)}
    assert not wrong, f"Marcadores distintos: {wrong}"


def test_sin_traducciones_huerfanas():
    unused = set(CATALOG_EN) - set(_marked_texts())
    assert not unused, f"Traducciones que ya no se usan: {sorted(unused)}"


def test_las_traducciones_no_son_espanol():
    spanish = re.compile(r"[ñáéíóú¿¡]")
    suspicious = {es: en for es, en in CATALOG_EN.items() if spanish.search(en) and "Pokémon" not in en}
    assert not suspicious, f"Traducciones con caracteres españoles: {suspicious}"


# ---- idioma -----------------------------------------------------------------------------------

@pytest.mark.parametrize(("setting", "windows", "expected"), [
    ("auto", "en-US", "en"), ("auto", "es-ES", "es"), ("auto", "es-MX", "es"), ("auto", "fr-FR", "en"),
    ("auto", None, "en"), ("en", "es-ES", "en"), ("es", "en-US", "es"),
])
def test_resolver_idioma(setting, windows, expected):
    assert resolve_language(setting, windows) == expected


def test_traducir_y_formatear():
    try:
        i18n.set_language("en")
        assert _("Texto que no está en el catálogo {n}", n=3) == "Texto que no está en el catálogo 3"
    finally:
        i18n.set_language("es")
    assert _("Hola {name}", name="Ash") == "Hola Ash"
    with pytest.raises(ValueError):
        i18n.set_language("fr")
