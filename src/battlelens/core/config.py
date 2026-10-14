"""Configuración del usuario (config.toml) y estado de la aplicación (state.json)."""

from __future__ import annotations

import json
import logging
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path

from ..i18n import _
from .storage import write_json_atomic, write_text_atomic

log = logging.getLogger(__name__)

CONFIG_TEMPLATE = """\
# Configuración de BattleLens.
# Puedes editar este archivo (los cambios se aplican al reiniciar) o usar «Ajustes…» en la bandeja,
# que lo reescribe con estos mismos comentarios.

[interface]
# Idioma de menús, avisos y textos de la ficha: "auto" (el de Windows), "es" o "en".
language = {interface_language}

[hotkeys]
# Combinaciones con al menos un modificador (Ctrl, Alt, Shift, Win).
# Las teclas F solas no se permiten: los emuladores las usan para los estados guardados.
recognize = {hotkey_recognize}
calibrate = {hotkey_calibrate}
hide = {hotkey_hide}
# Cambia entre la ficha Normal y la Competitiva.
toggle_mode = {hotkey_toggle_mode}
# Alterna la forma del rival (Megaevoluciones, Rotom, Deoxys...).
cycle_form = {hotkey_cycle_form}
# Muestra u oculta la ficha del stream (modo stream).
toggle_stream = {hotkey_toggle_stream}

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
# Ficha "normal" (compacta: aventura y captura) o "competitive" (todos los datos de combate).
mode = {overlay_mode}
# Idioma de la ficha: es, en, fr, de, it.
language = {language}
# Segundos hasta ocultar el overlay automáticamente (0 = no se oculta solo).
auto_hide_seconds = {auto_hide_seconds}

[stream]
# Fuente de navegador para OBS en http://localhost:<port>/ (solo en este PC).
enabled = {stream_enabled}
# Puerto local (1024-65535).
port = {stream_port}
# Ficha del stream: "normal" o "competitive", independiente de la tuya.
card_mode = {stream_card_mode}

[updates]
# Comprueba una vez al día si hay una versión nueva en GitHub (única conexión de la app).
check = {updates_check}
"""
LANGUAGES = ("es", "en", "fr", "de", "it")
MODES = ("normal", "competitive")
INTERFACE_LANGUAGES = ("auto", "es", "en")


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
    hotkey_toggle_mode: str = "Ctrl+Alt+M"
    overlay_mode: str = "normal"
    hotkey_cycle_form: str = "Ctrl+Alt+F"
    hotkey_toggle_stream: str = "Ctrl+Alt+S"
    stream_enabled: bool = False
    stream_port: int = 17320
    stream_card_mode: str = "normal"
    interface_language: str = "auto"

    @classmethod
    def from_toml(cls, text: str) -> Config:
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
            raise ConfigError(_("config.toml no es TOML válido: {error}", error=exc)) from exc
        hk = data.get("hotkeys", {})
        rec = data.get("recognition", {})
        ov = data.get("overlay", {})
        det = data.get("detection", {})
        upd = data.get("updates", {})
        st = data.get("stream", {})
        ui = data.get("interface", {})
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
            hotkey_toggle_mode=hk.get("toggle_mode", default.hotkey_toggle_mode),
            overlay_mode=ov.get("mode", default.overlay_mode),
            hotkey_cycle_form=hk.get("cycle_form", default.hotkey_cycle_form),
            hotkey_toggle_stream=hk.get("toggle_stream", default.hotkey_toggle_stream),
            stream_enabled=st.get("enabled", default.stream_enabled),
            stream_port=st.get("port", default.stream_port),
            stream_card_mode=st.get("card_mode", default.stream_card_mode),
            interface_language=ui.get("language", default.interface_language),
        )
        cfg._validate()
        return cfg

    def _validate(self) -> None:
        for name in ("hotkey_recognize", "hotkey_calibrate", "hotkey_hide", "language"):
            if not isinstance(getattr(self, name), str):
                raise ConfigError(_("{name} debe ser un texto", name=name))
        if not isinstance(self.threshold, (int, float)) or not 0 <= self.threshold <= 100:
            raise ConfigError(_("{key} debe estar entre {low} y {high}", key="recognition.threshold", low=0, high=100))
        if self.overlay_mode not in MODES:
            raise ConfigError(_("{key} debe ser uno de: {values}", key="overlay.mode", values=", ".join(MODES)))
        if not isinstance(self.hotkey_toggle_mode, str):
            raise ConfigError(_("{name} debe ser un texto", name="hotkeys.toggle_mode"))
        if not isinstance(self.hotkey_cycle_form, str):
            raise ConfigError(_("{name} debe ser un texto", name="hotkeys.cycle_form"))
        if not isinstance(self.hotkey_toggle_stream, str):
            raise ConfigError(_("{name} debe ser un texto", name="hotkeys.toggle_stream"))
        if not isinstance(self.stream_enabled, bool):
            raise ConfigError(_("{key} debe ser true o false", key="stream.enabled"))
        if not isinstance(self.stream_port, int) or isinstance(self.stream_port, bool) or not 1024 <= self.stream_port <= 65535:
            raise ConfigError(_("{key} debe ser un entero entre {low} y {high}", key="stream.port", low=1024, high=65535))
        if self.interface_language not in INTERFACE_LANGUAGES:
            raise ConfigError(_("{key} debe ser uno de: {values}", key="interface.language", values=", ".join(INTERFACE_LANGUAGES)))
        if self.stream_card_mode not in MODES:
            raise ConfigError(_("{key} debe ser uno de: {values}", key="stream.card_mode", values=", ".join(MODES)))
        if self.language not in LANGUAGES:
            raise ConfigError(_("{key} debe ser uno de: {values}", key="overlay.language", values=", ".join(LANGUAGES)))
        if not isinstance(self.updates_check, bool):
            raise ConfigError(_("{key} debe ser true o false", key="updates.check"))
        if not isinstance(self.debug, bool):
            raise ConfigError(_("{key} debe ser true o false", key="recognition.debug"))
        if not isinstance(self.auto_hide_seconds, (int, float)) or self.auto_hide_seconds < 0:
            raise ConfigError(_("{key} debe ser un número >= 0", key="overlay.auto_hide_seconds"))
        if not isinstance(self.detection_enabled, bool):
            raise ConfigError(_("{key} debe ser true o false", key="detection.enabled"))
        if not isinstance(self.detection_interval_ms, int) or not 200 <= self.detection_interval_ms <= 5000:
            raise ConfigError(_("{key} debe ser un entero entre {low} y {high}", key="detection.interval_ms", low=200, high=5000))
        if not isinstance(self.detection_hide_after_seconds, (int, float)) or self.detection_hide_after_seconds < 0:
            raise ConfigError(_("{key} debe ser un número >= 0", key="detection.hide_after_seconds"))


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
