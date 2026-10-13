"""Configuración del usuario (config.toml) y estado de la aplicación (state.json)."""

from __future__ import annotations

import json
import logging
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .storage import write_json_atomic, write_text_atomic

log = logging.getLogger(__name__)

DEFAULT_CONFIG_TOML = """\
# Configuración de BattleLens.
# Los cambios se aplican al reiniciar la aplicación.

[hotkeys]
# Combinaciones con al menos un modificador (Ctrl, Alt, Shift, Win).
# Las teclas F solas no se permiten: los emuladores las usan para los estados guardados.
recognize = "Ctrl+Alt+P"
calibrate = "Ctrl+Alt+C"
hide = "Ctrl+Alt+H"

[recognition]
# Puntuación mínima (0-100) para dar por reconocido un nombre.
threshold = 80
# Guarda recortes e imágenes preprocesadas en la carpeta debug/.
debug = false

[overlay]
# Idioma de la ficha: es, en, fr, de, it.
language = "es"
# Segundos hasta ocultar el overlay automáticamente (0 = no se oculta solo).
auto_hide_seconds = 0
"""


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Config:
    hotkey_recognize: str = "Ctrl+Alt+P"
    hotkey_calibrate: str = "Ctrl+Alt+C"
    hotkey_hide: str = "Ctrl+Alt+H"
    threshold: float = 80.0
    debug: bool = False
    language: str = "es"
    auto_hide_seconds: float = 0.0

    @classmethod
    def from_toml(cls, text: str) -> Config:
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
            raise ConfigError(f"config.toml no es TOML válido: {exc}") from exc
        hk = data.get("hotkeys", {})
        rec = data.get("recognition", {})
        ov = data.get("overlay", {})
        default = cls()
        cfg = cls(
            hotkey_recognize=hk.get("recognize", default.hotkey_recognize),
            hotkey_calibrate=hk.get("calibrate", default.hotkey_calibrate),
            hotkey_hide=hk.get("hide", default.hotkey_hide),
            threshold=rec.get("threshold", default.threshold),
            debug=rec.get("debug", default.debug),
            language=ov.get("language", default.language),
            auto_hide_seconds=ov.get("auto_hide_seconds", default.auto_hide_seconds),
        )
        cfg._validate()
        return cfg

    def _validate(self) -> None:
        for name in ("hotkey_recognize", "hotkey_calibrate", "hotkey_hide", "language"):
            if not isinstance(getattr(self, name), str):
                raise ConfigError(f"{name} debe ser un texto")
        if not isinstance(self.threshold, (int, float)) or not 0 <= self.threshold <= 100:
            raise ConfigError("recognition.threshold debe estar entre 0 y 100")
        if not isinstance(self.debug, bool):
            raise ConfigError("recognition.debug debe ser true o false")
        if not isinstance(self.auto_hide_seconds, (int, float)) or self.auto_hide_seconds < 0:
            raise ConfigError("overlay.auto_hide_seconds debe ser un número >= 0")


def load_config(path: Path) -> Config:
    """Lee config.toml; si no existe, lo crea con los valores por defecto."""
    if not path.exists():
        write_text_atomic(path, DEFAULT_CONFIG_TOML)
        return Config()
    return Config.from_toml(path.read_text(encoding="utf-8"))


@dataclass
class AppState:
    last_window_exe: str | None = None
    last_window_title: str | None = None
    active_profile: str | None = None
    overlay_pos: list[int] | None = field(default=None)

    @classmethod
    def load(cls, path: Path) -> AppState:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            known = {k: data[k] for k in cls.__dataclass_fields__ if k in data}
            return cls(**known)
        except FileNotFoundError:
            return cls()
        except (OSError, ValueError, TypeError) as exc:
            log.warning("state.json ignorado: %s", exc)
            return cls()

    def save(self, path: Path) -> None:
        write_json_atomic(path, asdict(self))
