"""Dataset local de especies, formas regionales, juegos y cálculo de eficacia de tipos."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from importlib import resources
from pathlib import Path

STAT_ORDER = ("hp", "attack", "defense", "special_attack", "special_defense", "speed")
MULTIPLIER_GROUPS = (4.0, 2.0, 0.5, 0.25, 0.0)
CURRENT_GENERATION = 9
ABILITIES_FROM_GENERATION = 3
HIDDEN_ABILITIES_FROM_GENERATION = 5


class DatasetMissingError(RuntimeError):
    def __init__(self, path: Path | str) -> None:
        super().__init__(
            f"No se encuentra el dataset ({path}). Genéralo con: uv run python tools/build_dataset.py"
        )


def _localized(names: dict[str, str], lang: str, fallback: str) -> str:
    return names.get(lang) or names.get("en") or fallback


@dataclass(frozen=True)
class Ability:
    identifier: str
    names: dict[str, str]
    hidden: bool

    def name(self, lang: str) -> str:
        return _localized(self.names, lang, self.identifier)


@dataclass(frozen=True)
class Form:
    identifier: str
    form: str  # p. ej. "galar", "paldea-combat-breed"
    names: dict[str, str]
    types: tuple[str, ...]
    stats: dict[str, int]
    abilities: tuple[Ability, ...]

    def name(self, lang: str) -> str:
        return _localized(self.names, lang, self.identifier)


@dataclass(frozen=True)
class PastTypes:
    until_generation: int
    types: tuple[str, ...]


@dataclass(frozen=True)
class Species:
    id: int
    identifier: str
    generation: int
    names: dict[str, str]
    types: tuple[str, ...]
    stats: dict[str, int]
    abilities: tuple[Ability, ...]
    past_types: tuple[PastTypes, ...] = ()
    forms: tuple[Form, ...] = ()

    def name(self, lang: str) -> str:
        return _localized(self.names, lang, self.identifier)

    @property
    def stat_total(self) -> int:
        return sum(self.stats.values())

    def types_in(self, generation: int) -> tuple[str, ...]:
        """Tipos de la forma por defecto vigentes en una generación (design.md D3)."""
        applicable = [p for p in self.past_types if p.until_generation >= generation]
        return min(applicable, key=lambda p: p.until_generation).types if applicable else self.types


@dataclass(frozen=True)
class Game:
    id: str
    generation: int
    regional_form: str | None
    names: dict[str, str]
    version_names: tuple[dict[str, str], ...]

    def name(self, lang: str) -> str:
        return _localized(self.names, lang, self.id)


@dataclass(frozen=True)
class OtherForm:
    name: str
    types: tuple[str, ...]


@dataclass(frozen=True)
class SpeciesView:
    """Lo que la ficha muestra de una especie en un juego concreto."""

    species_id: int
    name: str
    form: str | None
    types: tuple[str, ...]
    stats: dict[str, int]
    abilities: tuple[Ability, ...]
    generation: int
    matchups: dict[float, list[str]]
    other_forms: tuple[OtherForm, ...] = field(default_factory=tuple)

    @property
    def stat_total(self) -> int:
        return sum(self.stats.values())


def _abilities(raw: list[dict]) -> tuple[Ability, ...]:
    return tuple(Ability(a["identifier"], a["names"], a["hidden"]) for a in raw)


class Pokedex:
    def __init__(self, data: dict) -> None:
        self.languages: list[str] = data["languages"]
        self.type_names: dict[str, dict[str, str]] = {k: v["names"] for k, v in data["types"].items()}
        self.type_efficacy: dict[str, dict[str, float]] = data["type_efficacy"]
        self.type_generation: dict[str, int] = data.get("type_generation", {})
        self._efficacy_past: list[dict] = data.get("type_efficacy_past", [])
        self.games: list[Game] = [
            Game(
                g["id"],
                g["generation"],
                g.get("regional_form"),
                g.get("names", {}),
                tuple(v.get("names", {}) for v in g.get("versions", [])),
            )
            for g in data.get("games", [])
        ]
        self._games_by_id = {g.id: g for g in self.games}
        self._species: dict[int, Species] = {}
        for s in data["species"]:
            self._species[s["id"]] = Species(
                id=s["id"],
                identifier=s["identifier"],
                generation=s["generation"],
                names=s["names"],
                types=tuple(s["types"]),
                stats=s["stats"],
                abilities=_abilities(s["abilities"]),
                past_types=tuple(PastTypes(p["until_generation"], tuple(p["types"])) for p in s.get("past_types", [])),
                forms=tuple(
                    Form(f["identifier"], f["form"], f["names"], tuple(f["types"]), f["stats"], _abilities(f["abilities"]))
                    for f in s.get("forms", [])
                ),
            )
        self._charts: dict[int, dict[str, dict[str, float]]] = {}

    @classmethod
    def load(cls, path: Path | None = None) -> Pokedex:
        if path is None:
            resource = resources.files("battlelens") / "data" / "pokedex.json"
            if not resource.is_file():
                raise DatasetMissingError(resource)
            return cls(json.loads(resource.read_text(encoding="utf-8")))
        if not path.is_file():
            raise DatasetMissingError(path)
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def __len__(self) -> int:
        return len(self._species)

    def __iter__(self):
        return iter(self._species.values())

    def get_species(self, species_id: int) -> Species:
        return self._species[species_id]

    def get_game(self, game_id: str | None) -> Game | None:
        return self._games_by_id.get(game_id) if game_id else None

    def type_name(self, type_id: str, lang: str) -> str:
        return _localized(self.type_names.get(type_id, {}), lang, type_id)

    # ---- tablas de tipos ---------------------------------------------------

    def type_chart(self, generation: int = CURRENT_GENERATION) -> dict[str, dict[str, float]]:
        """Tabla atacante → defensor → multiplicador vigente en una generación (design.md D3)."""
        if generation not in self._charts:
            existing = [t for t in self.type_efficacy if self.type_generation.get(t, 1) <= generation]
            chart = {a: {d: self.type_efficacy[a].get(d, 1.0) for d in existing} for a in existing}
            overrides: dict[tuple[str, str], tuple[int, float]] = {}
            for row in self._efficacy_past:
                key = (row["attacker"], row["defender"])
                if row["until_generation"] >= generation and key[0] in chart and key[1] in chart:
                    current = overrides.get(key)
                    if current is None or row["until_generation"] < current[0]:
                        overrides[key] = (row["until_generation"], row["factor"])
            for (a, d), (_, factor) in overrides.items():
                chart[a][d] = factor
            self._charts[generation] = chart
        return self._charts[generation]

    def damage_multipliers(
        self, defending_types: tuple[str, ...] | list[str], generation: int = CURRENT_GENERATION
    ) -> dict[str, float]:
        """Multiplicador de daño recibido por cada tipo de ataque existente en la generación."""
        result = {}
        for attacking, row in self.type_chart(generation).items():
            factor = 1.0
            for t in defending_types:
                factor *= row.get(t, 1.0)
            result[attacking] = factor
        return result

    def defensive_matchups(
        self, defending_types: tuple[str, ...] | list[str], generation: int = CURRENT_GENERATION
    ) -> dict[float, list[str]]:
        """Agrupa los tipos de ataque en ×4, ×2, ×½, ×¼ y ×0 (se omite ×1)."""
        groups: dict[float, list[str]] = {m: [] for m in MULTIPLIER_GROUPS}
        for attacking, factor in self.damage_multipliers(defending_types, generation).items():
            if factor in groups:
                groups[factor].append(attacking)
        return groups

    # ---- vista según el juego ----------------------------------------------

    def view(self, species_id: int, game_id: str | None = None, lang: str = "es") -> SpeciesView:
        """Forma, tipos, habilidades y eficacias de una especie en un juego (design.md D1-D3)."""
        species = self.get_species(species_id)
        game = self.get_game(game_id)
        generation = game.generation if game else CURRENT_GENERATION

        form = None
        if game and game.regional_form:
            form = next((f for f in species.forms if f.form.startswith(game.regional_form)), None)

        if form is not None:
            name, types, stats, abilities = form.name(lang), form.types, form.stats, form.abilities
        else:
            name, types, stats, abilities = species.name(lang), species.types_in(generation), species.stats, species.abilities

        if generation < ABILITIES_FROM_GENERATION:
            abilities = ()
        elif generation < HIDDEN_ABILITIES_FROM_GENERATION:
            abilities = tuple(a for a in abilities if not a.hidden)

        others: list[OtherForm] = []
        if form is not None:
            others.append(OtherForm(species.name(lang), species.types_in(generation)))
        others += [OtherForm(f.name(lang), f.types) for f in species.forms if f is not form]

        return SpeciesView(
            species_id=species.id,
            name=name,
            form=form.form if form else None,
            types=types,
            stats=stats,
            abilities=abilities,
            generation=generation,
            matchups=self.defensive_matchups(types, generation),
            other_forms=tuple(others),
        )
