"""Dataset local de especies y cálculo de eficacia de tipos."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

STAT_ORDER = ("hp", "attack", "defense", "special_attack", "special_defense", "speed")
MULTIPLIER_GROUPS = (4.0, 2.0, 0.5, 0.25, 0.0)


class DatasetMissingError(RuntimeError):
    def __init__(self, path: Path | str) -> None:
        super().__init__(
            f"No se encuentra el dataset ({path}). Genéralo con: uv run python tools/build_dataset.py"
        )


@dataclass(frozen=True)
class Ability:
    identifier: str
    names: dict[str, str]
    hidden: bool

    def name(self, lang: str) -> str:
        return self.names.get(lang) or self.names.get("en") or self.identifier


@dataclass(frozen=True)
class Species:
    id: int
    identifier: str
    generation: int
    names: dict[str, str]
    types: tuple[str, ...]
    stats: dict[str, int]
    abilities: tuple[Ability, ...]

    def name(self, lang: str) -> str:
        return self.names.get(lang) or self.names.get("en") or self.identifier

    @property
    def stat_total(self) -> int:
        return sum(self.stats.values())


class Pokedex:
    def __init__(self, data: dict) -> None:
        self.languages: list[str] = data["languages"]
        self.type_names: dict[str, dict[str, str]] = {k: v["names"] for k, v in data["types"].items()}
        self.type_efficacy: dict[str, dict[str, float]] = data["type_efficacy"]
        self._species: dict[int, Species] = {}
        for s in data["species"]:
            self._species[s["id"]] = Species(
                id=s["id"],
                identifier=s["identifier"],
                generation=s["generation"],
                names=s["names"],
                types=tuple(s["types"]),
                stats=s["stats"],
                abilities=tuple(Ability(a["identifier"], a["names"], a["hidden"]) for a in s["abilities"]),
            )

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

    def type_name(self, type_id: str, lang: str) -> str:
        names = self.type_names.get(type_id, {})
        return names.get(lang) or names.get("en") or type_id

    def damage_multipliers(self, defending_types: tuple[str, ...] | list[str]) -> dict[str, float]:
        """Multiplicador de daño recibido por cada tipo de ataque."""
        result = {}
        for attacking, row in self.type_efficacy.items():
            factor = 1.0
            for t in defending_types:
                factor *= row.get(t, 1.0)
            result[attacking] = factor
        return result

    def defensive_matchups(self, defending_types: tuple[str, ...] | list[str]) -> dict[float, list[str]]:
        """Agrupa los tipos de ataque en ×4, ×2, ×½, ×¼ y ×0 (se omite ×1)."""
        groups: dict[float, list[str]] = {m: [] for m in MULTIPLIER_GROUPS}
        for attacking, factor in self.damage_multipliers(defending_types).items():
            if factor in groups:
                groups[factor].append(attacking)
        return groups
