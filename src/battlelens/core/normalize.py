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


# Las palabras sueltas cortas dan falsos positivos (p. ej. "PII", nombre alemán de Cleffa),
# así que solo se prueban a partir de 4 letras y con una pequeña penalización.
MIN_TOKEN_LEN = 4
TOKEN_PENALTY = 5.0
# El símbolo de género pegado al nombre (Gen 6+) se lee como "O", "d", "16"…: se prueban también
# los candidatos sin sus últimos caracteres, con una penalización por carácter recortado.
TRIM_MAX = 2
TRIM_MIN_LEN = 6
TRIM_PENALTY = 2.0


def _strip_decorations(text: str) -> str:
    text = _LEVEL.sub(" ", text)
    text = _TRAILING_NUMBER.sub("", text)
    return _DETACHED_GENDER.sub("", text)


def _clean(text: str) -> str:
    text = text.replace("♂", "M").replace("♀", "F")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return _NON_ALNUM.sub("", text.upper())


def clean_text(text: str) -> str:
    """Mayúsculas sin acentos, espacios ni signos (para comparar nombres de movimiento)."""
    return _clean(text)


def normalize_name(text: str) -> str:
    return _clean(_strip_decorations(text))


def name_candidates(text: str) -> list[tuple[str, float]]:
    """(candidato, penalización): el texto completo normalizado y, si hay varias palabras,
    cada palabra y cada par de palabras contiguas.

    Permite encontrar el nombre aunque el OCR lea texto de más (restos del fondo, iconos…).
    """
    stripped = _strip_decorations(text)
    full = _clean(stripped)
    candidates: list[tuple[str, float]] = [(full, 0.0)] if full else []
    tokens = stripped.split()
    if len(tokens) > 1:
        parts = [_clean(t) for t in tokens] + [_clean(a + b) for a, b in zip(tokens, tokens[1:])]
        for part in parts:
            if len(part) >= MIN_TOKEN_LEN and part != full and all(part != c for c, _ in candidates):
                candidates.append((part, TOKEN_PENALTY))
    trimmed: list[tuple[str, float]] = []
    for cand, penalty in candidates:
        for n in range(1, TRIM_MAX + 1):
            if len(cand) - n >= TRIM_MIN_LEN - TRIM_MAX:
                if len(cand) >= TRIM_MIN_LEN:
                    trimmed.append((cand[:-n], penalty + n * TRIM_PENALTY))
    known = {c for c, _ in candidates}
    candidates += [(c, p) for c, p in trimmed if c not in known]
    return candidates


_LEVEL_VALUE = re.compile(r"(?:\b(?:lv|nv|niv|n|l)\s*\.?|:l)\s*(\d{1,3})\b", re.IGNORECASE)
_TRAILING_VALUE = re.compile(r"\s(\d{1,3})\s*$")
# Letras que el OCR confunde con dígitos en fuentes estilizadas (improve-level-reading D1)
_DIGIT_CONFUSIONS = str.maketrans("OoQDIl|iZzSsGbB", "000011112255668")
_LEVEL_CONFUSED = re.compile(
    r"(?:\b(?P<prefix>lv|nv|niv|n|l)\s*\.?|:l)\s*(?P<value>[0-9OoQDIl|iZzSsGbB]{1,3})(?![A-Za-z0-9])", re.IGNORECASE
)
_STRONG_PREFIXES = {"lv", "nv", "niv"}


def _confused_levels(text: str):
    for match in _LEVEL_CONFUSED.finditer(text):
        raw, prefix = match.group("value"), (match.group("prefix") or "").lower()
        if prefix in _STRONG_PREFIXES or any(c.isdigit() for c in raw):
            yield raw.translate(_DIGIT_CONFUSIONS)


def extract_level(readings) -> int | None:
    """Nivel (1-100) leído en alguna lectura de OCR: con prefijo («Nv. 10»), con prefijo y dígitos
    confundidos («Nv. 1G») y, por último, un número suelto al final («… 10»)."""
    readings = [r for r in readings if r]
    finders = (
        lambda text: (m.group(1) for m in _LEVEL_VALUE.finditer(text)),
        _confused_levels,
        lambda text: (m.group(1) for m in _TRAILING_VALUE.finditer(text)),
    )
    for find in finders:
        for text in readings:
            for value in find(text):
                if value.isdigit() and 1 <= int(value) <= 100:
                    return int(value)
    return None
