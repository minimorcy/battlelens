"""Resolución del texto del OCR a una especie mediante coincidencia aproximada."""

from __future__ import annotations

from dataclasses import dataclass

from rapidfuzz import fuzz, process

from .normalize import name_candidates, normalize_name
from .pokedex import Pokedex

DEFAULT_THRESHOLD = 80.0
# Letras que el OCR confunde en las fuentes pixeladas de GBA/DS («A» leída como «R», «D» como «O»):
# se compara también con ellas unificadas, con una pequeña penalización (add-game-presets).
PIXEL_CONFUSIONS = str.maketrans("AD", "RO")
CONFUSION_PENALTY = 3.0
MATCH_LANGUAGES = ("en", "es", "fr", "de", "it")


@dataclass(frozen=True)
class MatchResult:
    species_id: int | None
    score: float
    raw_text: str
    matched_name: str | None = None

    @property
    def recognized(self) -> bool:
        return self.species_id is not None


class NameMatcher:
    def __init__(self, pokedex: Pokedex, threshold: float = DEFAULT_THRESHOLD) -> None:
        self.threshold = threshold
        self._index: dict[str, int] = {}
        for species in pokedex:
            for lang in MATCH_LANGUAGES:
                name = species.names.get(lang)
                if name:
                    self._index.setdefault(normalize_name(name), species.id)
        self._collapsed: dict[str, str] = {}  # nombre con las confusiones unificadas → nombre del índice
        for name in self._index:
            self._collapsed.setdefault(name.translate(PIXEL_CONFUSIONS), name)

    def match(self, raw_text: str) -> MatchResult:
        best: tuple[str, float] | None = None
        for query, penalty in name_candidates(raw_text):  # el texto completo va primero y gana los empates
            found = process.extractOne(query, self._index.keys(), scorer=fuzz.ratio)
            if found is not None and (best is None or found[1] - penalty > best[1]):
                best = (found[0], found[1] - penalty)
            collapsed = process.extractOne(query.translate(PIXEL_CONFUSIONS), self._collapsed.keys(), scorer=fuzz.ratio)
            if collapsed is not None:
                score = collapsed[1] - penalty - CONFUSION_PENALTY
                if best is None or score > best[1]:
                    best = (self._collapsed[collapsed[0]], score)
        if best is None:
            return MatchResult(None, 0.0, raw_text)
        name, score = best
        if score < self.threshold:
            return MatchResult(None, score, raw_text, name)
        return MatchResult(self._index[name], score, raw_text, name)
