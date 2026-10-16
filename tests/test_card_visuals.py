"""Estilo de la ficha y bloques plegables (improve-card-visuals)."""

import sys

import pytest

from battlelens.ui import theme


def test_pastillas_suaves_con_contraste_aa():
    for type_id in theme.TYPE_COLORS:
        fill, _border = theme.soft_type_colors(type_id)
        assert theme.contrast_ratio(theme.TEXT, fill) >= 4.5, type_id


def test_estadisticas_en_una_gama():
    assert theme.stat_bar_color(75, 75, 45) == theme.STAT_BAR_MAX
    low = theme.stat_bar_color(45, 75, 45)
    mid = theme.stat_bar_color(50, 75, 45)
    assert len({theme.STAT_BAR_MAX, low, mid}) == 3
    assert theme.stat_bar_color(80, 80, 80) == theme.STAT_BAR_MAX  # todas iguales: ninguna en rojo


@pytest.fixture(scope="module")
def dex():
    from battlelens.core.pokedex import Pokedex

    return Pokedex.load()


@pytest.fixture
def overlay(qapp, dex):
    from battlelens.ui.overlay import Overlay

    o = Overlay(dex, "es", mode="competitive")
    o._available_height = lambda rect: 100_000  # sin depender de la pantalla (la CI tiene 768 px)
    yield o
    o.close()


def _pills(overlay, kind):
    from PyQt6.QtWidgets import QLabel

    return [w.text() for w in overlay.findChildren(QLabel) if w.property("pill") == kind]


def _tones(overlay, name):
    from PyQt6.QtWidgets import QLabel

    return {w.text(): w.property("tone") for w in overlay.findChildren(QLabel) if w.objectName() == name}


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Qt en Windows")
def test_solo_la_cabecera_usa_color_pleno(qapp, overlay, dex):
    overlay.show_species(dex.get_species(759), None, game="sword-shield", level=10)
    qapp.processEvents()
    assert _pills(overlay, "solid") == ["Normal", "Lucha"]
    soft = _pills(overlay, "soft")
    assert {"Volador", "Psíquico", "Hada", "Roca", "Bicho", "Siniestro", "Fantasma"} <= set(soft)


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Qt en Windows")
def test_multiplicadores_con_significado(qapp, dex):
    from battlelens.ui.overlay import Overlay

    o = Overlay(dex, "es")
    o.show_battle([dex.view(263, "sword-shield")], None, None)  # Zigzagoon de Galar
    qapp.processEvents()
    tones = _tones(o, "eff-mult")
    assert tones["×4"] == "good" and tones["×0"] == "neutral"
    o.close()


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Qt en Windows")
def test_comparativa_con_borde_y_veredicto(qapp, overlay, dex):
    from PyQt6.QtWidgets import QLabel

    overlay.show_battle([dex.view(3)], dex.view(6), None)  # Venusaur contra tu Charizard
    qapp.processEvents()
    (block,) = overlay.blocks("matchup")
    assert theme.VERDICT_COLORS["advantage"] in block.styleSheet()
    verdict = next(w for w in block.findChildren(QLabel) if w.objectName() == "verdict")
    assert verdict.text() == "Ventaja" and verdict.property("pill") == "solid"
    tones = [w.property("tone") for w in block.findChildren(QLabel) if w.objectName() == "matchup-mult"]
    assert "good" in tones  # tus ataques de Fuego y Volador ×2


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Qt en Windows")
def test_eficacias_agrupadas(qapp, overlay, dex):
    from PyQt6.QtWidgets import QLabel

    overlay.show_species(dex.get_species(759), None, game="sword-shield", level=10)
    qapp.processEvents()
    (block,) = overlay.blocks("eff")
    texts = [w.text() for w in block.findChildren(QLabel)]
    assert {"DEBILIDADES", "RESISTENCIAS", "INMUNIDADES"} <= set(texts)


# ---- bloques plegables (D11) -----------------------------------------------------------

def _click_title(qapp, overlay, key, index=0):
    from PyQt6.QtCore import Qt
    from PyQt6.QtTest import QTest

    title = overlay.blocks(key)[index].title
    QTest.mouseClick(overlay, Qt.MouseButton.LeftButton, pos=title.mapTo(overlay, title.rect().center()))
    qapp.processEvents()


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Qt en Windows")
def test_clic_en_el_titulo_pliega_sin_ocultar(qapp, overlay, dex):
    overlay.show_species(dex.get_species(759), None, game="sword-shield", level=10)
    qapp.processEvents()
    height = overlay.height()
    pos = overlay.pos()
    changed = []
    overlay.collapsed_changed.connect(lambda: changed.append(True))
    _click_title(qapp, overlay, "abilities")
    assert overlay.isVisible()
    assert overlay.blocks("abilities")[0].collapsed
    assert overlay.height() < height and overlay.pos() == pos
    assert overlay.collapsed["competitive"] == {"abilities"} and changed


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Qt en Windows")
def test_plegado_por_modo_y_en_fichas_siguientes(qapp, overlay, dex):
    overlay.show_species(dex.get_species(759), None, game="sword-shield", level=10)
    qapp.processEvents()
    _click_title(qapp, overlay, "abilities")
    overlay.mode = "normal"
    overlay.show_species(dex.get_species(759), None)
    assert not any(b.collapsed for b in overlay.blocks())
    overlay.mode = "competitive"
    overlay.show_species(dex.get_species(16), None, level=5)
    assert overlay.blocks("abilities")[0].collapsed


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Qt en Windows")
def test_plegar_en_doble_afecta_a_las_dos(qapp, overlay, dex):
    overlay.show_battle([dex.view(16), dex.view(19)], None, None)  # Pidgey y Rattata
    qapp.processEvents()
    _click_title(qapp, overlay, "eff")
    assert [b.collapsed for b in overlay.blocks("eff")] == [True, True]


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Qt en Windows")
def test_veredicto_visible_con_el_bloque_plegado(qapp, overlay, dex):
    from PyQt6.QtWidgets import QLabel

    overlay.show_battle([dex.view(3)], dex.view(6), None)
    qapp.processEvents()
    _click_title(qapp, overlay, "matchup")
    (block,) = overlay.blocks("matchup")
    verdict = next(w for w in block.findChildren(QLabel) if w.objectName() == "verdict")
    assert block.collapsed and verdict.isVisibleTo(overlay)


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Qt en Windows")
def test_clic_fuera_de_los_titulos_no_oculta(qapp, overlay, dex):
    from PyQt6.QtCore import Qt
    from PyQt6.QtTest import QTest
    from PyQt6.QtWidgets import QLabel

    overlay.show_species(dex.get_species(759), None, game="sword-shield", level=10)
    qapp.processEvents()
    pill = next(w for w in overlay.findChildren(QLabel) if w.property("pill") == "soft")
    QTest.mouseClick(overlay, Qt.MouseButton.LeftButton, pos=pill.mapTo(overlay, pill.rect().center()))
    assert overlay.isVisible()  # solo el ✕ la cierra (redesign-settings-window)
