"""Detección del juego a partir del título de la ventana del emulador (design.md D4)."""

from __future__ import annotations

import re
import unicodedata

from dataclasses import dataclass

from .pokedex import Game

SHORT_NAME_MAX_LEN = 4
# Títulos internos de ROM que muestran mGBA o DeSmuME cuando no hay nombre de archivo
ROM_ALIASES = {
    "POKEMON EMER": "emerald",
    "POKEMON FIRE": "firered-leafgreen",
    "POKEMON LEAF": "firered-leafgreen",
    "POKEMON RUBY": "ruby-sapphire",
    "POKEMON SAPP": "ruby-sapphire",
    "POKEMON PL": "platinum",
    "POKEMON HG": "heartgold-soulsilver",
    "POKEMON SS": "heartgold-soulsilver",
}


def normalize_title(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^A-Z0-9]+", " ", text.upper())
    return f" {text.strip()} "


@dataclass(frozen=True)
class Detection:
    game_id: str
    version_names: dict[str, str]  # nombres de la versión concreta encontrada (p. ej. Espada / Sword)

    def version_name(self, lang: str) -> str | None:
        return self.version_names.get(lang) or self.version_names.get("en")


class GameDetector:
    def __init__(self, games: list[Game]) -> None:
        # (patrón normalizado, longitud del nombre, id del juego, nombres de la versión);
        # un nombre corto exige "POKEMON " delante
        self._patterns: list[tuple[str, int, str, dict[str, str]]] = []
        game_names = {g.id: g.names for g in games}
        for game in games:
            for names in game.version_names:
                for name in set(names.values()):
                    norm = normalize_title(name).strip()
                    if not norm:
                        continue
                    pattern = f"POKEMON {norm}" if len(norm.replace(" ", "")) <= SHORT_NAME_MAX_LEN else norm
                    self._patterns.append((pattern, len(norm), game.id, names))
        for alias, game_id in ROM_ALIASES.items():
            self._patterns.append((alias, len(alias), game_id, game_names.get(game_id, {})))
        known = {g.id for g in games}
        self._patterns = [p for p in self._patterns if p[2] in known]
        # Los nombres más largos primero: "ROJO FUEGO" antes que "ROJO" (sin contar el prefijo "POKEMON ")
        self._patterns.sort(key=lambda p: p[1], reverse=True)

    def detect_version(self, title: str | None) -> Detection | None:
        if not title:
            return None
        haystack = normalize_title(title)
        for pattern, _, game_id, names in self._patterns:
            if f" {pattern} " in haystack:
                return Detection(game_id, names)
        return None

    def detect(self, title: str | None) -> str | None:
        found = self.detect_version(title)
        return found.game_id if found else None
