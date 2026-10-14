"""Idioma de la interfaz (spec interface-language).

El texto en español es la clave: `_("Reconocer ahora")` devuelve el texto tal cual en español o su
traducción del catálogo inglés. Con argumentos, se formatea después de traducir:
`_("Perfil «{name}» activado.", name=...)`. `N_("…")` solo marca un texto para el test de cobertura
(constantes de módulo que se traducen al mostrarse con `_(constante)`).
"""

from __future__ import annotations

from . import en_app, en_card, en_menus

INTERFACE_LANGUAGES = ("auto", "es", "en")
CATALOG_EN: dict[str, str] = {**en_app.EN, **en_menus.EN, **en_card.EN}

_language = "es"


def set_language(language: str) -> None:
    global _language
    if language not in ("es", "en"):
        raise ValueError(language)
    _language = language


def get_language() -> str:
    return _language


def resolve_language(setting: str, windows_tag: str | None) -> str:
    """`auto`: español si Windows está en español; inglés en cualquier otro caso (design.md D3)."""
    if setting in ("es", "en"):
        return setting
    return "es" if (windows_tag or "").lower().startswith("es") else "en"


def _(text: str, /, **kwargs) -> str:
    translated = CATALOG_EN.get(text, text) if _language == "en" else text
    return translated.format(**kwargs) if kwargs else translated


def N_(text: str, /) -> str:  # noqa: N802 - convención de gettext
    return text
