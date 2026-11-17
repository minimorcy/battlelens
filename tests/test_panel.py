"""Modo panel: ficha y tabla de tipos en una ventana normal (spec panel-window)."""

import pytest

from battlelens.core.config import Config, ConfigError
from battlelens.core.pokedex import Pokedex


def test_display_en_la_configuracion():
    assert Config.from_toml("").overlay_display == "overlay"
    assert Config.from_toml('[overlay]\ndisplay = "panel"\n').overlay_display == "panel"
    with pytest.raises(ConfigError):
        Config.from_toml('[overlay]\ndisplay = "otro"\n')


def _panel(qapp):
    from battlelens.ui.overlay import Overlay
    from battlelens.ui.panel import PanelWindow
    from battlelens.ui.type_chart import TypeChartWindow

    dex = Pokedex.load()
    overlay, chart = Overlay(dex), TypeChartWindow()
    table = dex.type_chart(9)
    chart.set_chart(table, {t: dex.type_name(t, "es") for t in table}, 9)
    chart.set_scale(1.3)
    return dex, overlay, chart, PanelWindow(overlay, chart)


def test_panel_ficha_esperando_y_vuelta_al_overlay(qapp):
    dex, overlay, chart, panel = _panel(qapp)
    panel.dock()
    try:
        assert panel.isVisible() and not overlay.isWindow() and not chart.isWindow()
        assert panel._waiting.isVisible() and chart.isVisible()

        overlay.show_view(dex.view(759, None, "es"), None)
        qapp.processEvents()
        assert overlay.isVisible() and not panel._waiting.isVisible()
        assert overlay.height() <= panel._column.height()  # cabe en su columna (con desplazamiento si no)

        overlay.hide()  # fin del combate
        assert panel.isVisible() and panel._waiting.isVisible()

        panel.resize(1600, 1000)
        qapp.processEvents()
        big = chart.scale
        panel.resize(700, 400)
        qapp.processEvents()
        assert chart.scale < big
        panel.grab()  # se pinta sin errores
    finally:
        panel.undock()
    assert overlay.isWindow() and chart.isWindow() and chart.scale == 1.3 and not panel.isVisible()


def test_geometria_de_state_json(qapp):
    _dex, _overlay, _chart, panel = _panel(qapp)
    panel.restore_geometry([50, 60, 900, 600])
    assert panel.saved_geometry() == [50, 60, 900, 600]
    for bad in (None, [1, 2], ["a", 0, 0, 0], [99999, 99999, 800, 600]):
        panel.restore_geometry(bad)  # se ignora: tocado a mano o monitor que ya no está
        assert panel.saved_geometry() == [50, 60, 900, 600]


def test_panel_con_la_tabla_de_naturalezas(qapp):
    from battlelens.ui.nature_chart import NatureChartWindow
    from battlelens.ui.panel import PanelWindow

    _dex, overlay, chart, _ = _panel(qapp)
    natures = NatureChartWindow()
    panel = PanelWindow(overlay, chart, natures)
    panel.dock()
    try:
        panel.resize(1300, 900)
        qapp.processEvents()
        assert natures.isVisible() and not natures.isWindow()
        assert natures.y() >= chart.y() + chart.height()  # debajo de la de tipos
        assert natures.y() + natures.height() <= panel._chart_slot.height()  # caben las dos
        assert not panel.side_by_side
        panel._chart_slot.resize(1800, 500)  # hueco muy ancho y bajito (sin depender del tamaño de la pantalla del CI)
        panel.fit_chart()
        assert panel.side_by_side and natures.x() >= chart.x() + chart.width() and natures.y() == 0
        panel._chart_slot.resize(700, 860)
        panel.fit_chart()
        natures.hide()  # bandeja: la oculta y la de tipos recupera el hueco
        qapp.processEvents()
        assert chart.scale > natures.scale
    finally:
        panel.undock()
    assert natures.isWindow() and natures.scale == 1.0
