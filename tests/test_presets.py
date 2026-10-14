"""Presets por juego, localización de la imagen del juego y asistente (add-game-presets)."""

import sys

import numpy as np
import pytest
from PIL import Image, ImageDraw

from battlelens.core.presets import GBA, PRESETS, preset_for, region_pixels, to_profile_regions
from battlelens.vision.viewport import Viewport, find_viewport


def _game(width: int, height: int, seed: int = 1) -> np.ndarray:
    """Imagen «de juego» sintética: textura con detalle, filas blancas lisas arriba y una línea negra fina."""
    rng = np.random.default_rng(seed)
    img = rng.integers(60, 230, size=(height, width, 3), dtype=np.uint8)
    img[: height // 12] = 248  # fondo blanco liso del propio juego: no es banda del emulador
    img[height * 2 // 3] = 0  # línea negra de 1 px a todo el ancho (borde de cuadro de texto)
    return img


def _menubar(width: int, height: int = 24) -> np.ndarray:
    bar = Image.new("RGB", (width, height), (240, 240, 240))
    ImageDraw.Draw(bar).text((6, 5), "File  Emulation  Tools  Help", fill=(20, 20, 20))
    return np.array(bar)


def _scale(img: np.ndarray, factor: int) -> np.ndarray:
    return np.repeat(np.repeat(img, factor, axis=0), factor, axis=1)


# ---- localización ----------------------------------------------------------------------------

def test_bandas_negras():
    game = _scale(_game(240, 160), 4)
    frame = np.zeros((720, 1280, 3), np.uint8)
    frame[40:680, 160:1120] = game
    assert find_viewport(frame, GBA) == Viewport(160, 40, 960, 640, True)


def test_barra_de_menus():
    game = _scale(_game(240, 160), 3)
    frame = np.vstack([_menubar(720), game])
    vp = find_viewport(frame, GBA)
    # Con la parte de arriba del juego blanca y lisa, el borde con la barra es débil: error de hasta un 2,5 %
    assert (vp.x, vp.width, vp.height) == (0, 720, 480) and abs(vp.y - 24) <= 12 and vp.reliable


def test_barra_de_menus_y_bandas():
    game = _scale(_game(240, 160), 3)
    body = np.zeros((720, 1280, 3), np.uint8)
    body[120:600, 280:1000] = game
    vp = find_viewport(np.vstack([_menubar(1280), body]), GBA)
    assert (vp.x, vp.y, vp.width, vp.height) == (280, 144, 720, 480)


def test_ds_en_vertical_toma_la_pantalla_superior():
    top, bottom = _game(256, 192, 1), _game(256, 192, 2)
    frame = _scale(np.vstack([top, bottom]), 2)
    vp = find_viewport(frame, 256 / 192, ds=True)
    assert (vp.x, vp.y, vp.width, vp.height) == (0, 0, 512, 384) and vp.reliable


def test_ds_en_horizontal_toma_la_izquierda():
    frame = _scale(np.hstack([_game(256, 192, 1), _game(256, 192, 2)]), 2)
    vp = find_viewport(frame, 256 / 192, ds=True)
    assert (vp.x, vp.y, vp.width, vp.height) == (0, 0, 512, 384)


def test_proporcion_imposible():
    switch = _game(1280, 720)
    assert not find_viewport(switch, GBA).reliable
    assert find_viewport(switch, 16 / 9).reliable


# ---- presets ----------------------------------------------------------------------------------

def test_presets_por_juego():
    emerald = preset_for("emerald")
    assert emerald is not None and emerald.aspect == GBA and {"rival", "own"} <= set(emerald.regions)
    assert preset_for("scarlet-violet") is None and preset_for(None) is None
    assert preset_for("platinum").ds and not preset_for("sword-shield").ds
    gen1 = preset_for("red-blue")
    assert gen1 is preset_for("crystal") and gen1.aspect == pytest.approx(160 / 144)


def test_regiones_dentro_de_la_imagen():
    for preset in PRESETS:
        for role, (x, y, w, h) in preset.regions.items():
            assert 0 <= x and 0 <= y and x + w <= 1.0001 and y + h <= 1.0001, (preset.id, role)


def test_regiones_al_area_cliente():
    preset = preset_for("emerald")
    viewport = Viewport(160, 40, 960, 640)
    regions = to_profile_regions(preset, viewport, 1280, 720)
    x, y, w, h = preset.regions["rival"]
    assert regions["rival"].to_pixels(1280, 720) == region_pixels(preset.regions["rival"], viewport)
    assert regions["rival"].x == pytest.approx((160 + x * 960) / 1280, abs=1e-3)
    assert regions["own"].y == pytest.approx((40 + preset.regions["own"][1] * 640) / 720, abs=1e-3)


# ---- asistente ----------------------------------------------------------------------------------

pytestmark_windows = pytest.mark.skipif(sys.platform != "win32", reason="Qt en Windows")


def _frame_gba():
    frame = np.zeros((720, 1280, 3), np.uint8)
    frame[40:680, 160:1120] = _scale(_game(240, 160), 4)
    return frame


@pytestmark_windows
def test_asistente_propone_y_guarda(qapp):
    from battlelens.ui.preset_wizard import PresetWizard

    read = []
    wizard = PresetWizard(_frame_gba(), [("emerald", "Esmeralda"), ("platinum", "Platino")], "emerald",
                          lambda role, crop: read.append(role) or "PIDGEY")
    assert wizard.game_id == "emerald" and wizard.save_button.isEnabled()
    assert wizard.viewport == Viewport(160, 40, 960, 640, True)
    assert {"rival", "own"} <= set(read) and "PIDGEY" in wizard.readings.text()
    wizard._save()
    assert wizard.action == "save" and wizard.preset.id == "gba-gen3"


@pytestmark_windows
def test_asistente_sin_preset_y_proporcion_no_fiable(qapp):
    from battlelens.ui.preset_wizard import PresetWizard

    wizard = PresetWizard(_game(1280, 720), [("emerald", "Esmeralda"), ("scarlet-violet", "Escarlata")], "emerald",
                          lambda role, crop: "")
    assert not wizard.save_button.isEnabled() and "Ajustar la imagen del juego" in wizard.warning.text()
    wizard.game.setCurrentIndex(wizard.game.findData("scarlet-violet"))
    assert not wizard.save_button.isEnabled() and "calibra a mano" in wizard.warning.text()


@pytestmark_windows
def test_asistente_ajustar_la_imagen_del_juego(qapp, monkeypatch):
    from battlelens.core.profiles import Region
    from battlelens.ui import preset_wizard

    class FakeCalibration:
        def __init__(self, image, title, target):
            self.region = Region.from_pixels(100, 50, 600, 400, image.shape[1], image.shape[0])

        def exec(self):
            return True

    monkeypatch.setattr(preset_wizard, "CalibrationDialog", FakeCalibration)
    wizard = preset_wizard.PresetWizard(_game(1280, 720), [("emerald", "Esmeralda")], "emerald", lambda r, c: "")
    assert not wizard.save_button.isEnabled()
    wizard._adjust()
    assert (wizard.viewport.x, wizard.viewport.y, wizard.viewport.width, wizard.viewport.height) == (100, 50, 600, 400)
    assert wizard.save_button.isEnabled()


@pytestmark_windows
def test_controlador_crea_el_perfil_con_el_preset(qapp, tmp_path, monkeypatch):
    from battlelens import app as app_module
    from battlelens.app import Controller
    from battlelens.core.config import Config
    from battlelens.core.pokedex import Pokedex

    monkeypatch.setenv("BATTLELENS_HOME", str(tmp_path))
    config = Config(hotkey_recognize="Ctrl+Alt+Shift+F20", hotkey_calibrate="Ctrl+Alt+Shift+F21",
                    hotkey_hide="Ctrl+Alt+Shift+F22", hotkey_toggle_mode="Ctrl+Alt+Shift+F18",
                    hotkey_cycle_form="Ctrl+Alt+Shift+F17", hotkey_toggle_stream="Ctrl+Alt+Shift+F16",
                    updates_check=False, detection_enabled=False)
    controller = Controller(qapp, config, Pokedex.load())
    try:
        class FakeWizard:
            def __init__(self, image, games, proposed, read_fn):
                assert ("emerald", "Esmeralda") in games and ("scarlet-violet", "Escarlata / Púrpura") not in games
                self.action, self.game_id = "save", "emerald"
                self.preset, self.viewport = preset_for("emerald"), Viewport(160, 40, 960, 640)

            def exec(self):
                return True

        monkeypatch.setattr(app_module, "PresetWizard", FakeWizard)
        monkeypatch.setattr(app_module, "ask_profile", lambda name, games, game, lang: ("Mi Esmeralda", game))
        controller.tray.notify = lambda msg, warning=False: None
        controller._new_profile_from_preset_with(_frame_gba())
        profile = controller.profiles.active
        assert profile.name == "Mi Esmeralda" and profile.game == "emerald"
        assert profile.own_region is not None and profile.moves_region is not None
        assert profile.region.to_pixels(1280, 720) == region_pixels(preset_for("emerald").regions["rival"],
                                                                    Viewport(160, 40, 960, 640))
    finally:
        controller.hotkeys.stop()
        controller.tray.hide()
        controller.overlay.close()


def test_aviso_sin_perfiles_propone_el_preset():
    import ast
    from pathlib import Path

    source = (Path(__file__).resolve().parent.parent / "src" / "battlelens" / "app.py").read_text(encoding="utf-8")
    assert "Nuevo perfil con un preset…" in source and ast.parse(source)
