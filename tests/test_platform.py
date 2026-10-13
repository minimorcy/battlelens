import os
import sys
import time

import pytest

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="APIs de Windows")

from pokemon_stats_live.platform.hotkeys import (  # noqa: E402
    MOD_ALT,
    MOD_CONTROL,
    MOD_SHIFT,
    HotkeyParseError,
    parse_hotkey,
)


@pytest.mark.parametrize(
    ("text", "mods", "vk"),
    [
        ("Ctrl+Alt+P", MOD_CONTROL | MOD_ALT, ord("P")),
        ("ctrl + shift + 5", MOD_CONTROL | MOD_SHIFT, ord("5")),
        ("Alt+F9", MOD_ALT, 0x78),
        ("Ctrl+Home", MOD_CONTROL, 0x24),
    ],
)
def test_parseo_atajos_validos(text, mods, vk):
    hk = parse_hotkey(text)
    assert (hk.modifiers, hk.vk) == (mods, vk)


@pytest.mark.parametrize("text", ["F8", "P", "", "Ctrl+", "Hyper+P", "Ctrl+Alt+Ñ", "Ctrl+F25"])
def test_parseo_atajos_invalidos(text):
    with pytest.raises(HotkeyParseError):
        parse_hotkey(text)


@pytest.mark.windows
def test_atajo_ocupado_se_detecta(qapp):
    from pokemon_stats_live.platform.hotkeys import HotkeyManager

    hk = parse_hotkey("Ctrl+Alt+Shift+F23")
    first = HotkeyManager({"recognize": hk})
    second = HotkeyManager({"recognize": hk})
    try:
        assert first.start() == []
        assert second.start() == ["recognize"]
    finally:
        first.stop()
        second.stop()
    # Tras liberarlo se puede volver a registrar
    third = HotkeyManager({"recognize": hk})
    try:
        assert third.start() == []
    finally:
        third.stop()


@pytest.mark.windows
def test_instancia_unica():
    from pokemon_stats_live.platform.single_instance import SingleInstance

    name = f"Local\\pokemon-stats-live-test-{os.getpid()}"
    a = SingleInstance(name)
    b = SingleInstance(name)
    try:
        assert not a.already_running
        assert b.already_running
    finally:
        b.release()
        a.release()


@pytest.fixture
def known_window(qapp):
    from PyQt6.QtGui import QColor, QPalette
    from PyQt6.QtWidgets import QWidget

    w = QWidget()
    w.setWindowTitle("pokemon-stats-live test window")
    pal = w.palette()
    pal.setColor(QPalette.ColorRole.Window, QColor(255, 0, 0))
    w.setPalette(pal)
    w.setAutoFillBackground(True)
    w.resize(320, 200)
    w.show()
    w.raise_()
    w.activateWindow()
    deadline = time.monotonic() + 1.0
    while time.monotonic() < deadline:
        qapp.processEvents()
        time.sleep(0.02)
    yield w
    w.close()
    qapp.processEvents()


@pytest.mark.windows
def test_captura_area_cliente(known_window):
    from pokemon_stats_live.platform.capture import capture_client

    dpr = known_window.devicePixelRatioF()
    image = capture_client(int(known_window.winId()))
    assert image.shape[1] == round(320 * dpr)
    assert image.shape[0] == round(200 * dpr)
    center = image[image.shape[0] // 2, image.shape[1] // 2]
    assert center[0] > 200 and center[1] < 60 and center[2] < 60  # rojo → sin desplazamiento


@pytest.mark.windows
def test_lista_excluye_ventanas_propias(known_window):
    from pokemon_stats_live.platform.windows import list_windows

    own = int(known_window.winId())
    assert all(w.hwnd != own for w in list_windows())
    assert any(w.hwnd == own for w in list_windows(exclude_pids=set()))


@pytest.mark.windows
def test_errores_de_captura(known_window):
    from pokemon_stats_live.platform.capture import WindowMinimized, WindowUnavailable, capture_client

    hwnd = int(known_window.winId())
    known_window.showMinimized()
    time.sleep(0.3)
    with pytest.raises(WindowMinimized):
        capture_client(hwnd)
    with pytest.raises(WindowUnavailable):
        capture_client(0x7FFFFFF0)
