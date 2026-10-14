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
        updates_check=False,
        hotkey_toggle_mode="Ctrl+Alt+Shift+F18",
        hotkey_cycle_form="Ctrl+Alt+Shift+F17",
        hotkey_toggle_stream="Ctrl+Alt+Shift+F16",
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
        updates_check=False,
        hotkey_toggle_mode="Ctrl+Alt+Shift+F18",
        hotkey_cycle_form="Ctrl+Alt+Shift+F17",
        hotkey_toggle_stream="Ctrl+Alt+Shift+F16",
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


# ---- ajustes y actualizaciones (add-settings-and-updates) --------------------------

def test_aplicar_ajustes_en_caliente(qapp, controller, tmp_path):
    from dataclasses import replace

    from battlelens.core.config import load_config
    from battlelens.platform.hotkeys import HotkeyManager, parse_hotkey

    controller.tray.notify = lambda msg, warning=False: None
    new = replace(controller.config, language="en", threshold=70.0, hotkey_recognize="Ctrl+Alt+Shift+F19",
                  detection_interval_ms=900)
    controller.apply_config(new)
    assert controller.overlay.language == "en" and controller.pipeline.matcher.threshold == 70.0
    assert controller._watch_timer.interval() == 900
    assert load_config(tmp_path / "config.toml") == new
    # el atajo antiguo queda libre y el nuevo ocupado
    probe_old = HotkeyManager({"x": parse_hotkey("Ctrl+Alt+Shift+F20")})
    probe_new = HotkeyManager({"x": parse_hotkey("Ctrl+Alt+Shift+F19")})
    try:
        assert probe_old.start() == []
        assert probe_new.start() == ["x"]
    finally:
        probe_old.stop()
        probe_new.stop()
    assert "Ctrl+Alt+Shift+F19" in controller.tray._recognize_action.text()


def test_aviso_de_version_nueva(qapp, controller):
    from battlelens.core.updates import Release

    messages = []
    controller.tray.notify = lambda msg, warning=False: messages.append(msg)
    controller._on_update_checked(Release("9.9.9", "https://example.invalid/r"))
    assert controller.tray.update_action.isVisible()
    assert controller.tray.update_action.text() == "Descargar BattleLens 9.9.9…"
    assert "9.9.9" in messages[-1]
    assert controller.state.last_update_check is not None


def test_sin_version_nueva_no_hay_opcion(qapp, controller):
    controller._on_update_checked(None)
    assert not controller.tray.update_action.isVisible()


def test_comprobacion_desactivada_no_consulta(qapp, controller):
    calls = []
    controller.check_for_updates(fetch=lambda: calls.append(1) or {})
    _wait_pool(qapp)
    assert calls == []  # updates_check=False en el fixture


def _wait_pool(qapp):
    from PyQt6.QtCore import QThreadPool

    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()



# ---- modos de ficha (add-display-modes) -----------------------------------------------

def test_cambio_de_modo_redibuja_la_ficha_visible(qapp, controller, tmp_path):
    from PyQt6.QtWidgets import QLabel

    from battlelens.core.config import load_config

    controller.tray.notify = lambda msg, warning=False: None
    controller._show_battle((759, None, None), "sword-shield", None, (10, None, None))
    qapp.processEvents()

    def names(obj):
        return [w.text() for w in controller.overlay.findChildren(QLabel) if w.objectName() == obj]

    assert controller.overlay.mode == "normal" and not names("move")
    controller.toggle_mode()  # como Ctrl+Alt+M
    qapp.processEvents()
    assert controller.overlay.mode == "competitive"
    assert names("species-name") == ["Stufful"] and names("level") == ["Nv. 10"] and len(names("move")) == 4
    assert controller.tray.mode_actions["competitive"].isChecked()
    assert load_config(tmp_path / "config.toml").overlay_mode == "competitive"
    controller.set_mode("normal")
    qapp.processEvents()
    assert not names("move") and load_config(tmp_path / "config.toml").overlay_mode == "normal"


def _card_names(controller, obj):
    from PyQt6.QtWidgets import QLabel

    return [w.text() for w in controller.overlay.findChildren(QLabel) if w.objectName() == obj]


def test_cambiar_de_forma_rotom(qapp, controller):
    controller._show_battle((479, None, None), "platinum", None)
    qapp.processEvents()
    assert _card_names(controller, "species-name") == ["Rotom"]
    assert _card_names(controller, "form-hint") == ["Ctrl+Alt+Shift+F17: cambiar de forma"]
    controller.cycle_form()
    controller.cycle_form()  # como Ctrl+Alt+F dos veces
    qapp.processEvents()
    assert _card_names(controller, "species-name") == ["Rotom Lavado"]


def test_forma_se_mantiene_en_el_combate_y_se_olvida_al_salir(qapp, controller):
    controller._show_battle((6, None, None), "x-y", None)
    controller.cycle_form()
    controller._show_battle((6, None, None), "x-y", None)  # la detección vuelve a reconocerlo
    qapp.processEvents()
    assert _card_names(controller, "species-name") == ["Mega-Charizard X"]
    controller._show_battle((16, None, None), "x-y", None)  # entra otro Pokémon
    controller._show_battle((6, None, None), "x-y", None)
    qapp.processEvents()
    assert _card_names(controller, "species-name") == ["Charizard"]


def test_cambiar_de_forma_sin_formas_no_hace_nada(qapp, controller):
    controller._show_battle((16, 479, None), "platinum", None)  # Pidgey y Rotom: alterna el 2.º
    controller.cycle_form()
    qapp.processEvents()
    assert _card_names(controller, "species-name") == ["Pidgey", "Rotom Calor"]
    controller._show_battle((16, None, None), "platinum", None)
    controller.cycle_form()
    qapp.processEvents()
    assert _card_names(controller, "species-name") == ["Pidgey"]


def test_movimientos_de_una_mega(qapp, controller):
    controller.set_mode("competitive")
    controller._show_battle((6, None, None), "x-y", None, (50, None, None))
    controller.cycle_form()
    qapp.processEvents()
    assert _card_names(controller, "species-name") == ["Mega-Charizard X"]
    assert len(_card_names(controller, "move")) == 4


def test_menu_de_ataques_actualiza_la_ficha(qapp, controller):
    from battlelens.core.learnsets import Learnsets
    from battlelens.core.profiles import Profile, Region

    profile = Profile("Espada", Region(0.6, 0.05, 0.2, 0.05), game="sword-shield")
    controller.profiles.save(profile)
    controller._show_battle((821, None, 813), "sword-shield", None, (None, None, None))
    qapp.processEvents()
    assert not _card_names(controller, "own-move")  # sin memoria ni nivel: no hay apartado
    moves = tuple(Learnsets.get().move(i) for i in ("ember", "double-kick"))
    controller._on_moves_read((profile, moves))
    qapp.processEvents()
    assert _card_names(controller, "own-move") == ["Ascuas", "Doble Patada"]
    assert controller.move_memory.get(profile.id, 813) == ["ember", "double-kick"]
    controller._on_moves_read((profile, ()))  # lectura no válida: no cambia nada
    assert controller.move_memory.get(profile.id, 813) == ["ember", "double-kick"]


def test_probables_de_tu_pokemon_con_nivel(qapp, controller):
    from battlelens.core.profiles import Profile, Region

    controller.profiles.save(Profile("Espada", Region(0.6, 0.05, 0.2, 0.05), game="sword-shield"))
    controller._show_battle((821, None, 813), "sword-shield", None, (None, None, 15))
    qapp.processEvents()
    assert len(_card_names(controller, "own-move")) == 4


def _free_port():
    import socket

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_modo_stream_publica_y_oculta(qapp, controller, tmp_path):
    from battlelens.core.config import load_config

    controller.tray.notify = lambda msg, warning=False: None
    controller.apply_config(replace_config(controller, stream_port=_free_port()))
    controller.set_stream_enabled(True)  # como la casilla «Modo stream» de la bandeja
    assert controller.stream_server.running and controller.tray.stream_action.isChecked()
    assert controller.tray.copy_url_action.isEnabled()
    assert load_config(tmp_path / "config.toml").stream_enabled
    try:
        controller._show_battle((66, None, 813), "sword-shield", None, (16, None, 15))
        snapshot = controller.stream_state.snapshot()
        assert snapshot["visible"] and snapshot["cards"][0]["name"] == "Machop"
        assert snapshot["cards"][0]["versus"]["title"] == "Contra tu Scorbunny"

        controller.hide_overlay()  # clic en la ficha privada
        assert controller.stream_state.visible
        controller.toggle_stream_card()  # Ctrl+Alt+S
        assert not controller.stream_state.visible
        controller.toggle_stream_card()
        assert controller.stream_state.visible

        controller.overlay.show()
        controller._end_battle()  # la detección da por terminado el combate
        assert not controller.stream_state.visible and not controller.overlay.isVisible()
    finally:
        controller.set_stream_enabled(False)
    assert not controller.stream_server.running and not controller.tray.copy_url_action.isEnabled()


def test_modo_de_la_ficha_del_stream_desde_ajustes(qapp, controller):
    controller.tray.notify = lambda msg, warning=False: None
    controller._show_battle((66, None, None), "sword-shield", None, (16, None, None))
    assert controller.stream_state.snapshot()["cards"][0]["level"] is None
    controller.apply_config(replace_config(controller, stream_card_mode="competitive"))
    snapshot = controller.stream_state.snapshot()
    assert snapshot["mode"] == "competitive" and snapshot["cards"][0]["level"] == "Nv. 16"
    assert controller.overlay.mode == "normal"  # la ficha privada no cambia


def test_ajustes_reinician_el_servidor_en_otro_puerto(qapp, controller):
    controller.tray.notify = lambda msg, warning=False: None
    first, second = _free_port(), _free_port()
    controller.apply_config(replace_config(controller, stream_enabled=True, stream_port=first))
    try:
        assert controller.stream_server.port == first
        controller.apply_config(replace_config(controller, stream_port=second))
        assert controller.stream_server.port == second
        assert controller.tray.copy_url_action.text().endswith(f"(http://localhost:{second}/)")
    finally:
        controller.apply_config(replace_config(controller, stream_enabled=False))


def test_copiar_url_para_obs(qapp, controller):
    from PyQt6.QtGui import QGuiApplication

    messages = []
    controller.tray.notify = lambda msg, warning=False: messages.append(msg)
    port = _free_port()
    controller.apply_config(replace_config(controller, stream_enabled=True, stream_port=port))
    try:
        controller.copy_stream_url()
        assert QGuiApplication.clipboard().text() == f"http://localhost:{port}/"
        assert messages[-1] == f"URL copiada: http://localhost:{port}/"
    finally:
        controller.apply_config(replace_config(controller, stream_enabled=False))


def test_puerto_ocupado_avisa(qapp, controller):
    import socket

    warnings = []
    controller.tray.notify = lambda msg, warning=False: warnings.append(msg) if warning else None
    busy = socket.socket()
    busy.bind(("127.0.0.1", 0))
    busy.listen()
    port = busy.getsockname()[1]
    try:
        controller.apply_config(replace_config(controller, stream_enabled=True, stream_port=port))
        assert not controller.stream_server.running
        assert warnings == [f"El puerto {port} está ocupado: cámbialo en Ajustes."]
    finally:
        busy.close()
        controller.apply_config(replace_config(controller, stream_enabled=False))


def replace_config(controller, **changes):
    from dataclasses import replace

    return replace(controller.config, **changes)


def test_modo_desde_ajustes(qapp, controller):
    from dataclasses import replace

    controller.tray.notify = lambda msg, warning=False: None
    controller.apply_config(replace(controller.config, overlay_mode="competitive"))
    assert controller.overlay.mode == "competitive" and controller.tray.mode_actions["competitive"].isChecked()
