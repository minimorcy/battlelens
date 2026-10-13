"""Detección automática del combate: cuándo reconocer, mostrar y ocultar (spec battle-detection).

Lógica pura, sin Qt ni reloj real: la hora llega como parámetro (design.md D1).
La «clave» de un combate es cualquier valor comparable: el id de una especie o una tupla
(rival, 2.º rival, tu Pokémon). `has_rival(clave)` decide si la clave cuenta como reconocida.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Hashable

import numpy as np

CHANGE_THRESHOLD = 8.0
STABLE_TICKS = 2


class Action(Enum):
    NONE = "none"
    RECOGNIZE = "recognize"
    SHOW = "show"
    HIDE = "hide"


def default_has_rival(key: Hashable | None) -> bool:
    if key is None:
        return False
    if isinstance(key, tuple):
        return any(k is not None for k in key[:2])  # (rival, rival2, own): basta con un rival
    return True


@dataclass
class _Shown:
    key: Hashable
    fingerprint: np.ndarray
    away_since: float | None = None


class BattleDetector:
    def __init__(
        self,
        distance: Callable[[np.ndarray, np.ndarray], float],
        hide_after_seconds: float = 4.0,
        change_threshold: float = CHANGE_THRESHOLD,
        stable_ticks: int = STABLE_TICKS,
        has_rival: Callable[[Hashable | None], bool] = default_has_rival,
    ) -> None:
        self._has_rival = has_rival
        self._distance = distance
        self.hide_after_seconds = hide_after_seconds
        self.change_threshold = change_threshold
        self.stable_ticks = stable_ticks
        self.reset()

    def reset(self) -> None:
        self._last: np.ndarray | None = None
        self._stable = 0
        self._last_attempt: np.ndarray | None = None
        self._shown: _Shown | None = None
        self._hidden_by_user = False

    @property
    def shown_key(self) -> Hashable | None:
        return self._shown.key if self._shown else None

    shown_species = shown_key  # compatibilidad: con claves simples es el id de la especie

    def _differs(self, a: np.ndarray | None, b: np.ndarray | None) -> bool:
        return a is None or b is None or self._distance(a, b) > self.change_threshold

    def on_frame(self, fp: np.ndarray, now: float) -> Action:
        if self._differs(fp, self._last):
            self._stable = 0
        else:
            self._stable += 1
        self._last = fp

        if self._shown is not None and self.hide_after_seconds > 0:
            if self._differs(fp, self._shown.fingerprint):
                if self._shown.away_since is None:
                    self._shown.away_since = now
                elif now - self._shown.away_since >= self.hide_after_seconds:
                    self._shown = None
                    self._hidden_by_user = False
                    return Action.HIDE
            else:
                self._shown.away_since = None

        if self._stable == self.stable_ticks and self._differs(fp, self._last_attempt):
            return Action.RECOGNIZE
        return Action.NONE

    def on_result(self, key: Hashable | None, fp: np.ndarray, now: float) -> Action:
        self._last_attempt = fp
        if not self._has_rival(key):
            return Action.NONE
        if self._shown is not None and self._shown.key == key:
            self._shown.fingerprint = fp
            self._shown.away_since = None
            return Action.NONE
        self._shown = _Shown(key, fp)
        self._hidden_by_user = False
        return Action.SHOW

    def on_manual_result(self, key: Hashable | None, fp: np.ndarray | None) -> None:
        """Un reconocimiento manual también cuenta como mostrado, para no repetirlo en automático."""
        if self._has_rival(key) and fp is not None:
            self._shown = _Shown(key, fp)
            self._last_attempt = fp
            self._hidden_by_user = False

    def on_hidden_by_user(self) -> None:
        # Se mantiene la especie como «mostrada» para no volver a abrir la ficha del mismo rival.
        self._hidden_by_user = True


class RegionWatcher:
    """Vigila una región con su propia huella y avisa cuando se estabiliza en algo nuevo
    (menú de ataques, add-own-moves D3); no oculta ni muestra la ficha."""

    def __init__(
        self,
        distance: Callable[[np.ndarray, np.ndarray], float],
        change_threshold: float = CHANGE_THRESHOLD,
        stable_ticks: int = STABLE_TICKS,
    ) -> None:
        self._distance = distance
        self.change_threshold = change_threshold
        self.stable_ticks = stable_ticks
        self.reset()

    def reset(self) -> None:
        self._last: np.ndarray | None = None
        self._stable = 0
        self._last_read: np.ndarray | None = None

    def _differs(self, a: np.ndarray | None, b: np.ndarray | None) -> bool:
        return a is None or b is None or self._distance(a, b) > self.change_threshold

    def on_frame(self, fp: np.ndarray) -> bool:
        """True si toca leer la región: estable durante `stable_ticks` ciclos y distinta de la última leída."""
        self._stable = 0 if self._differs(fp, self._last) else self._stable + 1
        self._last = fp
        return self._stable == self.stable_ticks and self._differs(fp, self._last_read)

    def attempted(self, fp: np.ndarray) -> None:
        self._last_read = fp
