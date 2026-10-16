"""Interfaz en inglés de punta a punta (add-english-ui, spec interface-language)."""

import re
import sys

import pytest

import battlelens.i18n as i18n

pytestmark = [pytest.mark.windows, pytest.mark.skipif(sys.platform != "win32", reason="Qt en Windows")]

# Palabras que delatan un texto sin traducir (los datos Pokémon en español se excluyen aparte)
SPANISH = re.compile(
    r"\b(Reconocer|Ajustes|Perfil|Ventana|Calibrar|Debilidades|Inmunidades|Resistencias|Contra tu|Tus movimientos|"
    r"Captura|Evolución|Salir|Acerca|Detección|Ficha|Modo|Idioma|Atajos|Guardar|Ocultar|Estado|Ventaja|Desventaja|"
    r"Velocidad|Habilidades|Otras formas|Total estadísticas|Tú|Él|Nv\.)\b"
)


@pytest.fixture
def english():
    i18n.set_language("en")
    yield
    i18n.set_language("es")


@pytest.fixture(scope="module")
def dex():
    from battlelens.core.pokedex import Pokedex

    return Pokedex.load()


def _texts(widget):
    from PyQt6.QtWidgets import QAbstractButton, QComboBox, QGroupBox, QLabel

    texts = [w.text() for w in widget.findChildren(QLabel) if w.objectName() != "ability-description"]  # dato Pokémon
    texts += [w.text() for w in widget.findChildren(QAbstractButton)]
    texts += [w.title() for w in widget.findChildren(QGroupBox)]
    for combo in widget.findChildren(QComboBox):
        texts += [combo.itemText(i) for i in range(combo.count())]
    return texts


def _menu_texts(menu):
    texts = []
    for action in menu.actions():
        texts.append(action.text())
        if action.menu() is not None:
            action.menu().aboutToShow.emit()
            texts += _menu_texts(action.menu())
    return texts


def _spanish(texts, allowed=()):
    return [t for t in texts if SPANISH.search(t) and not any(a in t for a in allowed)]


def test_bandeja_en_ingles(qapp, english):
    from battlelens.core.profiles import Profile, Region
    from battlelens.ui.tray import Tray

    profile = Profile("Sword", Region(0.1, 0.1, 0.2, 0.05))
    tray = Tray(lambda: [], lambda: None, lambda: ([profile], profile.id), {})
    texts = _menu_texts(tray.menu)
    assert "Recognize now" in texts
    assert not _spanish(texts), _spanish(texts)
    tray.hide()


def test_ajustes_en_ingles(qapp, english):
    from battlelens.core.config import Config
    from battlelens.core.profiles import Profile, Region
    from battlelens.ui.settings import SettingsWindow

    profile = Profile("Sword", Region(0.1, 0.1, 0.2, 0.05))
    dialog = SettingsWindow(Config(), get_profiles=lambda: ([profile], profile.id))
    dialog.set_update("9.9.9")
    dialog.set_ocr_missing(True)
    dialog.refresh()
    texts = _texts(dialog) + [dialog.windowTitle()]
    texts += [dialog.nav.item(i).text() for i in range(dialog.nav.count())]
    assert "Interface language" in texts and "  Shortcuts" in texts and "Recalibrate…" in texts
    assert not _spanish(texts, allowed=("Español",)), _spanish(texts, allowed=("Español",))


@pytest.mark.parametrize("mode", ["normal", "competitive"])
def test_ficha_en_ingles_con_datos_en_espanol(qapp, english, dex, mode):
    from battlelens.core.learnsets import Learnsets
    from battlelens.ui.overlay import Overlay

    overlay = Overlay(dex, "es", mode=mode)
    overlay.form_hotkey = "Ctrl+Alt+F"
    moves = [Learnsets.get().move(i) for i in ("ember", "double-kick")]
    overlay.show_battle([dex.view(66, "sword-shield")], dex.view(813, "sword-shield"), None, [16], 15, moves)
    qapp.processEvents()
    texts = _texts(overlay)
    joined = " | ".join(texts)
    assert "AGAINST YOUR SCORBUNNY" in joined and "WEAKNESSES" in joined
    assert "Volador" in joined and "Ascuas" in joined  # datos Pokémon en español
    assert not _spanish(texts), _spanish(texts)
    overlay.close()


def test_ficha_doble_y_formas_en_ingles(qapp, english, dex):
    from battlelens.ui.overlay import Overlay

    overlay = Overlay(dex, "en", mode="competitive")
    overlay.form_hotkey = "Ctrl+Alt+F"
    overlay.show_battle([dex.view(437, "platinum"), dex.view(479, "platinum")], dex.view(445, "platinum"), None, [40, 40], 45)
    qapp.processEvents()
    texts = _texts(overlay)
    joined = " | ".join(texts)
    assert "if it has" in joined and "OTHER FORMS" in joined and "Ctrl+Alt+F: " in joined
    assert not _spanish(texts), _spanish(texts)
    overlay.close()


def test_cambio_de_idioma_en_caliente(qapp, tmp_path, monkeypatch, dex):
    from dataclasses import replace

    from PyQt6.QtWidgets import QLabel

    from battlelens.app import Controller
    from battlelens.core.config import Config

    monkeypatch.setenv("BATTLELENS_HOME", str(tmp_path))
    config = Config(hotkey_recognize="Ctrl+Alt+Shift+F20", hotkey_calibrate="Ctrl+Alt+Shift+F21",
                    hotkey_hide="Ctrl+Alt+Shift+F22", hotkey_toggle_mode="Ctrl+Alt+Shift+F18",
                    hotkey_cycle_form="Ctrl+Alt+Shift+F17", hotkey_toggle_stream="Ctrl+Alt+Shift+F16",
                    updates_check=False, detection_enabled=False, interface_language="es")
    controller = Controller(qapp, config, dex)
    messages = []
    controller.tray.notify = lambda msg, warning=False: messages.append(msg)
    try:
        controller._show_battle((66, None, None), "sword-shield", None)
        qapp.processEvents()

        def titles():
            return [w.text() for w in controller.overlay.findChildren(QLabel)]

        assert "DEBILIDADES" in titles()
        controller.apply_config(replace(controller.config, interface_language="en"))
        qapp.processEvents()
        assert i18n.get_language() == "en" and "WEAKNESSES" in titles()
        assert "Menus will switch language when BattleLens restarts." in messages
        assert controller.stream_state.snapshot()["cards"][0]["groups"][0]["title"] == "Weaknesses"
    finally:
        i18n.set_language("es")
        controller.hotkeys.stop()
        controller.tray.hide()
        controller.overlay.close()
