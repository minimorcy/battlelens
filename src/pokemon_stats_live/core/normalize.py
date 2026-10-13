"""Normalización de nombres para comparar el texto del OCR con el dataset."""

from __future__ import annotations

import re
import unicodedata

# "Lv5", "Lv. 5", "Nv5", "Nv.5", "N.5", ":L5" (Gen 1)
_LEVEL = re.compile(r"(?:\b(?:lv|nv|n)\s*\.?|:l)\s*\d+", re.IGNORECASE)
# Símbolo de género del recuadro de combate, separado del nombre por un espacio
_DETACHED_GENDER = re.compile(r"\s+[♂♀]")
# Número suelto al final (nivel leído sin el prefijo "Lv")
_TRAILING_NUMBER = re.compile(r"\s+\d+\s*$")
_NON_ALNUM = re.compile(r"[^A-Z0-9]")


def normalize_name(text: str) -> str:
    text = _LEVEL.sub(" ", text)
    text = _TRAILING_NUMBER.sub("", text)
    text = _DETACHED_GENDER.sub("", text)
    text = text.replace("♂", "M").replace("♀", "F")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return _NON_ALNUM.sub("", text.upper())
