import json
import logging

import pytest

from battlelens.core.config import AppState, Config, ConfigError, load_config
from battlelens.core.profiles import (
    Profile,
    ProfileError,
    ProfileStore,
    Region,
    RegionTooSmallError,
)


def test_region_relativa_ejemplo_spec():
    r = Region.from_pixels(480, 40, 160, 24, 960, 640)
    assert r.x == pytest.approx(0.5, abs=1e-4)
    assert r.y == pytest.approx(0.0625, abs=1e-4)
    assert r.width == pytest.approx(0.1667, abs=1e-4)
    assert r.height == pytest.approx(0.0375, abs=1e-4)


def test_region_escala_con_la_ventana():
    r = Region.from_pixels(480, 40, 160, 24, 960, 640)
    assert r.to_pixels(960, 640) == (480, 40, 160, 24)
    assert r.to_pixels(1440, 960) == (720, 60, 240, 36)


@pytest.mark.parametrize(("w", "h"), [(7, 20), (100, 7)])
def test_region_demasiado_pequena(w, h):
    with pytest.raises(RegionTooSmallError):
        Region.from_pixels(0, 0, w, h, 960, 640)


@pytest.mark.parametrize("args", [(-0.1, 0, 0.5, 0.5), (0.8, 0, 0.5, 0.5), (0, 0, 0, 0.5)])
def test_region_invalida(args):
    with pytest.raises(ProfileError):
        Region(*args)


def _profile(name="Esmeralda"):
    return Profile(name, Region(0.5, 0.0625, 0.1667, 0.0375))


def test_persistencia_ida_y_vuelta(tmp_path):
    store = ProfileStore(tmp_path)
    p = _profile()
    store.save(p)

    reloaded = ProfileStore(tmp_path)
    reloaded.load()
    assert reloaded.profiles[p.id] == p
    assert reloaded.active == p


def test_archivo_corrupto_se_ignora(tmp_path, caplog):
    store = ProfileStore(tmp_path)
    good = _profile()
    store.save(good)
    (tmp_path / "roto.json").write_text("{no es json", encoding="utf-8")
    (tmp_path / "esquema.json").write_text(json.dumps({"name": "x"}), encoding="utf-8")

    with caplog.at_level(logging.WARNING):
        store.load()
    assert list(store.profiles) == [good.id]
    assert "roto.json" in caplog.text and "esquema.json" in caplog.text


def test_perfil_activo_preferido_y_cambio(tmp_path):
    store = ProfileStore(tmp_path)
    a, b = _profile("A"), _profile("B")
    store.save(a)
    store.save(b)
    store.load(preferred_active=b.id)
    assert store.active == b
    store.set_active(a.id)
    assert store.active == a


def test_eliminar_activo_selecciona_otro(tmp_path):
    store = ProfileStore(tmp_path)
    a, b = _profile("A"), _profile("B")
    store.save(a)
    store.save(b)
    store.set_active(a.id)
    store.delete(a.id)
    assert not (tmp_path / f"{a.id}.json").exists()
    assert store.active == b
    store.delete(b.id)
    assert store.active is None


def test_recalibrar_mantiene_identidad(tmp_path):
    store = ProfileStore(tmp_path)
    p = _profile()
    store.save(p)
    updated = p.with_region(Region(0.1, 0.1, 0.2, 0.05))
    store.save(updated)
    assert store.profiles[p.id].name == p.name
    assert store.profiles[p.id].region == Region(0.1, 0.1, 0.2, 0.05)


def test_config_por_defecto_se_crea(tmp_path):
    path = tmp_path / "config.toml"
    cfg = load_config(path)
    assert path.exists()
    assert cfg == Config()
    assert load_config(path) == Config()


def test_config_personalizada(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('[recognition]\nthreshold = 70\ndebug = true\n[overlay]\nlanguage = "en"\n', encoding="utf-8")
    cfg = load_config(path)
    assert cfg.threshold == 70 and cfg.debug and cfg.language == "en"
    assert cfg.hotkey_recognize == "Ctrl+Alt+P"


@pytest.mark.parametrize("text", ["[recognition]\nthreshold = 150\n", "no = [toml"])
def test_config_invalida(tmp_path, text):
    path = tmp_path / "config.toml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(path)


def test_estado_ida_y_vuelta(tmp_path):
    path = tmp_path / "state.json"
    assert AppState.load(path) == AppState()
    AppState(last_window_exe="mGBA.exe", active_profile="abc", overlay_pos=[10, 20]).save(path)
    assert AppState.load(path).overlay_pos == [10, 20]
    path.write_text("basura", encoding="utf-8")
    assert AppState.load(path) == AppState()


def test_perfil_antiguo_sin_juego(tmp_path):
    legacy = {
        "name": "Viejo", "region": {"x": 0.1, "y": 0.1, "width": 0.2, "height": 0.05},
        "ocr_languages": ["es"], "id": "old00001", "created_at": "2026-10-13T00:00:00+00:00",
    }
    (tmp_path / "old00001.json").write_text(json.dumps(legacy), encoding="utf-8")
    store = ProfileStore(tmp_path)
    store.load()
    assert store.profiles["old00001"].game is None


def test_juego_ida_y_vuelta_y_busqueda(tmp_path):
    store = ProfileStore(tmp_path)
    esm = _profile("Esmeralda").with_game("emerald")
    esp1 = _profile("Espada A").with_game("sword-shield")
    esp2 = _profile("Espada B").with_game("sword-shield")
    for p in (esm, esp1, esp2):
        store.save(p)
    reloaded = ProfileStore(tmp_path)
    reloaded.load()
    assert reloaded.profiles[esm.id].game == "emerald"
    reloaded.set_active(esm.id)
    assert reloaded.find_by_game("sword-shield") == esp1  # el primero por nombre
    reloaded.set_active(esp2.id)
    assert reloaded.find_by_game("sword-shield") == esp2  # se mantiene el activo si ya es de ese juego
    assert reloaded.find_by_game("platinum") is None
