import urllib.error
from datetime import datetime, timedelta, timezone

import pytest

from battlelens.core.config import AppState, Config, ConfigError, load_config, render_config, save_config
from battlelens.core.updates import Release, check_latest, due, is_newer, parse_version


# ---- configuración --------------------------------------------------------------

def test_ida_y_vuelta(tmp_path):
    cfg = Config(hotkey_recognize="Ctrl+Alt+R", threshold=72.5, debug=True, language="en",
                 auto_hide_seconds=3, detection_enabled=False, detection_interval_ms=750,
                 detection_hide_after_seconds=0, updates_check=False)
    path = tmp_path / "config.toml"
    save_config(path, cfg)
    assert load_config(path) == cfg
    text = path.read_text(encoding="utf-8")
    assert "# Puntuación mínima" in text and 'language = "en"' in text and "check = false" in text


def test_plantilla_por_defecto_es_valida():
    assert Config.from_toml(render_config(Config())) == Config()


def test_updates_por_defecto(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("[overlay]\nlanguage = \"es\"\n", encoding="utf-8")
    assert load_config(path).updates_check is True


def test_idioma_no_valido(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("[overlay]\nlanguage = \"jp\"\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(path)


def test_guardar_valida(tmp_path):
    with pytest.raises(ConfigError):
        save_config(tmp_path / "config.toml", Config(threshold=150))
    assert not (tmp_path / "config.toml").exists()


def test_estado_ultima_comprobacion(tmp_path):
    AppState(last_update_check="2026-10-13T10:00:00+00:00").save(tmp_path / "s.json")
    assert AppState.load(tmp_path / "s.json").last_update_check == "2026-10-13T10:00:00+00:00"


# ---- versiones --------------------------------------------------------------------

@pytest.mark.parametrize(
    ("candidate", "current", "newer"),
    [("v0.3.0", "0.2.0", True), ("0.2.0", "0.2.0", False), ("v0.1.9", "0.2.0", False),
     ("0.10.0", "0.9.3", True), ("v1.0", "0.2.0", False), ("nightly", "0.2.0", False), (None, "0.2.0", False),
     ("v0.2.1", "0.2.0+dev", True)],
)
def test_is_newer(candidate, current, newer):
    assert is_newer(candidate, current) is newer


def test_parse_version():
    assert parse_version("v1.2.3") == (1, 2, 3) and parse_version("1.2") is None


def test_hay_version_nueva():
    release = check_latest("0.2.0", lambda: {"tag_name": "v0.3.0", "html_url": "https://x/releases/v0.3.0"})
    assert release == Release("0.3.0", "https://x/releases/v0.3.0")


def test_version_al_dia():
    assert check_latest("0.2.0", lambda: {"tag_name": "v0.2.0"}) is None


@pytest.mark.parametrize(
    "error",
    [urllib.error.HTTPError("u", 404, "Not Found", {}, None), urllib.error.URLError("sin red"), TimeoutError()],
)
def test_errores_silenciosos(error):
    def fetch():
        raise error

    assert check_latest("0.2.0", fetch) is None


def test_json_inesperado():
    assert check_latest("0.2.0", lambda: ["no", "es", "un", "objeto"]) is None


def test_comprobacion_reciente():
    now = datetime(2026, 10, 13, 12, tzinfo=timezone.utc)
    assert due(None, now)
    assert not due((now - timedelta(hours=3)).isoformat(), now)
    assert due((now - timedelta(hours=25)).isoformat(), now)
    assert due("basura", now)


def test_modo_y_atajo_de_modo(tmp_path):
    path = tmp_path / "config.toml"
    cfg = Config(overlay_mode="competitive", hotkey_toggle_mode="Ctrl+Alt+K")
    save_config(path, cfg)
    assert load_config(path) == cfg
    assert 'mode = "competitive"' in path.read_text(encoding="utf-8")


def test_modo_por_defecto_y_no_valido(tmp_path):
    assert Config().overlay_mode == "normal" and Config().hotkey_toggle_mode == "Ctrl+Alt+M"
    path = tmp_path / "config.toml"
    path.write_text('[overlay]\nmode = "pro"\n', encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(path)
