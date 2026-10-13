"""Configuración del usuario (config.toml) y estado de la aplicación (state.json)."""

from __future__ import annotations

import json
import logging
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .storage import write_json_atomic, write_text_atomic

log = logging.getLogger(__name__)

CONFIG_TEMPLATE = """\
# Configuración de BattleLens.
# Puedes editar este archivo (los cambios se aplican al reiniciar) o usar «Ajustes…» en la bandeja,
# que lo reescribe con estos mismos comentarios.

[hotkeys]
# Combinaciones con al menos un modificador (Ctrl, Alt, Shift, Win).
# Las teclas F solas no se permiten: los emuladores las usan para los estados guardados.
recognize = {hotkey_recognize}
calibrate = {hotkey_calibrate}
hide = {hotkey_hide}

[recognition]
# Puntuación mínima (0-100) para dar por reconocido un nombre.
threshold = {threshold}
# Guarda recortes e imágenes preprocesadas en la carpeta debug/.
debug = {debug}

[detection]
# Reconoce al rival automáticamente al entrar en combate (también se activa/desactiva desde la bandeja).
enabled = {detection_enabled}
# Cada cuántos milisegundos se vigila la región del nombre (200-5000).
interval_ms = {detection_interval_ms}
# Segundos sin ver al rival hasta ocultar la ficha al terminar el combate (0 = no se oculta sola).
hide_after_seconds = {detection_hide_after_seconds}

[overlay]
# Idioma de la ficha: es, en, fr, de, it.
language = {language}
# Segundos hasta ocultar el overlay automáticamente (0 = no se oculta solo).
auto_hide_seconds = {auto_hide_seconds}

[updates]
# Comprueba una vez al día si hay una versión nueva en GitHub (única conexión de la app).
check = {updates_check}
"""
LANGUAGES = ("es", "en", "fr", "de", "it")


def _toml_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)  # cadena básica TOML válida
    return repr(value)


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
    detection_enabled: bool = True
    detection_interval_ms: int = 500
    detection_hide_after_seconds: float = 4.0
    updates_check: bool = True

    @classmethod
    def from_toml(cls, text: str) -> Config:
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
            raise ConfigError(f"config.toml no es TOML válido: {exc}") from exc
        hk = data.get("hotkeys", {})
        rec = data.get("recognition", {})
        ov = data.get("overlay", {})
        det = data.get("detection", {})
        upd = data.get("updates", {})
        default = cls()
        cfg = cls(
            hotkey_recognize=hk.get("recognize", default.hotkey_recognize),
            hotkey_calibrate=hk.get("calibrate", default.hotkey_calibrate),
            hotkey_hide=hk.get("hide", default.hotkey_hide),
            threshold=rec.get("threshold", default.threshold),
            debug=rec.get("debug", default.debug),
            language=ov.get("language", default.language),
            auto_hide_seconds=ov.get("auto_hide_seconds", default.auto_hide_seconds),
            detection_enabled=det.get("enabled", default.detection_enabled),
            detection_interval_ms=det.get("interval_ms", default.detection_interval_ms),
            detection_hide_after_seconds=det.get("hide_after_seconds", default.detection_hide_after_seconds),
            updates_check=upd.get("check", default.updates_check),
        )
        cfg._validate()
        return cfg

    def _validate(self) -> None:
        for name in ("hotkey_recognize", "hotkey_calibrate", "hotkey_hide", "language"):
            if not isinstance(getattr(self, name), str):
                raise ConfigError(f"{name} debe ser un texto")
        if not isinstance(self.threshold, (int, float)) or not 0 <= self.threshold <= 100:
            raise ConfigError("recognition.threshold debe estar entre 0 y 100")
        if self.language not in LANGUAGES:
            raise ConfigError(f"overlay.language debe ser uno de: {', '.join(LANGUAGES)}")
        if not isinstance(self.updates_check, bool):
            raise ConfigError("updates.check debe ser true o false")
        if not isinstance(self.debug, bool):
            raise ConfigError("recognition.debug debe ser true o false")
        if not isinstance(self.auto_hide_seconds, (int, float)) or self.auto_hide_seconds < 0:
            raise ConfigError("overlay.auto_hide_seconds debe ser un número >= 0")
        if not isinstance(self.detection_enabled, bool):
            raise ConfigError("detection.enabled debe ser true o false")
        if not isinstance(self.detection_interval_ms, int) or not 200 <= self.detection_interval_ms <= 5000:
            raise ConfigError("detection.interval_ms debe ser un entero entre 200 y 5000")
        if not isinstance(self.detection_hide_after_seconds, (int, float)) or self.detection_hide_after_seconds < 0:
            raise ConfigError("detection.hide_after_seconds debe ser un número >= 0")


def render_config(cfg: Config) -> str:
    """config.toml con los comentarios de la plantilla y los valores de `cfg` (design.md D1)."""
    return CONFIG_TEMPLATE.format(**{k: _toml_value(v) for k, v in asdict(cfg).items()})


DEFAULT_CONFIG_TOML = render_config(Config())


def save_config(path: Path, cfg: Config) -> None:
    cfg._validate()
    write_text_atomic(path, render_config(cfg))


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
    auto_detect: bool | None = None  # conmutador de la bandeja; tiene prioridad sobre detection.enabled
    last_update_check: str | None = None  # ISO 8601 de la última consulta a GitHub

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
