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

    o = Overlay(dex, "es", mode="competitive")  # la ficha completa; el modo Normal tiene sus tests
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


def test_ficha_forma_regional(qapp, overlay, dex):
    overlay.show_species(dex.get_species(263), None, game="sword-shield")
    qapp.processEvents()
    texts = " | ".join(_labels(overlay))
    assert "Zigzagoon de Galar" in texts and "Siniestro" in texts and "×4" in texts
    assert "OTRAS FORMAS" in texts


def test_ficha_gen1_sin_habilidades(qapp, overlay, dex):
    overlay.show_species(dex.get_species(6), None, game="red-blue")
    qapp.processEvents()
    texts = " | ".join(_labels(overlay))
    assert "HABILIDADES" not in texts and "Hada" not in texts


def test_dialogo_perfil_propone_juego(qapp, dex):
    from battlelens.ui.calibrator import ProfileDialog

    dialog = ProfileDialog("Pokémon Espada", dex.games, "sword-shield")
    assert dialog.result_value == ("Pokémon Espada", "sword-shield")
    assert "Espada / Escudo" in dialog.game_combo.currentText()
    dialog.game_combo.setCurrentIndex(0)
    assert dialog.result_value[1] is None


def test_menu_juego_del_perfil(qapp):
    from battlelens.core.profiles import Profile, Region
    from battlelens.ui.tray import Tray

    profile = Profile("Espada", Region(0.1, 0.1, 0.2, 0.05), game="sword-shield")
    tray = Tray(lambda: [], lambda: None, lambda: ([profile], profile.id), {},
                lambda: [("emerald", "Gen 3 · Esmeralda"), ("sword-shield", "Gen 8 · Espada / Escudo")])
    chosen = []
    tray.profile_game_selected.connect(chosen.append)
    tray._populate_games()
    actions = tray._game_menu.actions()
    assert [a.text() for a in actions] == ["Sin especificar", "Gen 3 · Esmeralda", "Gen 8 · Espada / Escudo"]
    assert actions[2].isChecked()
    actions[1].trigger()
    assert chosen == ["emerald"]
    tray.hide()


def test_combate_doble_con_comparativa(qapp, overlay, dex):
    rivals = [dex.view(3), dex.view(76)]  # Venusaur y Golem
    overlay.show_battle(rivals, dex.view(6), None)  # contra tu Charizard
    qapp.processEvents()
    from PyQt6.QtWidgets import QLabel

    names = [w.text() for w in overlay.findChildren(QLabel) if w.objectName() == "species-name"]
    verdicts = [w.text() for w in overlay.findChildren(QLabel) if w.objectName() == "verdict"]
    assert names == ["Venusaur", "Golem"]
    assert verdicts == ["Ventaja", "Desventaja"]
    texts = " | ".join(_labels(overlay))
    assert "CONTRA TU CHARIZARD" in texts and "Fuego ×2" in texts and "Planta ×¼" in texts
    assert overlay.width() > 600


def test_sin_tu_pokemon_no_hay_comparativa(qapp, overlay, dex):
    overlay.show_battle([dex.view(3)], None, None)
    qapp.processEvents()
    assert "CONTRA TU" not in " | ".join(_labels(overlay))
    assert overlay.width() == 360


def test_submenu_de_regiones(qapp):
    from battlelens.core.profiles import Profile, Region
    from battlelens.ui.tray import Tray

    simple = Profile("Simple", Region(0.1, 0.1, 0.2, 0.05))
    tray = Tray(lambda: [], lambda: None, lambda: ([simple], simple.id), {})
    tray._populate_regions()
    labels = [a.text() for a in tray._regions_menu.actions()]
    assert labels == ["Recalibrar rival", "Calibrar 2.º rival (combates dobles)…", "Calibrar tu Pokémon…"]

    full = simple.with_role_region("rival2", Region(0.1, 0.2, 0.2, 0.05))
    tray2 = Tray(lambda: [], lambda: None, lambda: ([full], full.id), {})
    removed = []
    tray2.region_remove_requested.connect(removed.append)
    tray2._populate_regions()
    actions = {a.text(): a for a in tray2._regions_menu.actions()}
    assert "Quitar 2.º rival (combates dobles)" in actions and "Quitar tu Pokémon" not in actions
    actions["Quitar 2.º rival (combates dobles)"].trigger()
    assert removed == ["rival2"]
    tray.hide()
    tray2.hide()


def test_datos_adicionales_stufful(qapp, overlay, dex):
    from PyQt6.QtWidgets import QLabel

    overlay.show_species(dex.get_species(759), None)
    qapp.processEvents()
    by_name = {w.objectName(): w.text() for w in overlay.findChildren(QLabel) if w.objectName()}
    assert by_name["capture"] == "Captura: 140 · Media"
    assert by_name["evolution"] == "Stufful → Bewear (Nv. 27)"
    fluffy = next(w for w in overlay.findChildren(QLabel) if "Peluche" in w.text() and w.toolTip())
    assert "Fuego" in fluffy.toolTip()


def test_sin_evolucion_no_hay_apartado(qapp, overlay, dex):
    overlay.show_species(dex.get_species(128), None)
    qapp.processEvents()
    assert "EVOLUCIÓN" not in " | ".join(_labels(overlay))


def test_ajustes_muestran_valores_actuales(qapp):
    from battlelens.core.config import Config
    from battlelens.ui.settings import SettingsDialog

    d = SettingsDialog(Config(language="fr", threshold=75, detection_interval_ms=800, updates_check=False))
    assert d.language.currentData() == "fr" and d.threshold.value() == 75
    assert d.interval.value() == 800 and not d.updates.isChecked()
    assert d.hotkey_edits["hotkey_recognize"].text() == "Ctrl+Alt+P"


def test_ajustes_rechazan_atajo_sin_modificador(qapp):
    from battlelens.core.config import Config
    from battlelens.ui.settings import SettingsDialog

    d = SettingsDialog(Config())
    d.hotkey_edits["hotkey_recognize"].setText("F8")
    d._save()
    assert d.result_config is None
    assert not d.hotkey_errors["hotkey_recognize"].isHidden()
    assert "modificador" in d.hotkey_errors["hotkey_recognize"].text()


def test_ajustes_rechazan_atajos_repetidos(qapp):
    from battlelens.core.config import Config
    from battlelens.ui.settings import SettingsDialog

    d = SettingsDialog(Config())
    d.hotkey_edits["hotkey_hide"].setText("ctrl+alt+p")
    config, errors = d.collect()
    assert config is None and "hotkey_hide" in errors


def test_ajustes_devuelven_configuracion(qapp):
    from battlelens.core.config import Config
    from battlelens.ui.settings import SettingsDialog

    d = SettingsDialog(Config())
    d.language.setCurrentIndex(d.language.findData("en"))
    d.debug.setChecked(True)
    config, errors = d.collect()
    assert errors == {} and config.language == "en" and config.debug is True



# ---- modos de ficha (add-display-modes) ------------------------------------------------

def _named(overlay, name):
    from PyQt6.QtWidgets import QLabel

    return [w.text() for w in overlay.findChildren(QLabel) if w.objectName() == name]


def test_modo_normal_compacto(qapp, dex):
    from PyQt6.QtWidgets import QProgressBar

    from battlelens.ui.overlay import Overlay

    o = Overlay(dex, "es")  # Normal por defecto
    o.show_species(dex.get_species(759), None, level=10)
    qapp.processEvents()
    texts = " | ".join(_labels(o))
    assert _named(o, "capture") == ["Captura: 140 · Media"]
    assert "DEBILIDADES" in texts and "Stufful → Bewear (Nv. 27)" in texts and "<b>340</b>" in texts
    assert "RESISTENCIAS" not in texts and "HABILIDADES" not in texts and "MOVIMIENTOS" not in texts
    assert not o.findChildren(QProgressBar)
    assert o.width() == 300
    o.close()


def test_modo_competitivo_completo(qapp, overlay, dex):
    overlay.show_species(dex.get_species(759), None, game="sword-shield", level=10)
    qapp.processEvents()
    assert _named(overlay, "level") == ["Nv. 10"]
    assert _named(overlay, "move") == ["Placaje", "Malicioso", "Ojitos Tiernos", "Vendetta"]
    assert "Fuego ×2" in _named(overlay, "ability-effect")
    assert any("Fuego" in t for t in _named(overlay, "ability-description"))
    assert "1 Ataque" in _named(overlay, "training")[0] and "6,8 kg" in _named(overlay, "training")[0]
    assert _named(overlay, "range-hp") == ["34-43"]  # PS base 70 a nivel 10


def test_competitivo_sin_nivel_pide_recalibrar(qapp, overlay, dex):
    overlay.show_species(dex.get_species(759), None, game="sword-shield")
    qapp.processEvents()
    assert _named(overlay, "level") == ["Nv. ?"]
    assert "incluyendo el nivel" in _named(overlay, "moves-hint")[0]
    assert not _named(overlay, "range-hp")


def test_competitivo_velocidad_y_movimientos_contra_ti(qapp, overlay, dex):
    # Rival Stufful Nv. 10 contra tu Gastly Nv. 10 (Fantasma/Veneno):
    # Vendetta (Siniestro) le hace ×2 y Placaje (Normal) ×0; los de estado no se marcan
    overlay.show_battle([dex.view(759, "sword-shield")], dex.view(92), None, [10], 10)
    qapp.processEvents()
    assert _named(overlay, "speed") and "Velocidad:" in _named(overlay, "speed")[0]
    assert sorted(_named(overlay, "move-vs-you")) == ["×0", "×2"]



def test_ajustes_incluyen_modo_y_atajo(qapp):
    from battlelens.core.config import Config
    from battlelens.ui.settings import SettingsDialog

    d = SettingsDialog(Config(overlay_mode="competitive"))
    assert d.mode.currentData() == "competitive"
    assert d.hotkey_edits["hotkey_toggle_mode"].text() == "Ctrl+Alt+M"
    d.mode.setCurrentIndex(d.mode.findData("normal"))
    config, errors = d.collect()
    assert errors == {} and config.overlay_mode == "normal"
