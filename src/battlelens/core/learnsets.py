"""Movimientos por nivel (learnsets.json, carga diferida) y movimientos probables (spec competitive-data)."""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from importlib import resources

PROBABLE_MOVES = 4


@dataclass(frozen=True)
class Move:
    id: int
    identifier: str
    names: dict[str, str]
    type: str | None
    category: str | None  # "physical" | "special" | "status"
    power: int | None
    accuracy: int | None
    pp: int | None
    priority: int
    level: int

    def name(self, lang: str) -> str:
        return self.names.get(lang) or self.names.get("en") or self.identifier


class LearnsetsMissingError(RuntimeError):
    pass


class Learnsets:
    """Se carga una sola vez, la primera vez que se usa (add-display-modes D3)."""

    _instance: Learnsets | None = None
    _lock = threading.Lock()

    def __init__(self, data: dict) -> None:
        self._moves: dict[str, dict] = data["moves"]
        self._sets: list[list[list[int]]] = data["sets"]
        self._pokemon: dict[str, dict[str, int]] = data["pokemon"]
        # grupo de versiones → (generación, orden)
        self._vg: dict[str, tuple[int, int]] = {k: tuple(v) for k, v in data["version_groups"].items()}

    @classmethod
    def get(cls) -> Learnsets:
        with cls._lock:
            if cls._instance is None:
                resource = resources.files("battlelens") / "data" / "learnsets.json"
                if not resource.is_file():
                    raise LearnsetsMissingError("Falta learnsets.json: genera los datos con tools/build_dataset.py")
                cls._instance = cls(json.loads(resource.read_text(encoding="utf-8")))
            return cls._instance

    @classmethod
    def is_loaded(cls) -> bool:
        return cls._instance is not None

    def choose_version_group(self, pokemon: str, game: str | None, generation: int | None) -> str | None:
        """Juego del perfil; si no hay datos, el más reciente de su generación; si no, el más reciente."""
        available = self._pokemon.get(pokemon, {})
        if not available:
            return None
        if game in available:
            return game
        ordered = sorted(available, key=lambda vg: self._vg.get(vg, (0, 0)), reverse=True)
        if generation is not None:
            same_gen = [vg for vg in ordered if self._vg.get(vg, (0, 0))[0] == generation]
            if same_gen:
                return same_gen[0]
            older = [vg for vg in ordered if self._vg.get(vg, (0, 0))[0] <= generation]
            if older:
                return older[0]
        return ordered[0]

    def level_up_moves(self, pokemon: str, version_group: str) -> list[Move]:
        index = self._pokemon.get(pokemon, {}).get(version_group)
        if index is None:
            return []
        result = []
        for level, move_id in self._sets[index]:
            m = self._moves[str(move_id)]
            result.append(
                Move(move_id, m["identifier"], m["names"], m["type"], m["class"], m["power"],
                     m["accuracy"], m["pp"], m["priority"], level)
            )
        return result

    def probable_moves(
        self, pokemon: str, level: int, game: str | None = None, generation: int | None = None
    ) -> list[Move]:
        """Últimos 4 movimientos distintos aprendidos por nivel hasta `level` (D4), en orden de aprendizaje."""
        vg = self.choose_version_group(pokemon, game, generation)
        if vg is None:
            return []
        learned: list[Move] = []
        for move in sorted(self.level_up_moves(pokemon, vg), key=lambda m: m.level):
            if move.level > level:
                break
            learned = [m for m in learned if m.id != move.id] + [move]
        return learned[-PROBABLE_MOVES:]
