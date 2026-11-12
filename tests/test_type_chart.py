"""Tabla de tipos (spec type-chart)."""

from battlelens.core.config import Config
from battlelens.core.pokedex import Pokedex


def test_atajo_de_la_tabla_en_la_configuracion():
    assert Config.from_toml("").hotkey_type_chart == "Ctrl+Alt+T"
    assert Config.from_toml('[hotkeys]\ntype_chart = "Ctrl+Shift+Y"\n').hotkey_type_chart == "Ctrl+Shift+Y"


def _window(qapp, dex, generation, lang="es"):
    from battlelens.ui.type_chart import TypeChartWindow

    chart = dex.type_chart(generation)
    w = TypeChartWindow()
    w.set_chart(chart, {t: dex.type_name(t, lang) for t in chart}, generation)
    return w


def test_tabla_segun_la_generacion(qapp):
    dex = Pokedex.load()
    gen1 = _window(qapp, dex, 1)
    assert len(gen1.types) == 15 and gen1.cell("ghost", "psychic") == "×0"  # el fallo original de Rojo/Azul
    gen3 = _window(qapp, dex, 3)
    assert len(gen3.types) == 17 and "fairy" not in gen3.types and gen3.cell("ghost", "steel") == "×½"
    gen9 = _window(qapp, dex, 9)
    assert len(gen9.types) == 18 and gen9.cell("ghost", "steel") == "" and gen9.cell("water", "fire") == "×2"
    assert gen9.width() > gen3.width() > gen1.width()
    gen9.set_highlight(["psychic", "fairy"])
    assert gen9.highlight == {"psychic", "fairy"}
    gen9.grab()  # se pinta sin errores


def test_abreviaturas_unicas(qapp):
    from battlelens.ui.type_chart import abbreviation

    dex = Pokedex.load()
    for lang in ("es", "en"):
        names = [abbreviation(dex.type_name(t, lang)) for t in dex.type_chart(9)]
        assert len(set(names)) == len(names), (lang, names)


def test_tabla_reescalable(qapp):
    from PyQt6.QtCore import QPoint, QPointF, Qt
    from PyQt6.QtGui import QWheelEvent

    from battlelens.ui.type_chart import MAX_SCALE, MIN_SCALE

    dex = Pokedex.load()
    w = _window(qapp, dex, 9)
    base = w.size()
    changes = []
    w.changed.connect(lambda: changes.append(w.scale))
    w.set_scale(1.5)
    assert w.width() == round(base.width() * 1.5) and w.height() == round(base.height() * 1.5)
    w.set_scale(10)
    assert w.scale == MAX_SCALE
    w.set_scale(0)
    assert w.scale == MIN_SCALE

    w.set_scale(1.0)
    wheel = QWheelEvent(QPointF(10, 10), QPointF(10, 10), QPoint(), QPoint(0, 120), Qt.MouseButton.NoButton,
                        Qt.KeyboardModifier.ControlModifier, Qt.ScrollPhase.NoScrollPhase, False)
    w.wheelEvent(wheel)  # Ctrl+rueda hacia arriba
    assert w.scale == 1.1 and changes == [1.1]
    w.grab()  # pinta escalada sin errores
