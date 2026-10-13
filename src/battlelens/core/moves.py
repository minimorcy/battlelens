"""Movimientos de tu Pokémon: lectura del menú de ataques y memoria por especie (spec own-moves)."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from rapidfuzz import fuzz, process

from .learnsets import Move
from .normalize import clean_text
from .storage import write_json_atomic

log = logging.getLogger(__name__)

MOVE_THRESHOLD = 80.0
MIN_MOVES = 2
MAX_MOVES = 4
MAX_WINDOW_WORDS = 3
MIN_WINDOW_CHARS = 4
MATCH_LANGUAGES = ("en", "es", "fr", "de", "it")


class MoveMatcher:
    """Busca nombres de movimiento en el texto del OCR (add-own-moves D2)."""

    def __init__(self, moves: list[Move]) -> None:
        self._moves = {m.identifier: m for m in moves}
        self._index: dict[str, str] = {}
        for move in moves:
            for lang in MATCH_LANGUAGES:
                name = move.names.get(lang)
                if name:
                    self._index.setdefault(clean_text(name), move.identifier)

    def match(self, text: str) -> list[Move]:
        words = text.split()
        candidates: list[tuple[float, int, int, str]] = []  # (puntuación, inicio, fin, movimiento)
        for start in range(len(words)):
            for size in range(1, MAX_WINDOW_WORDS + 1):
                end = start + size
                if end > len(words):
                    break
                query = clean_text(" ".join(words[start:end]))
                if len(query) < MIN_WINDOW_CHARS:
                    continue
                found = process.extractOne(query, self._index.keys(), scorer=fuzz.ratio)
                if found is not None and found[1] >= MOVE_THRESHOLD:
                    candidates.append((found[1], start, end, self._index[found[0]]))
        chosen: list[tuple[int, str]] = []
        used: set[int] = set()
        for score, start, end, identifier in sorted(candidates, key=lambda c: (-c[0], -(c[2] - c[1]))):
            span = set(range(start, end))
            if span & used or any(identifier == m for _, m in chosen):
                continue
            chosen.append((start, identifier))
            used |= span
            if len(chosen) == MAX_MOVES:
                break
        return [self._moves[identifier] for _, identifier in sorted(chosen)]


class MoveMemory:
    """Movimientos leídos por perfil y especie, en moves.json (add-own-moves D4)."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._data: dict[str, dict[str, list[str]]] = {}
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                self._data = raw
        except FileNotFoundError:
            pass
        except (OSError, ValueError) as exc:
            log.warning("moves.json ignorado: %s", exc)

    def get(self, profile_id: str, species_id: int) -> list[str]:
        return list(self._data.get(profile_id, {}).get(str(species_id), []))

    def store(self, profile_id: str, species_id: int, moves: list[str]) -> bool:
        """Guarda los movimientos de una especie; devuelve si han cambiado."""
        if self.get(profile_id, species_id) == list(moves):
            return False
        self._data.setdefault(profile_id, {})[str(species_id)] = list(moves)
        try:
            write_json_atomic(self.path, self._data)
        except OSError as exc:
            log.warning("No se pudo guardar moves.json: %s", exc)
        return True
