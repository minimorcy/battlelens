import sys

import numpy as np
import pytest

pytestmark = [pytest.mark.windows, pytest.mark.skipif(sys.platform != "win32", reason="Qt en Windows")]


@pytest.fixture(scope="module")
def dex():
    from battlelens.core.pokedex import Pokedex

    return Pokedex.load()


@pytest.fixture
def overlay(qapp, dex):
    from battlelens.ui.overlay import Overlay

    o = Overlay(dex, "es")
    yield o
    o.close()


def _labels(widget):
    from PyQt6.QtWidgets import QLabel

    return [label.text() for label in widget.findChildren(QLabel) if not label.isHidden()]


def test_ficha_completa(qapp, overlay, dex):
    overlay.show_species(dex.get_species(6), None)
    qapp.processEvents()
    texts = " | ".join(_labels(overlay))
    for expected in ("Charizard", "#0006", "Fuego", "Volador", "Roca", "×4", "DEBILIDADES",
                     "RESISTENCIAS", "INMUNIDADES", "Tierra", "534", "Mar Llamas", "Poder Solar", "(oculta)"):
        assert expected in texts, expected
    assert overlay.isVisible()


def test_nuevo_rival_reemplaza_contenido(qapp, overlay, dex):
    overlay.show_species(dex.get_species(16), None)
    overlay.show_species(dex.get_species(19), None)
    qapp.processEvents()
    qapp.processEvents()
    texts = " | ".join(_labels(overlay))
    assert "Rattata" in texts and "Pidgey" not in texts


def test_no_reconocido_muestra_texto(qapp, overlay):
    overlay.show_unrecognized("P!D<GEY", None)
    qapp.processEvents()
    texts = " | ".join(_labels(overlay))
    assert "No reconocido" in texts and "P!D&lt;GEY" in texts and "recalibra" in texts


def test_ventana_no_activa_ni_en_barra_de_tareas(overlay):
    from PyQt6.QtCore import Qt

    flags = overlay.windowFlags()
    assert flags & Qt.WindowType.WindowStaysOnTopHint
    assert flags & Qt.WindowType.Tool
    assert flags & Qt.WindowType.WindowDoesNotAcceptFocus
    assert overlay.testAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)


def test_posicion_junto_a_la_ventana(qapp, overlay, dex):
    from PyQt6.QtGui import QGuiApplication

    screen = QGuiApplication.primaryScreen()
    dpr = screen.devicePixelRatio()
    geo = screen.availableGeometry()
    # Ventana objetivo pequeña en la esquina superior izquierda (píxeles físicos)
    rect = (int(geo.x() * dpr) + 50, int(geo.y() * dpr) + 50, int(400 * dpr), int(300 * dpr))
    overlay.show_species(dex.get_species(6), rect)
    qapp.processEvents()
    assert overlay.x() >= geo.x() + 50 + 400  # a la derecha de la ventana
    assert abs(overlay.y() - (geo.y() + 50)) <= 2


def test_posicion_ventana_a_pantalla_completa(qapp, overlay, dex):
    from PyQt6.QtGui import QGuiApplication

    screen = QGuiApplication.primaryScreen()
    dpr = screen.devicePixelRatio()
    g = screen.geometry()
    rect = (int(g.x() * dpr), int(g.y() * dpr), int(g.width() * dpr), int(g.height() * dpr))
    overlay.show_species(dex.get_species(6), rect)
    qapp.processEvents()
    avail = screen.availableGeometry()
    assert avail.contains(overlay.frameGeometry())
    assert overlay.frameGeometry().right() >= avail.right() - 20


def test_clic_oculta(qapp, overlay, dex):
    from PyQt6.QtCore import QPoint, Qt
    from PyQt6.QtTest import QTest

    overlay.show_species(dex.get_species(6), None)
    qapp.processEvents()
    QTest.mouseClick(overlay, Qt.MouseButton.LeftButton, pos=QPoint(20, 20))
    assert not overlay.isVisible()


def test_auto_ocultar(qapp, dex):
    from PyQt6.QtTest import QTest

    from battlelens.ui.overlay import Overlay

    o = Overlay(dex, "es", auto_hide_seconds=0.2)
    o.show_species(dex.get_species(6), None)
    assert o.isVisible()
    QTest.qWait(400)
    assert not o.isVisible()
    o.close()


def _drag(widget, start, end):
    from PyQt6.QtCore import QPoint, Qt
    from PyQt6.QtTest import QTest

    QTest.mousePress(widget, Qt.MouseButton.LeftButton, pos=QPoint(*start))
    QTest.mouseMove(widget, QPoint(*end))
    QTest.mouseRelease(widget, Qt.MouseButton.LeftButton, pos=QPoint(*end))


def test_calibrador_region_relativa(qapp):
    from battlelens.ui.calibrator import CalibrationDialog

    image = np.zeros((160, 240, 3), dtype=np.uint8)
    dialog = CalibrationDialog(image, "test")
    sel = dialog._selector
    sx, sy = sel.width() / 240, sel.height() / 160
    _drag(sel, (round(120 * sx), round(10 * sy)), (round(200 * sx), round(26 * sy)))
    dialog._confirm()
    assert dialog.result() == 1
    r = dialog.region
    assert r.x == pytest.approx(0.5, abs=0.01) and r.y == pytest.approx(10 / 160, abs=0.01)
    assert r.width == pytest.approx(80 / 240, abs=0.01) and r.height == pytest.approx(16 / 160, abs=0.01)


def test_calibrador_rechaza_region_pequena(qapp):
    from battlelens.ui.calibrator import CalibrationDialog

    image = np.zeros((160, 240, 3), dtype=np.uint8)
    dialog = CalibrationDialog(image, "test")
    sel = dialog._selector
    s = sel.width() / 240
    _drag(sel, (10, 10), (10 + round(30 * s), 10 + round(4 * s)))
    dialog._confirm()
    assert dialog.region is None
    assert "mínimo" in dialog._error.text()


def test_calibrador_esc_cancela(qapp):
    from PyQt6.QtCore import Qt
    from PyQt6.QtTest import QTest

    from battlelens.ui.calibrator import CalibrationDialog

    dialog = CalibrationDialog(np.zeros((160, 240, 3), dtype=np.uint8), "test")
    dialog.show()
    QTest.keyClick(dialog, Qt.Key.Key_Escape)
    assert dialog.result() == 0 and dialog.region is None
