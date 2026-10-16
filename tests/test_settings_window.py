"""Ventana de Ajustes con secciones (redesign-settings-window, spec app-settings)."""

import sys

import pytest

pytestmark = [pytest.mark.windows, pytest.mark.skipif(sys.platform != "win32", reason="Qt en Windows")]

GAMES = [("emerald", "Gen 3 · Esmeralda"), ("sword-shield", "Gen 8 · Espada / Escudo")]


def _region(y=0.1):
    from battlelens.core.profiles import Region

    return Region(0.1, y, 0.2, 0.05)


def _window(profiles=(), active=None, **kwargs):
    from battlelens.core.config import Config
    from battlelens.ui.settings import SettingsWindow

    profiles = list(profiles)
    w = SettingsWindow(Config(**kwargs), get_profiles=lambda: (profiles, active), get_games=lambda: GAMES)
    w.refresh()
    return w


# ---- navegación y guardado --------------------------------------------------------------

def test_secciones_de_la_barra_lateral(qapp):
    w = _window()
    titles = [w.nav.item(i).text().strip() for i in range(w.nav.count())]
    assert titles == ["General", "Ficha", "Reconocimiento", "Atajos", "Modo stream", "Perfiles", "Acerca de"]
    w.show_section("hotkeys")
    assert w.current_section() == "hotkeys" and w.pages.currentIndex() == 3
    w.nav.setCurrentRow(5)
    assert w.current_section() == "profiles"


def test_guardar_solo_con_cambios(qapp):
    w = _window()
    assert not w.save_button.isEnabled() and not w.has_changes()
    w.threshold.setValue(60)
    assert w.save_button.isEnabled() and w.dirty_label.isVisibleTo(w)
    w.threshold.setValue(80)  # volver al valor guardado deja de ser un cambio
    assert not w.save_button.isEnabled()


def test_guardar_emite_y_sigue_abierta(qapp):
    w = _window()
    saved = []
    w.saved.connect(saved.append)
    w.debug.setChecked(True)
    assert w._save()
    assert saved and saved[0].debug is True
    assert not w.has_changes() and not w.save_button.isEnabled()


def test_error_lleva_a_la_seccion_de_atajos(qapp):
    w = _window()
    w.show_section("general")
    w.hotkey_edits["hotkey_hide"].setText("F8")
    saved = []
    w.saved.connect(saved.append)
    assert not w._save()
    assert saved == [] and w.current_section() == "hotkeys"
    assert not w.hotkey_errors["hotkey_hide"].isHidden()


@pytest.mark.parametrize(("answer", "closed", "threshold"), [("cancel", False, 50), ("discard", True, 80)])
def test_cerrar_con_cambios_pendientes(qapp, answer, closed, threshold):
    from PyQt6.QtGui import QCloseEvent

    w = _window()
    w.threshold.setValue(50)
    w.ask_unsaved = lambda: answer
    event = QCloseEvent()
    w.closeEvent(event)
    assert event.isAccepted() == closed
    assert w.threshold.value() == threshold


def test_cambio_externo_no_queda_pendiente(qapp):
    w = _window()
    w.sync_value("mode", "competitive")
    w.sync_value("detection_enabled", False)
    assert w.mode.currentData() == "competitive" and not w.detection_enabled.isChecked()
    assert not w.has_changes()
    config, errors = w.collect()
    assert not errors and config.overlay_mode == "competitive"


def test_modo_stream_y_mantenimiento(qapp):
    w = _window()
    assert not w.copy_url_button.isEnabled() and w._update_row.isHidden() and w._ocr_row.isHidden()
    w.set_stream(True, "http://localhost:17320/")
    assert w.stream_url.text() == "http://localhost:17320/" and w.copy_url_button.isEnabled()
    w.set_update("9.9.9")
    w.set_ocr_missing(True)
    assert w.update_button.text() == "Descargar BattleLens 9.9.9…"
    assert not w._update_row.isHidden() and not w._ocr_row.isHidden()
    copied = []
    w.copy_stream_url_requested.connect(lambda: copied.append(1))
    w.copy_url_button.click()
    assert copied == [1]


def test_acerca_de_en_ajustes(qapp):
    from battlelens import DISCLAIMER

    assert DISCLAIMER in _window().about.text()


# ---- perfiles (D4) ----------------------------------------------------------------------

def test_sin_perfiles(qapp):
    w = _window()
    assert not w.no_profiles.isHidden() and w.profile_list.isHidden() and w.active_card.isHidden()
    assert not w.delete_button.isEnabled()
    asked = []
    w.preset_requested.connect(lambda: asked.append(1))
    w.preset_button.click()
    assert asked == [1]


def test_estado_de_las_regiones(qapp):
    from battlelens.core.profiles import Profile

    profile = Profile("Esmeralda", _region()).with_role_region("own", _region(0.5))
    w = _window([profile], profile.id)
    status = {role: row[0].text() for role, row in w.region_rows.items()}
    assert status == {"rival": "✓ Calibrada", "rival2": "Sin calibrar", "own": "✓ Calibrada", "moves": "Sin calibrar"}
    assert w.region_rows["own"][1].text() == "Recalibrar…" and w.region_rows["rival2"][1].text() == "Calibrar…"
    assert w.region_rows["rival"][2] is None  # el rival no se puede quitar
    assert not w.region_rows["own"][2].isHidden() and w.region_rows["rival2"][2].isHidden()
    requested, removed = [], []
    w.region_requested.connect(requested.append)
    w.region_remove_requested.connect(removed.append)
    w.region_rows["rival2"][1].click()
    w.region_rows["own"][2].click()
    assert requested == ["rival2"] and removed == ["own"]


def test_juego_del_perfil(qapp):
    from battlelens.core.profiles import Profile

    profile = Profile("Espada", _region(), game="sword-shield")
    w = _window([profile], profile.id)
    combo = w.game_combo
    assert [combo.itemText(i) for i in range(combo.count())] == ["Sin especificar", *[label for _, label in GAMES]]
    assert combo.currentData() == "sword-shield"
    chosen = []
    w.profile_game_selected.connect(chosen.append)
    combo.activated.emit(1)
    combo.activated.emit(0)
    assert chosen == ["emerald", None]


def test_elegir_otro_perfil_lo_activa(qapp):
    from battlelens.core.profiles import Profile

    first, second = Profile("Esmeralda", _region(), game="emerald"), Profile("Espada", _region())
    w = _window([first, second], first.id)
    assert [w.profile_list.item(i).text() for i in range(2)] == ["Esmeralda   ·   Gen 3 · Esmeralda", "Espada"]
    assert w.profile_list.currentRow() == 0
    selected = []
    w.profile_selected.connect(selected.append)
    w.profile_list.setCurrentRow(1)
    assert selected == [second.id]


def test_ventana_del_emulador(qapp):
    from battlelens.platform.windows import WindowInfo
    from battlelens.ui.settings import SettingsWindow
    from battlelens.core.config import Config

    infos = [WindowInfo(1, "mGBA - Pokémon Esmeralda", "mGBA.exe", 10), WindowInfo(2, "Ryujinx", "Ryujinx.exe", 20)]
    w = SettingsWindow(Config(), list_windows=lambda: infos, get_target=lambda: infos[1])
    w.refresh()
    assert w.window_combo.count() == 2 and w.window_combo.currentIndex() == 1
    chosen = []
    w.window_selected.connect(chosen.append)
    w.window_combo.activated.emit(0)
    assert chosen == [infos[0]]


# ---- bandeja (D7) -----------------------------------------------------------------------

def test_bandeja_con_opciones_rapidas(qapp):
    from battlelens.core.profiles import Profile
    from battlelens.ui.tray import Tray

    profile = Profile("Esmeralda", _region())
    tray = Tray(lambda: [], lambda: None, lambda: ([profile], profile.id), {})
    labels = [a.text() for a in tray.menu.actions()]
    for gone in ("Regiones del perfil", "Juego del perfil activo", "Eliminar perfil activo…", "Acerca de…",
                 "Abrir carpeta de datos"):
        assert gone not in labels
    assert tray.menu.defaultAction() is tray.settings_action
    tray._populate_profiles()
    manage = next(a for a in tray._profiles_menu.actions() if a.text() == "Gestionar perfiles…")
    asked = []
    tray.manage_profiles_requested.connect(lambda: asked.append(1))
    manage.trigger()
    assert asked == [1]
    tray.hide()


def test_doble_clic_abre_ajustes(qapp):
    from PyQt6.QtWidgets import QSystemTrayIcon

    from battlelens.ui.tray import Tray

    tray = Tray(lambda: [], lambda: None, lambda: ([], None), {})
    asked = []
    tray.settings_requested.connect(lambda: asked.append(1))
    tray._on_activated(QSystemTrayIcon.ActivationReason.DoubleClick)
    assert asked == [1]
    tray.hide()


def test_desplegar_todas_las_secciones(qapp):
    """Ficha: el botón pide desplegar sin pasar por «Guardar» (improve-card-visuals)."""
    w = _window()
    asked = []
    w.expand_sections_requested.connect(lambda: asked.append(True))
    w.expand_button.click()
    assert asked == [True]
    w.close()
