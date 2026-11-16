"""Sprites de los Pokémon: número por forma, descarga validada con recorte, cabecera y stream (add-pokemon-sprites).

Sin red: la descarga se inyecta. Los sprites son rectángulos generados aquí (los reales tienen copyright).
"""

import threading

import pytest
from PIL import Image

from battlelens.core.sprites import MAX_SPRITE_BYTES, SPRITE_URL, Sprites


def fake_sprite(box=(10, 40, 50, 90), size: int = 96) -> bytes:
    """Lienzo transparente de 96×96 con un rectángulo opaco abajo a la izquierda, como los sprites de PokéAPI."""
    import io

    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    image.paste((200, 60, 60, 255), box)
    out = io.BytesIO()
    image.save(out, "PNG")
    return out.getvalue()


@pytest.fixture(scope="module")
def dex():
    from battlelens.core.pokedex import Pokedex

    return Pokedex.load()


def wait(sprites: Sprites, qapp, sprite_id: int) -> None:
    for _ in range(200):
        qapp.processEvents()
        if sprite_id not in sprites._pending:
            qapp.processEvents()  # entrega la señal `arrived` en cola
            return
        threading.Event().wait(0.02)
    raise AssertionError("la descarga no terminó")


# ---- datos ---------------------------------------------------------------------

@pytest.mark.parametrize(("species", "game", "form", "sprite_id"), [
    (759, "sword-shield", None, 759),  # Stufful
    (263, "sword-shield", None, 10174),  # Zigzagoon de Galar en Espada
    (479, "platinum", "rotom-wash", 10009),  # Rotom Lavado
    (6, "x-y", "charizard-mega-x", 10034),  # Mega Charizard X
])
def test_numero_de_sprite_por_especie_y_forma(dex, species, game, form, sprite_id):
    assert dex.view(species, game, "es", form).sprite_id == sprite_id


# ---- caché ---------------------------------------------------------------------

def test_descarga_recorta_al_contorno(qapp, tmp_path):
    urls = []
    sprites = Sprites(tmp_path, lambda url, limit: urls.append(url) or fake_sprite())
    got = []
    sprites.arrived.connect(got.append)
    assert sprites.request(759)
    wait(sprites, qapp, 759)
    assert urls == [SPRITE_URL.format(id=759)] and got == [759]
    with Image.open(sprites.path(759)) as image:
        assert image.size == (40, 50)  # solo la caja de los píxeles visibles
    assert sorted(p.name for p in tmp_path.iterdir()) == ["759.png"]  # sin restos temporales


def test_ya_en_cache_no_hace_peticiones(qapp, tmp_path):
    (tmp_path / "759.png").write_bytes(fake_sprite())
    sprites = Sprites(tmp_path, lambda url, limit: pytest.fail("no debía descargar"))
    assert sprites.request(759) and not sprites._pending


@pytest.mark.parametrize("body", [b"<html>404</html>", b"x" * (MAX_SPRITE_BYTES + 1), fake_sprite((0, 0, 0, 0))],
                         ids=["html", "grande", "vacio"])
def test_respuesta_no_valida_no_guarda_nada(qapp, tmp_path, body):
    sprites = Sprites(tmp_path, lambda url, limit: body)
    sprites.request(759)
    wait(sprites, qapp, 759)
    assert not list(tmp_path.iterdir())
    assert sprites.request(759) is False  # fallo recordado: no se reintenta en la sesión


def test_fallo_de_red_recordado_en_la_sesion(qapp, tmp_path):
    calls = []

    def offline(url, limit):
        calls.append(url)
        raise OSError("sin conexión")

    sprites = Sprites(tmp_path, offline)
    sprites.request(759)
    wait(sprites, qapp, 759)
    assert sprites.request(759) is False and len(calls) == 1


def test_pixmap_nitido_como_mucho_x2(qapp, tmp_path):
    (tmp_path / "1.png").write_bytes(fake_sprite((0, 0, 20, 10)))  # 20×10 → ×2 (cabría ×2,4)
    (tmp_path / "2.png").write_bytes(fake_sprite((0, 0, 80, 40)))  # 80×40 → se reduce a 48 de ancho
    sprites = Sprites(tmp_path)
    for path in tmp_path.glob("*.png"):
        from battlelens.core.sprites import crop_to_content

        crop_to_content(path)
    small, big = sprites.pixmap(1, 48), sprites.pixmap(2, 48)
    ratio = small.devicePixelRatio()
    assert (small.width() / ratio, small.height() / ratio) == (40, 20)
    assert big.width() / ratio == 48
    assert sprites.pixmap(3, 48) is None


# ---- cabecera ------------------------------------------------------------------

def _card(dex, sprites, species=759):
    from battlelens.ui.overlay import Overlay

    o = Overlay(dex, "es", mode="normal")
    o._available_height = lambda rect: 100_000
    o.sprites = sprites
    o.show_battle([dex.view(species, "sword-shield", "es")], None, None, [10])
    return o


def _slot(overlay):
    from PyQt6.QtWidgets import QLabel

    return overlay.findChild(QLabel, "sprite")


def test_cabecera_con_imagen_en_cache(qapp, dex, tmp_path):
    (tmp_path / "759.png").write_bytes(fake_sprite())
    o = _card(dex, Sprites(tmp_path, lambda url, limit: pytest.fail("no debía descargar")))
    slot = _slot(o)
    assert slot is not None and not slot.pixmap().isNull() and slot.accessibleName() == "Stufful"
    o.close()


def test_imagen_que_llega_despues_sin_redibujar(qapp, dex, tmp_path):
    gate = threading.Event()  # la descarga espera a que la ficha esté dibujada
    sprites = Sprites(tmp_path, lambda url, limit: gate.wait(5) and fake_sprite())
    o = _card(dex, sprites)
    sprites.arrived.connect(o.sprite_arrived)
    slot = _slot(o)
    assert slot is not None and slot.pixmap().isNull()  # recuadro reservado mientras llega
    gate.set()
    wait(sprites, qapp, 759)
    assert _slot(o) is slot and not slot.pixmap().isNull()
    o.close()


def test_imagenes_desactivadas_sin_recuadro(qapp, dex):
    o = _card(dex, None)
    assert _slot(o) is None
    o.close()


def test_sin_conexion_sin_recuadro(qapp, dex, tmp_path):
    sprites = Sprites(tmp_path, lambda url, limit: (_ for _ in ()).throw(OSError("sin red")))
    sprites.request(759)
    wait(sprites, qapp, 759)
    o = _card(dex, sprites)
    assert _slot(o) is None
    o.close()


# ---- stream --------------------------------------------------------------------

def test_payload_con_sprite_solo_si_esta_en_cache(dex):
    from battlelens.stream.payload import build_cards

    view = dex.view(759, "sword-shield")
    (card,) = build_cards(dex, [view], None, [10], has_sprite=lambda sid: sid == 759)
    assert card["sprite"] == "/sprite/759.png"
    (card,) = build_cards(dex, [view], None, [10], has_sprite=lambda sid: False)
    assert card["sprite"] is None
    (card,) = build_cards(dex, [view], None, [10])
    assert card["sprite"] is None


@pytest.fixture
def sprite_server(tmp_path):
    from battlelens.stream.server import StreamServer, StreamState

    sprites = tmp_path / "sprites"
    sprites.mkdir()
    (sprites / "759.png").write_bytes(b"\x89PNG\r\n\x1a\nfalso")
    (tmp_path / "config.toml").write_text("secreto", encoding="utf-8")
    srv = StreamServer(StreamState(), None, sprites)
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


def test_servidor_sirve_el_sprite_en_cache(sprite_server):
    response, body = _get(sprite_server, "/sprite/759.png")
    assert response.status == 200 and response.getheader("Content-Type") == "image/png"


@pytest.mark.parametrize("path", ["/sprite/123.png", "/sprite/..%2Fconfig.png", "/sprite/../config.toml",
                                  "/sprite/123456.png", "/sprite/x.png", "/sprite/759.png/"])
def test_servidor_rechaza_rutas_no_validas(sprite_server, path):
    response, body = _get(sprite_server, path)
    assert response.status == 404 and b"secreto" not in body
