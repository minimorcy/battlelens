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
    from battlelens.app import Controller
    from battlelens.core.config import Config
    from battlelens.core.pokedex import Pokedex

    monkeypatch.setenv("BATTLELENS_HOME", str(tmp_path))
    config = Config(
        hotkey_recognize="Ctrl+Alt+Shift+F20",
        hotkey_calibrate="Ctrl+Alt+Shift+F21",
        hotkey_hide="Ctrl+Alt+Shift+F22",
        detection_enabled=False,
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


def test_reconocimiento_completo(qapp, controller, fake_emulator, tmp_path, requires_ocr):
    from battlelens.core.profiles import Profile, Region
    from battlelens.platform.windows import WindowInfo

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

    from battlelens.platform.windows import WindowInfo

    controller.target = WindowInfo(1, "x", "x.exe", 0)
    controller.recognize()
    assert "calibra" in messages[-1]
    assert not controller._busy


def test_ventana_cerrada_borra_objetivo(qapp, controller, fake_emulator):
    from battlelens.core.profiles import Profile, Region
    from battlelens.platform.windows import WindowInfo

    messages = []
    controller.tray.notify = lambda msg, warning=False: messages.append(msg)
    controller.select_window(WindowInfo(0x7FFFFFF0, "gone", "gone.exe", 0))
    controller.profiles.save(Profile("Fake", Region(0.1, 0.1, 0.3, 0.1)))
    controller.recognize()
    assert _wait(qapp, lambda: not controller._busy)
    assert controller.target is None
    assert "no está disponible" in messages[-1]


def test_reconocimiento_simultaneo_se_ignora(qapp, controller, fake_emulator, requires_ocr):
    from battlelens.core.profiles import Profile, Region
    from battlelens.platform.windows import WindowInfo

    controller.select_window(WindowInfo(int(fake_emulator.winId()), "Fake emulator", "python.exe", 0))
    controller.profiles.save(Profile("Fake", Region.from_pixels(14, 16, 70, 13, 240, 160)))
    started = []
    original = controller._pool.start
    controller._pool.start = lambda task: (started.append(task), original(task))
    controller.recognize()
    controller.recognize()
    assert len(started) == 1
    assert _wait(qapp, lambda: not controller._busy)


@pytest.mark.parametrize(
    ("outcome", "available", "expected"),
    [("cancelled", False, "cancelada"), ("success", True, "Ya puedes"), ("success", False, "Reinicia")],
)
def test_resultado_instalacion_ocr(qapp, controller, monkeypatch, outcome, available, expected):
    from battlelens.platform.ocr_setup import InstallOutcome, InstallResult

    messages = []
    controller.tray.notify = lambda msg, warning=False: messages.append(msg)
    monkeypatch.setattr(type(controller), "ocr_available", staticmethod(lambda: available))
    controller.tray.set_ocr_missing(True)
    controller._on_ocr_installed(InstallResult(InstallOutcome(outcome), "es-ES", 0))
    assert expected in messages[-1]
    assert controller.tray.install_ocr_action.isVisible() == (not (outcome == "success" and available))


def test_activacion_automatica_por_juego(qapp, controller, fake_emulator):
    from battlelens.core.profiles import Profile, Region
    from battlelens.platform.windows import WindowInfo

    messages = []
    controller.tray.notify = lambda msg, warning=False: messages.append(msg)
    esmeralda = Profile("Esmeralda", Region(0.1, 0.1, 0.2, 0.05), game="emerald")
    espada = Profile("Espada", Region(0.1, 0.1, 0.2, 0.05), game="sword-shield")
    controller.profiles.save(espada)
    controller.profiles.save(esmeralda)  # queda activo
    fake_emulator.setWindowTitle("Eden Nightly | Pokémon Espada (64-bit) | 1.3.2")
    qapp.processEvents()

    controller.select_window(WindowInfo(int(fake_emulator.winId()), "x", "eden.exe", 0))
    assert controller.profiles.active_id == espada.id
    assert "Espada" in messages[-1]


def test_juego_sin_perfil_mantiene_el_activo(qapp, controller, fake_emulator):
    from battlelens.core.profiles import Profile, Region
    from battlelens.platform.windows import WindowInfo

    esmeralda = Profile("Esmeralda", Region(0.1, 0.1, 0.2, 0.05), game="emerald")
    controller.profiles.save(esmeralda)
    fake_emulator.setWindowTitle("Citra | Pokémon X")
    qapp.processEvents()
    controller.select_window(WindowInfo(int(fake_emulator.winId()), "x", "citra.exe", 0))
    assert controller.profiles.active_id == esmeralda.id


def test_cambiar_juego_del_perfil(qapp, controller):
    from battlelens.core.profiles import Profile, Region

    controller.tray.notify = lambda msg, warning=False: None
    p = Profile("Viejo", Region(0.1, 0.1, 0.2, 0.05))
    controller.profiles.save(p)
    controller.set_profile_game("sword-shield")
    assert controller.profiles.active.game == "sword-shield"
    controller.profiles.load(preferred_active=p.id)  # persistido en disco
    assert controller.profiles.active.game == "sword-shield"


def _show_frame(qapp, label, frame):
    from PyQt6.QtGui import QImage, QPixmap

    h, w = frame.shape[:2]
    label.setPixmap(QPixmap.fromImage(QImage(frame.data, w, h, frame.strides[0], QImage.Format.Format_RGB888).copy()))
    qapp.processEvents()


@pytest.fixture
def auto_controller(qapp, tmp_path, monkeypatch):
    from battlelens.app import Controller
    from battlelens.core.config import Config
    from battlelens.core.pokedex import Pokedex

    monkeypatch.setenv("BATTLELENS_HOME", str(tmp_path))
    config = Config(
        hotkey_recognize="Ctrl+Alt+Shift+F20",
        hotkey_calibrate="Ctrl+Alt+Shift+F21",
        hotkey_hide="Ctrl+Alt+Shift+F22",
        detection_enabled=True,
        detection_interval_ms=200,
        detection_hide_after_seconds=1.0,
    )
    c = Controller(qapp, config, Pokedex.load())
    yield c
    c._watch_timer.stop()
    c.hotkeys.stop()
    c.tray.hide()
    c.overlay.close()


def _overlay_name(controller):
    from PyQt6.QtWidgets import QLabel

    labels = [w for w in controller.overlay.findChildren(QLabel) if w.objectName() == "species-name"]
    return labels[0].text() if labels and controller.overlay.isVisible() else None


def test_deteccion_automatica_de_extremo_a_extremo(qapp, auto_controller, fake_emulator, requires_ocr):
    from battlelens.core.profiles import Profile, Region
    from battlelens.platform.windows import WindowInfo

    c = auto_controller
    c.tray.notify = lambda msg, warning=False: None
    c.profiles.save(Profile("Fake", Region.from_pixels(14, 16, 70, 13, 240, 160)))
    c.select_window(WindowInfo(int(fake_emulator.winId()), "Fake emulator", "python.exe", 0))
    assert c.auto_detect

    # 1. Entra en combate: la ficha aparece sin pulsar nada
    assert _wait(qapp, lambda: _overlay_name(c) == "Zigzagoon", timeout=6)

    # 2. Cambia el rival
    _show_frame(qapp, fake_emulator, _battle_frame("GEODUDE"))
    assert _wait(qapp, lambda: _overlay_name(c) == "Geodude", timeout=6)

    # 3. Termina el combate: escena sin recuadro de nombre → se oculta sola
    scene = np.full((480, 720, 3), (112, 200, 160), dtype=np.uint8)
    _show_frame(qapp, fake_emulator, scene)
    assert _wait(qapp, lambda: not c.overlay.isVisible(), timeout=6)


def test_conmutador_de_deteccion_persiste(qapp, controller, tmp_path):
    from battlelens.core.config import AppState

    controller.set_auto_detect(True)
    assert controller.auto_detect and controller.tray.auto_detect_action.isChecked()
    controller.set_auto_detect(False)
    assert not controller.auto_detect and not controller.tray.auto_detect_action.isChecked()
    assert AppState.load(tmp_path / "state.json").auto_detect is False


def _double_frame(rival: str, own: str) -> np.ndarray:
    img = Image.new("RGB", (240, 160), (112, 200, 160))
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    font = ImageFont.truetype("consola.ttf", 10)
    d.rectangle((10, 14, 110, 44), fill=(248, 248, 216), outline=(64, 64, 64))
    d.text((16, 17), rival, fill=(64, 64, 64), font=font)
    d.rectangle((130, 110, 230, 140), fill=(248, 248, 216), outline=(64, 64, 64))
    d.text((136, 113), own, fill=(64, 64, 64), font=font)
    return np.array(img.resize((720, 480), Image.NEAREST))


def test_auto_actualiza_al_cambiar_tu_pokemon(qapp, auto_controller, fake_emulator, requires_ocr):
    from battlelens.core.profiles import Profile, Region
    from battlelens.platform.windows import WindowInfo

    c = auto_controller
    c.tray.notify = lambda msg, warning=False: None
    profile = Profile("Fake", Region.from_pixels(14, 16, 70, 13, 240, 160),
                      own_region=Region.from_pixels(134, 112, 70, 13, 240, 160))
    c.profiles.save(profile)
    _show_frame(qapp, fake_emulator, _double_frame("GEODUDE", "TENTACOOL"))
    c.select_window(WindowInfo(int(fake_emulator.winId()), "Fake emulator", "python.exe", 0))

    def verdict():
        from PyQt6.QtWidgets import QLabel

        labels = [w.text() for w in c.overlay.findChildren(QLabel) if w.objectName() == "verdict"]
        return labels[0] if labels and c.overlay.isVisible() else None

    # Tentacool (Agua/Veneno) contra Geodude (Roca/Tierra): ventaja
    assert _wait(qapp, lambda: verdict() == "Ventaja", timeout=6)
    # Sacas a Pidgey (Normal/Volador) contra Geodude: desventaja
    _show_frame(qapp, fake_emulator, _double_frame("GEODUDE", "PIDGEY"))
    assert _wait(qapp, lambda: verdict() == "Desventaja", timeout=6)
