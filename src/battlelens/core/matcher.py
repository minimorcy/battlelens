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
# Nombre que solo existe en un idioma distinto del del juego (p. ej. «Blanas», Nuzleaf en alemán, frente a
# una mala lectura de «Yamask» en un juego en español): mejor «no reconocido» que una ficha equivocada.
FOREIGN_PENALTY = 10.0


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
        self._languages: dict[str, set[str]] = {}  # idiomas en los que existe cada nombre
        for species in pokedex:
            for lang in MATCH_LANGUAGES:
                name = species.names.get(lang)
                if name:
                    key = normalize_name(name)
                    self._index.setdefault(key, species.id)
                    self._languages.setdefault(key, set()).add(lang)
        self._collapsed: dict[str, str] = {}  # nombre con las confusiones unificadas → nombre del índice
        for name in self._index:
            self._collapsed.setdefault(name.translate(PIXEL_CONFUSIONS), name)

    def match(self, raw_text: str, languages: tuple[str, ...] = ()) -> MatchResult:
        """`languages`: los del OCR del perfil (el idioma del juego); vacío, todos los idiomas valen igual."""
        wanted = {lang.split("-")[0].lower() for lang in languages}

        def foreign(name: str) -> float:
            return FOREIGN_PENALTY if wanted and not wanted & self._languages[name] else 0.0

        best: tuple[str, float] | None = None
        for query, penalty in name_candidates(raw_text):  # el texto completo va primero y gana los empates
            for found, score, _ in process.extract(query, self._index.keys(), scorer=fuzz.ratio, limit=5):
                score -= penalty + foreign(found)
                if best is None or score > best[1]:
                    best = (found, score)
            for found, score, _ in process.extract(query.translate(PIXEL_CONFUSIONS), self._collapsed.keys(),
                                                   scorer=fuzz.ratio, limit=5):
                name = self._collapsed[found]
                score -= penalty + CONFUSION_PENALTY + foreign(name)
                if best is None or score > best[1]:
                    best = (name, score)
        if best is None:
            return MatchResult(None, 0.0, raw_text)
        name, score = best
        if score < self.threshold:
            return MatchResult(None, score, raw_text, name)
        return MatchResult(self._index[name], score, raw_text, name)
