"""Secciones de la ficha a medida y altura de los bloques plegados (redesign-settings-window D8)."""

import sys
from pathlib import Path

import pytest

from battlelens.core.config import CARD_SECTIONS, Config, ConfigError, render_config

STATIC = Path(__file__).resolve().parent.parent / "src" / "battlelens" / "stream" / "static"
windows = pytest.mark.skipif(sys.platform != "win32", reason="Qt en Windows")


# ---- configuración ------------------------------------------------------------------------

def test_secciones_ocultas_ida_y_vuelta():
    config = Config(hidden_sections_normal=("forms",), hidden_sections_competitive=("stats", "training"))
    text = render_config(config)
    assert 'hidden_competitive = ["stats", "training"]' in text
    assert Config.from_toml(text) == config
    assert config.hidden_sections("competitive") == {"stats", "training"}


def test_ficha_por_defecto():
    """Instalación nueva: Normal solo con eficacias; Competitivo con eficacias y estadísticas."""
    assert Config.from_toml("") == Config()
    visible = {mode: [k for k in CARD_SECTIONS[mode] if k not in Config().hidden_sections(mode)]
               for mode in CARD_SECTIONS}
    assert visible == {"normal": ["eff"], "competitive": ["eff", "stats"]}


@pytest.mark.parametrize("toml", ['[overlay]\nhidden_normal = ["stats"]', '[overlay]\nhidden_competitive = "eff"'])
def test_secciones_no_validas(toml):
    with pytest.raises(ConfigError):
        Config.from_toml(toml)


# ---- ficha privada --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def dex():
    from battlelens.core.pokedex import Pokedex

    return Pokedex.load()


def _visible_blocks(overlay):
    return [b.key for b in overlay.blocks() if not b.isHidden()]


@windows
def test_la_ficha_no_muestra_las_secciones_ocultas(qapp, dex):
    from battlelens.ui.overlay import Overlay

    overlay = Overlay(dex, "es", mode="competitive")
    overlay.show_battle([dex.view(6, "sword-shield")], dex.view(9, "sword-shield"), None, [50], 50)
    qapp.processEvents()
    full = overlay.height()
    assert "stats" in _visible_blocks(overlay)
    overlay.hidden = {"normal": frozenset(), "competitive": frozenset({"stats", "eff"})}
    overlay.show_battle([dex.view(6, "sword-shield")], dex.view(9, "sword-shield"), None, [50], 50)
    qapp.processEvents()
    visible = _visible_blocks(overlay)
    assert "stats" not in visible and "eff" not in visible and "matchup" in visible
    assert overlay.height() < full
    overlay.close()


@windows
def test_plegar_deja_solo_el_titulo(qapp, dex):
    """Un bloque plegado ocupa solo su título: la tarjeta encoge en vez de repartir el hueco."""
    from battlelens.ui.overlay import Overlay

    overlay = Overlay(dex, "es", mode="competitive")
    overlay.show_battle([dex.view(6, "sword-shield")], dex.view(9, "sword-shield"), None, [50], 50)
    qapp.processEvents()
    before = overlay._cards[0].minimumHeight()
    for key in ("eff", "stats", "abilities"):
        overlay.toggle_block(key)
    qapp.processEvents()
    blocks = {b.key: b for b in overlay.blocks()}
    for key in ("eff", "stats", "abilities"):
        assert blocks[key].height() <= blocks[key].header.height() + 16
    assert overlay._cards[0].minimumHeight() < before - 200
    overlay.close()


# ---- ficha del stream -----------------------------------------------------------------------

def test_stream_sin_las_secciones_ocultas(dex):
    from battlelens.stream.payload import build_cards

    args = (dex, [dex.view(6, "sword-shield")], dex.view(9, "sword-shield"), [50])
    full = build_cards(*args, mode="competitive")[0]
    assert full["versus"] and full["stats"] and full["groups"] and full["evolution"]
    card = build_cards(*args, mode="competitive", hidden=frozenset({"matchup", "stats", "eff", "evo"}))[0]
    assert card["versus"] is None and card["stats"] is None and card["evolution"] is None
    assert card["groups"] == [] and card["ability_lines"] == []
    assert card["name"] == full["name"]


def test_la_evolucion_del_stream_no_usa_la_clase_del_contenedor():
    """`.stage` es el contenedor raíz (posición absoluta arriba a la izquierda): la evolución no puede usarla."""
    js = (STATIC / "card.js").read_text(encoding="utf-8")
    assert 'el("span", "stage"' not in js and '"current" : "stage"' not in js
    assert ".evo .stage" not in (STATIC / "card.css").read_text(encoding="utf-8")


# ---- Ajustes ----------------------------------------------------------------------------------

@windows
def test_ajustes_eligen_las_secciones(qapp):
    from battlelens.ui.settings import SettingsWindow

    w = SettingsWindow(Config(hidden_sections_normal=(), hidden_sections_competitive=("training",)))
    toggles = w.section_toggles
    assert set(toggles) == {(m, k) for m, keys in CARD_SECTIONS.items() for k in keys}
    assert not toggles[("competitive", "training")].isChecked() and toggles[("normal", "eff")].isChecked()
    assert ("normal", "stats") not in toggles  # no existe en la ficha Normal
    toggles[("normal", "evo")].setChecked(False)
    assert w.has_changes()
    config, errors = w.collect()
    assert not errors and config.hidden_sections_normal == ("evo",)
    assert config.hidden_sections_competitive == ("training",)
    reset = next(b for b in w.findChildren(type(w.save_button)) if b.text() == "Mostrar todas")
    reset.click()
    config, _errors = w.collect()
    assert config.hidden_sections_normal == () and config.hidden_sections_competitive == ()


@windows
@pytest.mark.windows
def test_guardar_secciones_redibuja_la_ficha(qapp, tmp_path, monkeypatch, dex):
    from dataclasses import replace

    from battlelens.app import Controller

    monkeypatch.setenv("BATTLELENS_HOME", str(tmp_path))
    config = Config(hotkey_recognize="Ctrl+Alt+Shift+F20", hotkey_calibrate="Ctrl+Alt+Shift+F21",
                    hotkey_hide="Ctrl+Alt+Shift+F22", hotkey_toggle_mode="Ctrl+Alt+Shift+F18",
                    hotkey_cycle_form="Ctrl+Alt+Shift+F17", hotkey_toggle_stream="Ctrl+Alt+Shift+F16",
                    updates_check=False, detection_enabled=False)
    c = Controller(qapp, config, dex)
    try:
        c.tray.notify = lambda msg, warning=False: None
        assert c.overlay.hidden["competitive"] == set(Config().hidden_sections_competitive)
        c.apply_config(replace(c.config, hidden_sections_normal=("eff",)))
        assert c.overlay.hidden["normal"] == {"eff"}
        c.overlay.show_species(dex.get_species(6), None)
        qapp.processEvents()
        assert "eff" not in _visible_blocks(c.overlay)
    finally:
        c.hotkeys.stop()
        c.tray.hide()
        c.overlay.close()
