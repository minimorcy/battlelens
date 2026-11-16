"""Iconos de tipo: descarga validada, caché y uso en la ficha, la tabla y el stream (add-type-icons).

Sin red: la descarga se inyecta. Los iconos son círculos de color generados aquí (los reales tienen copyright).
"""

import threading

import pytest

from battlelens.core.remote_images import MAX_ICON_BYTES, TYPE_ICON_URL, TypeIcons, fetch_png

NUMBERS = {"normal": 1, "fire": 10, "water": 11}


def fake_png(color: str = "#e0533c", size: int = 60) -> bytes:
    from PyQt6.QtCore import QBuffer, QIODevice, Qt
    from PyQt6.QtGui import QColor, QImage, QPainter

    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    p = QPainter(image)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(color))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(4, 4, size - 8, size - 8)
    p.end()
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


def fill_cache(directory, numbers) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for n in numbers:
        (directory / f"{n}.png").write_bytes(fake_png())


def wait(icons: TypeIcons, qapp) -> None:
    for _ in range(200):
        qapp.processEvents()
        if not icons._running:
            qapp.processEvents()  # entrega la señal `finished` en cola
            return
        threading.Event().wait(0.02)
    raise AssertionError("la descarga no terminó")


# ---- fetch_png ------------------------------------------------------------------

def test_fetch_png_guarda_el_png(qapp, tmp_path):
    data = fake_png()
    dest = tmp_path / "icons" / "10.png"
    fetch_png("https://x/10.png", dest, MAX_ICON_BYTES, lambda url, limit: data)
    assert dest.read_bytes() == data
    assert not list(dest.parent.glob("*.tmp"))


@pytest.mark.parametrize("body", [b"<html>404</html>", b"\x89PNG\r\n\x1a\nbasura", b""])
def test_fetch_png_rechaza_lo_que_no_es_png(qapp, tmp_path, body):
    dest = tmp_path / "10.png"
    with pytest.raises(ValueError):
        fetch_png("https://x/10.png", dest, MAX_ICON_BYTES, lambda url, limit: body)
    assert not dest.exists()


def test_fetch_png_rechaza_lo_que_supera_el_maximo(qapp, tmp_path):
    dest = tmp_path / "10.png"
    with pytest.raises(ValueError):
        fetch_png("https://x/10.png", dest, 100, lambda url, limit: fake_png() + b"\0" * 200)
    assert not dest.exists()


def test_fetch_png_propaga_el_error_de_red(qapp, tmp_path):
    def offline(url, limit):
        raise OSError("sin conexión")

    with pytest.raises(OSError):
        fetch_png("https://x/10.png", tmp_path / "10.png", MAX_ICON_BYTES, offline)


# ---- TypeIcons ------------------------------------------------------------------

def test_cache_completa_no_hace_peticiones(qapp, tmp_path):
    fill_cache(tmp_path, NUMBERS.values())
    calls = []
    icons = TypeIcons(tmp_path, NUMBERS, lambda url, limit: calls.append(url) or fake_png())
    assert icons.complete()
    assert icons.ensure() is False
    assert calls == []


def test_ensure_descarga_los_que_faltan(qapp, tmp_path):
    fill_cache(tmp_path, [1])
    calls = []
    icons = TypeIcons(tmp_path, NUMBERS, lambda url, limit: calls.append(url) or fake_png())
    assert not icons.complete()
    assert icons.ensure() is True
    wait(icons, qapp)
    assert icons.complete()
    assert sorted(calls) == sorted(TYPE_ICON_URL.format(id=n) for n in (10, 11))


def test_fallo_se_recuerda_en_la_sesion(qapp, tmp_path):
    calls = []

    def flaky(url, limit):
        calls.append(url)
        return b"no es un png" if url.endswith("/11.png") else fake_png()

    icons = TypeIcons(tmp_path, NUMBERS, flaky)
    icons.ensure()
    wait(icons, qapp)
    assert not icons.complete()
    assert not (tmp_path / "11.png").exists()
    assert icons.ensure() is False  # el fallido no se reintenta
    assert len(calls) == 3


def test_pixmap_escalado_y_en_cache(qapp, tmp_path):
    fill_cache(tmp_path, NUMBERS.values())
    icons = TypeIcons(tmp_path, NUMBERS)
    small = icons.pixmap("fire", 22)
    assert small is not None and round(small.width() / small.devicePixelRatio()) == 22
    assert icons.pixmap("fire", 22) is small
    assert icons.pixmap("fire").width() == 60
    assert icons.pixmap("stellar", 22) is None


# ---- ficha, tabla y stream con iconos ------------------------------------------------

@pytest.fixture(scope="module")
def dex():
    from battlelens.core.pokedex import Pokedex

    return Pokedex.load()


@pytest.fixture
def full_icons(qapp, tmp_path, dex):
    fill_cache(tmp_path, dex.type_numbers.values())
    return TypeIcons(tmp_path, dex.type_numbers)


def _card(dex, icons, moves=None):
    from battlelens.core.learnsets import Learnsets
    from battlelens.ui.overlay import Overlay

    o = Overlay(dex, "es", mode="competitive")
    o._available_height = lambda rect: 100_000
    o.type_icons = icons
    if moves is None:
        moves = [Learnsets.get().move(i) for i in ("ember", "growl")]
    # Pidgey de rival contra tu Scorbunny, con tus movimientos: todas las secciones con tipos
    o.show_battle([dex.view(16, "sword-shield", "es")], dex.view(813, "sword-shield", "es"), None, [16], 15, moves)
    return o


def _labels(overlay, kind):
    from PyQt6.QtWidgets import QLabel

    return [w for w in overlay.findChildren(QLabel) if w.property("pill") == kind]


def test_ficha_con_iconos_y_nombre_accesible(qapp, dex, full_icons):
    o = _card(dex, full_icons)
    icons = _labels(o, "icon")
    names = [w.accessibleName() for w in icons]
    assert names[:2] == ["Normal", "Volador"]  # cabecera, en orden
    from PyQt6.QtWidgets import QLabel

    assert [w.text() for w in o.findChildren(QLabel, "type-name")] == ["Normal", "Volador"]  # con su nombre
    assert {"Roca", "Eléctrico", "Hielo", "Fuego"} <= set(names)  # Eficacias, «Contra tu…» y «Tus movimientos»
    assert all(w.toolTip() == w.accessibleName() and not w.pixmap().isNull() for w in icons)
    head, rest = icons[0].pixmap(), icons[-1].pixmap()
    assert head.width() / head.devicePixelRatio() == 28 and rest.width() / rest.devicePixelRatio() == 22
    assert _labels(o, "soft") == []  # ningún tipo queda como etiqueta
    o.close()


def test_sin_iconos_todo_con_etiquetas(qapp, dex):
    o = _card(dex, None)
    assert _labels(o, "icon") == []
    assert "Volador" in [w.text() for w in _labels(o, "solid")]
    o.close()


def test_movimiento_sin_tipo_sigue_con_interrogacion(qapp, dex, full_icons):
    from battlelens.core.learnsets import Move

    unknown = Move(0, "x", {"es": "Desconocido"}, None, "status", None, None, None, 0, 0)
    o = _card(dex, full_icons, [unknown])
    assert "?" in [w.text() for w in _labels(o, "soft")]
    o.close()


def test_tabla_de_tipos_con_iconos(qapp, dex, full_icons):
    from PyQt6.QtCore import QPoint

    from battlelens.ui.type_chart import PAD, TypeChartWindow

    w = TypeChartWindow()
    chart = dex.type_chart(9)
    w.set_chart(chart, {t: dex.type_name(t, "es") for t in chart}, 9)
    w.set_icons({t: full_icons.pixmap(t) for t in chart})
    assert set(w.icons) == set(chart)
    origin = w._grid_origin()
    assert w._type_at(QPoint(PAD + 1, origin.y() + 1)) == w.types[0]  # cabecera de fila: nombre en el tooltip
    w.set_highlight(["fire"], ["water"])
    assert not w.grab().isNull()  # se pinta con iconos y resaltado
    w.set_icons({})
    assert w._type_at(QPoint(PAD + 1, origin.y() + 1)) is None  # sin iconos la fila ya lleva el nombre


def test_payload_del_stream_con_iconos(dex):
    from battlelens.stream.payload import build_cards

    (card,) = build_cards(dex, [dex.view(16, "sword-shield")], None, [16], type_icons=True)
    assert [t["icon"] for t in card["types"]] == ["/type-icon/1.png", "/type-icon/3.png"]
    (card,) = build_cards(dex, [dex.view(16, "sword-shield")], None, [16])
    assert [t["icon"] for t in card["types"]] == [None, None]


@pytest.fixture
def icon_server(tmp_path):
    from battlelens.stream.server import StreamServer, StreamState

    icons = tmp_path / "type-icons"
    icons.mkdir()
    (icons / "10.png").write_bytes(b"\x89PNG\r\n\x1a\nfalso")
    (tmp_path / "config.toml").write_text("secreto", encoding="utf-8")
    srv = StreamServer(StreamState(), icons)
    assert srv.start(0)
    yield srv
    srv.stop()


def _get(srv, path):
    import http.client

    conn = http.client.HTTPConnection("127.0.0.1", srv.port, timeout=5)
    conn.request("GET", path, headers={"Host": f"localhost:{srv.port}"})
    response = conn.getresponse()
    body = response.read()
    conn.close()
    return response, body


def test_servidor_sirve_el_icono_en_cache(icon_server):
    response, body = _get(icon_server, "/type-icon/10.png")
    assert response.status == 200 and response.getheader("Content-Type") == "image/png"
    assert body.startswith(b"\x89PNG")


@pytest.mark.parametrize("path", ["/type-icon/11.png", "/type-icon/123.png", "/type-icon/../config.toml",
                                  "/type-icon/%2e%2e/config.toml", "/type-icon/x.png", "/type-icon/10.png/",
                                  "/type-icon/10.PNG", "/type-icon/-1.png"])
def test_servidor_rechaza_rutas_no_validas(icon_server, path):
    response, body = _get(icon_server, path)
    assert response.status == 404 and b"secreto" not in body
