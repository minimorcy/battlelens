"""Modo stream: payload, servidor local y configuración (add-stream-mode)."""

import http.client
import json
import socket

import pytest

from battlelens.core.config import Config, ConfigError
from battlelens.core.learnsets import Learnsets
from battlelens.core.pokedex import Pokedex
from battlelens.stream.payload import build_cards
from battlelens.stream.server import StreamServer, StreamState


@pytest.fixture(scope="module")
def dex():
    return Pokedex.load()


# ---- contenido ------------------------------------------------------------------------------

def test_tarjeta_normal_machop_contra_scorbunny(dex):
    moves = [Learnsets.get().move(i) for i in ("ember", "growl")]
    (card,) = build_cards(dex, [dex.view(66, "sword-shield")], dex.view(813, "sword-shield"), [16], moves)
    assert card["name"] == "Machop" and card["number"] == "#0066" and card["level"] is None
    assert [t["label"] for t in card["types"]] == ["Lucha"] and card["types"][0]["color"] == "#C22E28"
    assert card["capture"]["text"] == "Captura: 180 · Media"
    assert card["versus"]["title"] == "Contra tu Scorbunny" and card["versus"]["verdict"]["label"] == "Neutral"
    assert [(m["name"], m["mult"]) for m in card["moves"]["items"]] == [("Ascuas", "×1"), ("Gruñido", "Estado")]
    (weak,) = card["groups"]
    assert weak["title"] == "Debilidades"
    assert [t["label"] for t in weak["rows"][0]["types"]] == ["Volador", "Psíquico", "Hada"]
    assert card["stats"] is None and card["total"] == "Total estadísticas base: 305"


def test_tarjeta_competitiva(dex):
    (card,) = build_cards(dex, [dex.view(66, "sword-shield")], None, [16], mode="competitive")
    assert card["level"] == "Nv. 16"
    assert [g["title"] for g in card["groups"]] == ["Debilidades", "Resistencias"]
    assert card["stats"]["total"] == 305 and len(card["stats"]["rows"]) == 6


def test_tarjeta_en_ingles_con_datos_en_espanol(dex):
    """Interfaz en inglés (add-english-ui D5): títulos y etiquetas de card.js traducidos; datos en español."""
    import battlelens.i18n as i18n

    moves = [Learnsets.get().move(i) for i in ("ember", "growl")]
    try:
        i18n.set_language("en")
        (card,) = build_cards(dex, [dex.view(66, "sword-shield")], dex.view(813, "sword-shield"), [16], moves,
                              mode="competitive")
    finally:
        i18n.set_language("es")
    assert card["labels"] == {"you": "You", "them": "Them", "total": "Total"}
    assert card["level"] == "Lv. 16" and card["capture"]["text"] == "Catch rate: 180 · Medium"
    assert card["versus"]["title"] == "Against your Scorbunny"
    assert card["versus"]["verdict"] == {"label": "Neutral", "key": "neutral"}
    assert [(m["name"], m["mult"]) for m in card["moves"]["items"]] == [("Ascuas", "×1"), ("Gruñido", "Status")]
    assert [g["title"] for g in card["groups"]] == ["Weaknesses", "Resistances"]
    assert [t["label"] for t in card["groups"][0]["rows"][0]["types"]] == ["Volador", "Psíquico", "Hada"]
    assert card["stats"]["title"] == "Base stats" and card["stats"]["rows"][0]["label"] == "HP"


def test_etiquetas_de_card_js_en_espanol(dex):
    (card,) = build_cards(dex, [dex.view(66, "sword-shield")], None, [None])
    assert card["labels"] == {"you": "Tú", "them": "Él", "total": "Total"}


def test_textos_de_habilidades_iguales_que_la_ficha(dex):
    (card,) = build_cards(dex, [dex.view(437, "platinum")], dex.view(445, "platinum"), [None])
    assert "Si tiene Levitación: Tierra ×0" in card["ability_lines"]
    assert "Tierra: ×0 si tiene Levitación" in card["versus"]["notes"]
    assert any(t["label"] == "Tierra ×2*" for t in card["versus"]["you"])


# ---- estado ---------------------------------------------------------------------------------

def test_estado_visibilidad_y_contador():
    state = StreamState()
    assert state.snapshot() == {"seq": 0, "visible": False, "mode": "normal", "cards": []}
    state.set_visible(True)  # sin tarjetas no se muestra nada
    assert not state.visible and state.snapshot()["seq"] == 0
    state.publish([{"name": "Machop"}])
    assert state.visible and state.snapshot()["seq"] == 1
    state.set_visible(False)
    assert not state.visible and state.snapshot()["seq"] == 2
    state.set_visible(False)  # sin cambios: el contador no avanza
    assert state.snapshot()["seq"] == 2


# ---- servidor -------------------------------------------------------------------------------

@pytest.fixture
def server():
    state = StreamState()
    state.publish([{"name": "Machop"}])
    srv = StreamServer(state)
    assert srv.start(0)  # puerto libre cualquiera
    yield srv
    srv.stop()


def _get(srv, path, host=None, method="GET"):
    conn = http.client.HTTPConnection("127.0.0.1", srv.port, timeout=5)
    conn.request(method, path, headers={"Host": host or f"localhost:{srv.port}"})
    response = conn.getresponse()
    body = response.read()
    conn.close()
    return response, body


def test_pagina_y_estado(server):
    response, body = _get(server, "/")
    assert response.status == 200 and b"card.js" in body
    assert response.getheader("Content-Security-Policy").startswith("default-src 'self'")
    assert response.getheader("Cache-Control") == "no-store"
    for path in ("/card.css", "/card.js"):
        assert _get(server, path)[0].status == 200
    response, body = _get(server, "/state?x=1", host=f"127.0.0.1:{server.port}")
    assert response.status == 200
    assert json.loads(body) == {"seq": 1, "visible": True, "mode": "normal", "cards": [{"name": "Machop"}]}


def test_host_ajeno_rechazado(server):
    response, body = _get(server, "/state", host="ejemplo.com")
    assert response.status == 403 and b"Machop" not in body
    assert _get(server, "/state", host=f"ejemplo.com:{server.port}")[0].status == 403


@pytest.mark.parametrize("path", ["/otra", "/../config.toml", "/static/card.js", "/%2e%2e/pyproject.toml"])
def test_rutas_desconocidas(server, path):
    assert _get(server, path)[0].status == 404


def test_solo_get(server):
    assert _get(server, "/state", method="POST")[0].status == 501


def test_solo_escucha_en_local(server):
    assert server.url == f"http://localhost:{server.port}/"
    assert server._httpd.server_address[0] == "127.0.0.1"


def test_puerto_ocupado():
    busy = socket.socket()
    busy.bind(("127.0.0.1", 0))
    busy.listen()
    try:
        srv = StreamServer(StreamState())
        assert not srv.start(busy.getsockname()[1]) and not srv.running and srv.url is None
    finally:
        busy.close()


def test_parar_libera_el_puerto(server):
    port = server.port
    server.stop()
    again = StreamServer(StreamState())
    assert again.start(port)
    again.stop()


# ---- configuración --------------------------------------------------------------------------

def test_configuracion_por_defecto_y_validacion():
    cfg = Config.from_toml("")
    assert not cfg.stream_enabled and cfg.stream_port == 17320 and cfg.stream_card_mode == "normal"
    assert cfg.hotkey_toggle_stream == "Ctrl+Alt+S"
    cfg = Config.from_toml('[stream]\nenabled = true\nport = 18000\ncard_mode = "competitive"\n')
    assert cfg.stream_enabled and cfg.stream_port == 18000 and cfg.stream_card_mode == "competitive"
    for bad in ("[stream]\nport = 80\n", "[stream]\nport = \"x\"\n", '[stream]\ncard_mode = "mega"\n',
                "[stream]\nenabled = 1\n"):
        with pytest.raises(ConfigError):
            Config.from_toml(bad)


def test_configuracion_se_guarda_con_el_stream(tmp_path):
    from dataclasses import replace

    from battlelens.core.config import load_config, save_config

    cfg = replace(Config(), stream_enabled=True, stream_port=18001)
    save_config(tmp_path / "config.toml", cfg)
    assert load_config(tmp_path / "config.toml") == cfg
