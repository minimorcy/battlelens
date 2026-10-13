import sys
import time

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont

pytestmark = [pytest.mark.windows, pytest.mark.skipif(sys.platform != "win32", reason="Windows")]


def _battle_frame(name: str) -> np.ndarray:
    img = Image.new("RGB", (240, 160), (112, 200, 160))
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    d.rectangle((10, 14, 110, 44), fill=(248, 248, 216), outline=(64, 64, 64))
    d.text((16, 17), name, fill=(64, 64, 64), font=ImageFont.truetype("consola.ttf", 10))
    return np.array(img.resize((720, 480), Image.NEAREST))


@pytest.fixture
def controller(qapp, tmp_path, monkeypatch):
    from pokemon_stats_live.app import Controller
    from pokemon_stats_live.core.config import Config
    from pokemon_stats_live.core.pokedex import Pokedex

    monkeypatch.setenv("POKEMON_STATS_LIVE_HOME", str(tmp_path))
    config = Config(
        hotkey_recognize="Ctrl+Alt+Shift+F20",
        hotkey_calibrate="Ctrl+Alt+Shift+F21",
        hotkey_hide="Ctrl+Alt+Shift+F22",
    )
    c = Controller(qapp, config, Pokedex.load())
    yield c
    c.hotkeys.stop()
    c.tray.hide()
    c.overlay.close()


@pytest.fixture
def fake_emulator(qapp):
    from PyQt6.QtGui import QImage, QPixmap
    from PyQt6.QtWidgets import QLabel

    frame = _battle_frame("ZIGZAGOON")
    label = QLabel()
    label.setWindowTitle("Fake emulator")
    label.setPixmap(QPixmap.fromImage(QImage(frame.data, 720, 480, frame.strides[0], QImage.Format.Format_RGB888).copy()))
    label.show()
    label.raise_()
    label.activateWindow()
    deadline = time.monotonic() + 0.6
    while time.monotonic() < deadline:
        qapp.processEvents()
        time.sleep(0.02)
    yield label
    label.close()


def _wait(qapp, predicate, timeout=5.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        qapp.processEvents()
        if predicate():
            return True
        time.sleep(0.02)
    return False


def test_reconocimiento_completo(qapp, controller, fake_emulator, tmp_path):
    from pokemon_stats_live.core.profiles import Profile, Region
    from pokemon_stats_live.platform.windows import WindowInfo

    controller.select_window(WindowInfo(int(fake_emulator.winId()), "Fake emulator", "python.exe", 0))
    controller.profiles.save(Profile("Fake", Region.from_pixels(14, 16, 70, 13, 240, 160)))

    controller.recognize()
    assert _wait(qapp, lambda: not controller._busy and controller.overlay.isVisible())
    from PyQt6.QtWidgets import QLabel

    texts = [w.text() for w in controller.overlay.findChildren(QLabel)]
    assert "Zigzagoon" in texts
    assert (tmp_path / "state.json").exists()


def test_sin_ventana_ni_perfil_avisa(qapp, controller):
    messages = []
    controller.tray.notify = lambda msg, warning=False: messages.append(msg)
    controller.target = None
    controller.recognize()
    assert "ventana" in messages[-1]

    from pokemon_stats_live.platform.windows import WindowInfo

    controller.target = WindowInfo(1, "x", "x.exe", 0)
    controller.recognize()
    assert "calibra" in messages[-1]
    assert not controller._busy


def test_ventana_cerrada_borra_objetivo(qapp, controller, fake_emulator):
    from pokemon_stats_live.core.profiles import Profile, Region
    from pokemon_stats_live.platform.windows import WindowInfo

    messages = []
    controller.tray.notify = lambda msg, warning=False: messages.append(msg)
    controller.select_window(WindowInfo(0x7FFFFFF0, "gone", "gone.exe", 0))
    controller.profiles.save(Profile("Fake", Region(0.1, 0.1, 0.3, 0.1)))
    controller.recognize()
    assert _wait(qapp, lambda: not controller._busy)
    assert controller.target is None
    assert "no está disponible" in messages[-1]


def test_reconocimiento_simultaneo_se_ignora(qapp, controller, fake_emulator):
    from pokemon_stats_live.core.profiles import Profile, Region
    from pokemon_stats_live.platform.windows import WindowInfo

    controller.select_window(WindowInfo(int(fake_emulator.winId()), "Fake emulator", "python.exe", 0))
    controller.profiles.save(Profile("Fake", Region.from_pixels(14, 16, 70, 13, 240, 160)))
    started = []
    original = controller._pool.start
    controller._pool.start = lambda task: (started.append(task), original(task))
    controller.recognize()
    controller.recognize()
    assert len(started) == 1
    assert _wait(qapp, lambda: not controller._busy)
