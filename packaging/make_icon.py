"""Genera el icono de BattleLens a partir del logo vectorial (packaging/logo.svg): una lupa con un rayo.

Uso:  uv run python packaging/make_icon.py
Salidas: src/battlelens/assets/icon.png (256 px, para Qt), packaging/battlelens.ico (16-256 px)
y la copia de ambos en la web (site/assets/icon.png, site/assets/favicon.ico, site/assets/logo.svg).
"""

from __future__ import annotations

import shutil
from io import BytesIO
from pathlib import Path

from PIL import Image
from PyQt6.QtCore import QBuffer, QByteArray, QIODevice
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtSvg import QSvgRenderer

ROOT = Path(__file__).resolve().parent.parent
SVG = ROOT / "packaging" / "logo.svg"
PNG_OUT = ROOT / "src" / "battlelens" / "assets" / "icon.png"
ICO_OUT = ROOT / "packaging" / "battlelens.ico"
SITE_ASSETS = ROOT / "site" / "assets"
ICO_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def render(size: int = 1024) -> Image.Image:
    renderer = QSvgRenderer(str(SVG))
    if not renderer.isValid():
        raise SystemExit(f"SVG no válido: {SVG}")
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(0)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter)
    painter.end()
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    buffer.close()
    return Image.open(BytesIO(bytes(data))).convert("RGBA")


def main() -> None:
    master = render(1024)
    icon = master.resize((256, 256), Image.Resampling.LANCZOS)
    PNG_OUT.parent.mkdir(parents=True, exist_ok=True)
    icon.save(PNG_OUT)
    icon.save(ICO_OUT, sizes=ICO_SIZES)
    shutil.copy2(PNG_OUT, SITE_ASSETS / "icon.png")
    shutil.copy2(ICO_OUT, SITE_ASSETS / "favicon.ico")
    shutil.copy2(SVG, SITE_ASSETS / "logo.svg")
    print(f"{PNG_OUT}\n{ICO_OUT}\n{SITE_ASSETS}")


if __name__ == "__main__":
    main()
