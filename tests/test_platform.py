import os
import sys
import time

import pytest

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="APIs de Windows")

from battlelens.platform.hotkeys import (  # noqa: E402
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
    from battlelens.platform.hotkeys import HotkeyManager

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
    from battlelens.platform.single_instance import SingleInstance

    name = f"Local\\battlelens-test-{os.getpid()}"
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
    w.setWindowTitle("battlelens test window")
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
    from battlelens.platform.capture import capture_client

    dpr = known_window.devicePixelRatioF()
    image = capture_client(int(known_window.winId()))
    assert image.shape[1] == round(320 * dpr)
    assert image.shape[0] == round(200 * dpr)
    center = image[image.shape[0] // 2, image.shape[1] // 2]
    assert center[0] > 200 and center[1] < 60 and center[2] < 60  # rojo → sin desplazamiento


@pytest.mark.windows
def test_captura_ventana_tapada(qapp, known_window):
    """El emulador suele quedar detrás de otras ventanas: la captura debe ver su contenido igualmente."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QColor, QPalette
    from PyQt6.QtWidgets import QWidget

    from battlelens.platform.capture import capture_client

    cover = QWidget(None, Qt.WindowType.WindowStaysOnTopHint)
    pal = cover.palette()
    pal.setColor(QPalette.ColorRole.Window, QColor(0, 0, 255))
    cover.setPalette(pal)
    cover.setAutoFillBackground(True)
    cover.setGeometry(known_window.frameGeometry().adjusted(-20, -20, 20, 20))
    cover.show()
    deadline = time.monotonic() + 0.6
    while time.monotonic() < deadline:
        qapp.processEvents()
        time.sleep(0.02)
    try:
        image = capture_client(int(known_window.winId()))
        center = image[image.shape[0] // 2, image.shape[1] // 2]
        assert center[0] > 200 and center[2] < 60  # rojo de la ventana, no el azul de la que la tapa
    finally:
        cover.close()


def test_captura_recurre_a_pantalla_si_printwindow_da_negro(monkeypatch):
    import numpy as np

    from battlelens.platform import capture

    monkeypatch.setattr(capture.windows, "is_window", lambda h: True)
    monkeypatch.setattr(capture.windows, "is_minimized", lambda h: False)
    monkeypatch.setattr(capture.windows, "client_rect_on_screen", lambda h: (0, 0, 4, 3))
    monkeypatch.setattr(capture, "_print_window", lambda h, w, ht: np.zeros((ht, w, 3), np.uint8))
    monkeypatch.setattr(capture, "_screen_copy", lambda l, t, w, ht: np.full((ht, w, 3), 7 + 100, np.uint8))
    assert capture.capture_client(1).max() == 107


@pytest.mark.windows
def test_lista_excluye_ventanas_propias(known_window):
    from battlelens.platform.windows import list_windows

    own = int(known_window.winId())
    assert all(w.hwnd != own for w in list_windows())
    assert any(w.hwnd == own for w in list_windows(exclude_pids=set()))


@pytest.mark.windows
def test_errores_de_captura(known_window):
    from battlelens.platform.capture import WindowMinimized, WindowUnavailable, capture_client

    hwnd = int(known_window.winId())
    known_window.showMinimized()
    time.sleep(0.3)
    with pytest.raises(WindowMinimized):
        capture_client(hwnd)
    with pytest.raises(WindowUnavailable):
        capture_client(0x7FFFFFF0)


@pytest.mark.windows
def test_mutex_por_defecto_coincide_con_appmutex_del_instalador():
    from battlelens import APP_NAME
    from battlelens.platform.single_instance import SingleInstance

    a = SingleInstance()
    b = SingleInstance(APP_NAME)
    try:
        assert APP_NAME == "BattleLens"
        assert b.already_running
    finally:
        b.release()
        a.release()
