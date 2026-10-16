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
SITE_HOST = "battlelens.minim-labs.app"


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
            if parsed.scheme and tag == "link" and attrs.get("rel") == "canonical":
                assert parsed.netloc == SITE_HOST, url  # no carga nada: solo indica la URL oficial
            elif parsed.scheme:
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


def test_metadatos_para_buscadores_y_redes(page):
    meta = {a.get("property") or a.get("name"): a.get("content") for t, a in page if t == "meta"}
    for key in ("og:title", "og:description", "og:url", "twitter:title", "twitter:description", "description"):
        assert meta.get(key, "").strip(), key
    assert meta["twitter:card"] == "summary_large_image"
    # X y el resto de redes solo aceptan la imagen con URL absoluta
    for key in ("og:image", "twitter:image"):
        url = urlparse(meta[key])
        assert url.scheme == "https" and url.netloc == SITE_HOST, meta[key]
        assert Image.open(SITE / url.path.lstrip("/")).size == (1200, 630)
    assert (int(meta["og:image:width"]), int(meta["og:image:height"])) == (1200, 630)
    assert meta["og:image:alt"].strip() and meta["twitter:image:alt"].strip()
    (canonical,) = [a["href"] for t, a in page if t == "link" and a.get("rel") == "canonical"]
    assert canonical == f"https://{SITE_HOST}/"


def test_robots_y_sitemap():
    robots = (SITE / "robots.txt").read_text(encoding="utf-8")
    assert f"Sitemap: https://{SITE_HOST}/sitemap.xml" in robots
    assert f"<loc>https://{SITE_HOST}/</loc>" in (SITE / "sitemap.xml").read_text(encoding="utf-8")
    dockerfile = (SITE / "Dockerfile").read_text(encoding="utf-8")
    assert "robots.txt" in dockerfile and "sitemap.xml" in dockerfile


def test_datos_estructurados_validos():
    import json

    html = (SITE / "index.html").read_text(encoding="utf-8")
    (block,) = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    data = json.loads(block)
    assert data["@type"] == "SoftwareApplication" and data["name"] == "BattleLens"
    assert data["offers"]["price"] == "0"


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


# ---- analítica opcional con Umami (add-website-analytics) ---------------------------

import shutil  # noqa: E402
import subprocess  # noqa: E402

SH = shutil.which("sh")
UMAMI_URL = "https://umami.minim-labs.app/script.js"
UMAMI_ID = "3f2a9c1e-7b4d-4e8a-9c2f-1a2b3c4d5e6f"


@pytest.fixture
def deployed(tmp_path):
    """Copias de la página y de las cabeceras, como dentro del contenedor."""
    html = tmp_path / "index.html"
    headers = tmp_path / "security-headers.conf"
    shutil.copy2(SITE / "index.html", html)
    shutil.copy2(SITE / "security-headers.conf", headers)
    return html, headers


def _run_umami(deployed, **env):
    html, headers = deployed
    full_env = {"PATH": __import__("os").environ["PATH"], "UMAMI_HTML_PATH": str(html), "UMAMI_HEADERS_PATH": str(headers), **env}
    # cwd junto a los archivos: algunos sed (Git Bash) crean el temporal de «sed -i» en el directorio
    # de trabajo y fallan al moverlo entre unidades (repositorio en D:, temporales en C: en la CI)
    proc = subprocess.run([SH, str(SITE / "docker-entrypoint.d" / "40-umami.sh")], env=full_env,
                          capture_output=True, text=True, timeout=30, cwd=html.parent)
    assert proc.returncode == 0, proc.stderr
    return html.read_text(encoding="utf-8"), headers.read_text(encoding="utf-8"), proc.stdout


needs_sh = pytest.mark.skipif(SH is None, reason="hace falta sh")


def test_marcador_y_eventos_en_la_pagina(page):
    assert "<!-- umami -->" in (SITE / "index.html").read_text(encoding="utf-8")
    events = [(a.get("data-umami-event"), a.get("href")) for t, a in page if t == "a" and a.get("data-umami-event")]
    assert ("download", "https://github.com/minimorcy/battlelens/releases/latest") in events
    assert any(e == "github" for e, _ in events)
    (note,) = [a for _, a in page if a.get("id") == "analytics-note"]
    assert "hidden" in note and "Umami" in note["data-en"] and "Umami" in note["data-es"]


@needs_sh
def test_sin_variables_no_cambia_nada(deployed):
    html, headers, out = _run_umami(deployed)
    assert "<!-- umami -->" in html and "<script defer" not in html
    assert "script-src 'self';" in headers and "connect-src 'none'" in headers
    assert "no configurado" in out


@needs_sh
def test_umami_configurado(deployed):
    html, headers, out = _run_umami(deployed, UMAMI_SCRIPT_URL=UMAMI_URL, UMAMI_WEBSITE_ID=UMAMI_ID,
                                    UMAMI_DOMAINS="battlelens.minim-labs.app")
    assert f'<script defer src="{UMAMI_URL}" data-website-id="{UMAMI_ID}" data-domains="battlelens.minim-labs.app"></script>' in html
    assert "<!-- umami -->" not in html
    assert "script-src 'self' https://umami.minim-labs.app;" in headers
    assert "connect-src https://umami.minim-labs.app;" in headers
    assert "Umami activado" in out


@needs_sh
def test_reinicio_idempotente(deployed):
    env = {"UMAMI_SCRIPT_URL": UMAMI_URL, "UMAMI_WEBSITE_ID": UMAMI_ID}
    _run_umami(deployed, **env)
    html, headers, out = _run_umami(deployed, **env)
    assert html.count("data-website-id") == 1 and headers.count("https://umami.minim-labs.app") == 2  # script-src y connect-src
    assert "ya estaba insertado" in out


@needs_sh
@pytest.mark.parametrize(
    "env",
    [
        {"UMAMI_SCRIPT_URL": "http://umami.minim-labs.app/script.js", "UMAMI_WEBSITE_ID": UMAMI_ID},
        {"UMAMI_SCRIPT_URL": 'https://evil.example/x.js" onload="alert(1)', "UMAMI_WEBSITE_ID": UMAMI_ID},
        {"UMAMI_SCRIPT_URL": UMAMI_URL, "UMAMI_WEBSITE_ID": "no-es-un-uuid"},
        {"UMAMI_SCRIPT_URL": UMAMI_URL, "UMAMI_WEBSITE_ID": UMAMI_ID, "UMAMI_DOMAINS": "a.com; b"},
        {"UMAMI_SCRIPT_URL": UMAMI_URL},
    ],
)
def test_valores_no_validos_no_insertan_nada(deployed, env):
    html, headers, out = _run_umami(deployed, **env)
    assert "<!-- umami -->" in html and "data-website-id" not in html
    assert "script-src 'self';" in headers
    assert "AVISO" in out



def test_captura_de_partida_con_credito(page):
    (img,) = [a for t, a in page if t == "img" and a.get("src") == "assets/gameplay.jpg"]
    assert (int(img["width"]), int(img["height"])) == Image.open(SITE / "assets" / "gameplay.jpg").size
    (credit,) = [a for _, a in page if a.get("id") == "gameplay-credit"]
    for lang in ("data-en", "data-es"):
        assert "Nintendo" in credit[lang] and "GAME FREAK" in credit[lang]


# ---- guía de uso (add-user-guide) ------------------------------------------------------

GUIDE = SITE / "guide.html"


def _parse(html: str) -> list[tuple[str, dict]]:
    parser = _Collector()
    parser.feed(html)
    return parser.elements


@pytest.fixture(scope="module")
def guide():
    return _parse(GUIDE.read_text(encoding="utf-8"))


def _guide_blocks() -> dict[str, list[tuple[str, dict]]]:
    """Elementos del bloque de cada idioma (<div class="guide" data-lang="…">)."""
    html = GUIDE.read_text(encoding="utf-8")
    es_start = html.index('<div class="guide" data-lang="es"')
    en_start = html.index('<div class="guide" data-lang="en"')
    end = html.index("</main>")
    return {"es": _parse(html[es_start:en_start]), "en": _parse(html[en_start:end])}


def test_guia_enlazada_desde_la_portada(page):
    links = [a for t, a in page if t == "a" and a.get("href") == "guide.html"]
    assert any(a.get("data-umami-event") == "guide" for a in links)
    dockerfile = (SITE / "Dockerfile").read_text(encoding="utf-8")
    assert "guide.html" in dockerfile
    assert f"<loc>https://{SITE_HOST}/guide.html</loc>" in (SITE / "sitemap.xml").read_text(encoding="utf-8")


def test_guia_recursos_locales_y_paridad(guide):
    for tag, attrs in guide:
        for key in ("src", "href"):
            url = attrs.get(key)
            if not url or url.startswith("#"):
                continue
            parsed = urlparse(url)
            if parsed.scheme:
                assert (tag == "a" and parsed.netloc in ALLOWED_EXTERNAL_HOSTS) or (
                    tag == "link" and attrs.get("rel") == "canonical" and parsed.netloc == SITE_HOST), url
            else:
                assert (SITE / parsed.path).is_file(), f"falta {url}"
        for suffix in ("", "-alt", "-content", "-aria-label"):
            assert (f"data-en{suffix}" in attrs) == (f"data-es{suffix}" in attrs), (tag, attrs)
    assert "<!-- umami -->" in GUIDE.read_text(encoding="utf-8")
    (attrs,) = [a for _, a in guide if a.get("id") == "disclaimer"]
    assert "unofficial fan project" in attrs["data-en"] and "proyecto de fans no oficial" in attrs["data-es"]


def test_guia_mismo_contenido_en_los_dos_idiomas():
    blocks = _guide_blocks()

    def shape(elements):
        return [t for t, a in elements if t in ("section", "h2", "h3", "figure", "img", "table", "details", "kbd")]

    assert shape(blocks["es"]) == shape(blocks["en"])
    images = {lang: [a["src"] for t, a in els if t == "img"] for lang, els in blocks.items()}
    assert images["es"] == [src.replace("/en/", "/es/") for src in images["en"]]
    assert all(src.startswith("assets/guide/es/") for src in images["es"])


def test_guia_indice_apunta_a_secciones_de_su_idioma():
    all_ids = []
    for elements in _guide_blocks().values():
        ids = {a["id"] for _, a in elements if "id" in a}
        all_ids += [a["id"] for _, a in elements if "id" in a]
        targets = [a["href"][1:] for t, a in elements if t == "a" and a.get("href", "").startswith("#")]
        assert targets and all(t in ids for t in targets), set(targets) - ids
    assert len(all_ids) == len(set(all_ids)), "ids repetidos entre idiomas"


def test_guia_capturas_con_alt_y_tamano_correcto(guide):
    imgs = [a for t, a in guide if t == "img" and a["src"].startswith("assets/guide/")]
    assert len(imgs) >= 28
    for attrs in imgs:
        assert attrs.get("alt", "").strip(), attrs["src"]
        width, height = Image.open(SITE / attrs["src"]).size
        assert (int(attrs["width"]), int(attrs["height"])) == (width // 2, height // 2), attrs["src"]
    (credit,) = [a for _, a in guide if a.get("id") == "guide-credit"]
    for lang in ("data-en", "data-es"):
        assert "Nintendo" in credit[lang] and "GAME FREAK" in credit[lang]


@needs_sh
def test_umami_en_portada_y_guia(tmp_path):
    pages = []
    for name in ("index.html", "guide.html"):
        shutil.copy2(SITE / name, tmp_path / name)
        pages.append(tmp_path / name)
    headers = tmp_path / "security-headers.conf"
    shutil.copy2(SITE / "security-headers.conf", headers)
    env = {"PATH": __import__("os").environ["PATH"], "UMAMI_HTML_PATH": " ".join(str(p) for p in pages),
           "UMAMI_HEADERS_PATH": str(headers), "UMAMI_SCRIPT_URL": UMAMI_URL, "UMAMI_WEBSITE_ID": UMAMI_ID}
    for _ in range(2):  # el segundo arranque no cambia nada
        proc = subprocess.run([SH, str(SITE / "docker-entrypoint.d" / "40-umami.sh")], env=env,
                              capture_output=True, text=True, timeout=30, cwd=tmp_path)
        assert proc.returncode == 0, proc.stderr
    for path in pages:
        assert path.read_text(encoding="utf-8").count("data-website-id") == 1, path.name
    assert headers.read_text(encoding="utf-8").count("https://umami.minim-labs.app") == 2
