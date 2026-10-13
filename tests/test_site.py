"""Web del proyecto (spec project-website) y README bilingüe (spec project-readme)."""

import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
ALLOWED_EXTERNAL_HOSTS = {"github.com", "pokeapi.co"}


class _Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements: list[tuple[str, dict]] = []

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    handle_startendtag = handle_starttag


@pytest.fixture(scope="module")
def page():
    parser = _Collector()
    parser.feed((SITE / "index.html").read_text(encoding="utf-8"))
    return parser.elements


def test_paridad_de_idiomas(page):
    for suffix in ("", "-alt", "-content", "-aria-label"):
        for tag, attrs in page:
            has_en, has_es = f"data-en{suffix}" in attrs, f"data-es{suffix}" in attrs
            assert has_en == has_es, (tag, attrs)
            if has_en:
                assert attrs[f"data-en{suffix}"].strip() and attrs[f"data-es{suffix}"].strip()
    assert sum("data-en" in a for _, a in page) >= 40


def test_recursos_locales_existen_y_no_hay_externos(page):
    for tag, attrs in page:
        for key in ("src", "href"):
            url = attrs.get(key)
            if not url or url.startswith(("#", "mailto:")):
                continue
            parsed = urlparse(url)
            if parsed.scheme:
                assert tag == "a", f"recurso externo no permitido: <{tag} {key}={url}>"
                assert parsed.netloc in ALLOWED_EXTERNAL_HOSTS, url
            else:
                assert (SITE / parsed.path).is_file(), f"falta {url}"


def test_textos_traducidos_no_cargan_recursos_externos(page):
    # los enlaces dentro de data-en/data-es también deben ir solo a dominios permitidos
    for _, attrs in page:
        for key in ("data-en", "data-es"):
            for host in re.findall(r'https?://([^/"]+)', attrs.get(key, "")):
                assert host in ALLOWED_EXTERNAL_HOSTS, host


def test_descarga_apunta_a_la_ultima_release(page):
    links = [a.get("href") for t, a in page if t == "a" and a.get("id") == "download"]
    assert links == ["https://github.com/minimorcy/battlelens/releases/latest"]


def test_aviso_legal_en_ambos_idiomas(page):
    (attrs,) = [a for _, a in page if a.get("id") == "disclaimer"]
    assert "unofficial fan project" in attrs["data-en"] and "Nintendo" in attrs["data-en"]
    assert "proyecto de fans no oficial" in attrs["data-es"] and "Nintendo" in attrs["data-es"]


def test_imagenes_con_alt_y_tamano_correcto(page):
    for tag, attrs in page:
        if tag != "img":
            continue
        assert "alt" in attrs
        size = Image.open(SITE / attrs["src"]).size
        if attrs["src"].startswith("assets/card-"):  # capturas a doble resolución
            assert (int(attrs["width"]), int(attrs["height"])) == (size[0] // 2, size[1] // 2), attrs["src"]


def test_capturas_generadas():
    for name in ("card-normal.png", "card-competitive.png", "card-double.png", "icon.png", "favicon.ico"):
        assert (SITE / "assets" / name).is_file(), name


def test_csp_estricta_en_nginx():
    headers = (SITE / "security-headers.conf").read_text(encoding="utf-8")
    assert "default-src 'self'" in headers and "unsafe-inline" not in headers
    conf = (SITE / "nginx.conf").read_text(encoding="utf-8")
    assert conf.count("include /etc/nginx/snippets/security-headers.conf;") >= 3
    assert "location = /health" in conf


def test_readme_bilingue():
    en = (ROOT / "README.md").read_text(encoding="utf-8")
    es = (ROOT / "README.es.md").read_text(encoding="utf-8")
    assert "[Español](README.es.md)" in en.splitlines()[2] and "[English](README.md)" in es.splitlines()[2]
    assert "battlelens.minim-labs.app" in en.splitlines()[2] and "battlelens.minim-labs.app" in es.splitlines()[2]
    for level in ("## ", "### "):
        assert sum(l.startswith(level) for l in en.splitlines()) == sum(l.startswith(level) for l in es.splitlines())
