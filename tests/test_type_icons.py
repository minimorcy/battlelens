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
