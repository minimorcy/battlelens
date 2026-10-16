"""Genera la imagen para redes sociales de la web (site/assets/og-image.png, 1200x630).

Uso:  uv run python tools/make_og_image.py

Es la que muestran X, Discord, WhatsApp… al compartir el enlace. Va en inglés (más alcance) y usa
la ficha real de BattleLens en inglés, sin imágenes de los juegos. Necesita las fuentes Segoe UI de Windows.
"""

from __future__ import annotations

import os
import sys
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "assets" / "og-image.png"
ICON = ROOT / "src" / "battlelens" / "assets" / "icon.png"
FONTS = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
GAME = "sword-shield"
W, H = 1200, 630

BG = (15, 18, 24)
TEXT = (238, 240, 245)
MUTED = (163, 169, 188)
ACCENT = (255, 203, 5)
GRADIENT = [(255, 224, 102), (255, 159, 67), (248, 88, 136)]


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def render_card(mode: str, species: int, level: int, own: int, own_level: int) -> Image.Image:
    """La ficha real de la app, en inglés y a doble resolución."""
    os.environ.setdefault("QT_SCALE_FACTOR", "2")
    sys.path.insert(0, str(ROOT / "src"))
    from PyQt6.QtCore import QBuffer, QByteArray, QIODevice
    from PyQt6.QtWidgets import QApplication

    from battlelens.core.pokedex import Pokedex
    from battlelens.i18n import set_language
    from battlelens.ui.overlay import Overlay

    app = QApplication.instance() or QApplication([])
    set_language("en")
    dex = Pokedex.load()
    overlay = Overlay(dex, "en", mode=mode)
    overlay._available_height = lambda rect: 100_000  # ficha completa, sin desplazamiento
    overlay.show_battle([dex.view(species, GAME, "en")], dex.view(own, GAME, "en"), None, [level], own_level)
    for _ in range(5):
        app.processEvents()
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    overlay.grab().save(buffer, "PNG")
    buffer.close()
    overlay.close()
    return Image.open(BytesIO(bytes(data))).convert("RGBA")


def glow(base: Image.Image, center: tuple[float, float], radius: float, color: tuple[int, int, int], strength: float) -> None:
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.hypot(xx - center[0], yy - center[1]) / radius
    alpha = np.clip(1 - dist, 0, 1) ** 2 * strength
    layer = Image.new("RGBA", (W, H), color + (0,))
    layer.putalpha(Image.fromarray((alpha * 255).astype(np.uint8)))
    base.alpha_composite(layer)


def gradient_text(img: Image.Image, xy: tuple[int, int], text: str, fnt: ImageFont.FreeTypeFont) -> None:
    left, top, right, bottom = fnt.getbbox(text)
    w, h = right, bottom
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((0, 0), text, font=fnt, fill=255)
    x = np.linspace(0, 1, w)
    stops = np.array(GRADIENT, dtype=float)
    pos = np.linspace(0, 1, len(stops))
    rgb = np.stack([np.interp(x, pos, stops[:, c]) for c in range(3)], axis=-1)
    fill = Image.fromarray(np.repeat(rgb[None, :, :], h, axis=0).astype(np.uint8), "RGB").convert("RGBA")
    fill.putalpha(mask)
    img.alpha_composite(fill, xy)


def place_card(img: Image.Image, card: Image.Image, height: int, xy: tuple[int, int], angle: float) -> None:
    card = card.resize((round(card.width * height / card.height), height), Image.Resampling.LANCZOS)
    card = card.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    shadow = Image.new("RGBA", (card.width + 120, card.height + 120), (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 170), (60, 80), card.split()[3])
    shadow = shadow.filter(ImageFilter.GaussianBlur(26))
    img.alpha_composite(shadow, (xy[0] - 60, xy[1] - 60))
    img.alpha_composite(card, xy)


def main() -> int:
    normal = render_card("normal", 759, 10, 813, 14)  # Stufful contra tu Scorbunny
    competitive = render_card("competitive", 759, 10, 813, 14)

    img = Image.new("RGBA", (W, H), BG + (255,))
    glow(img, (260, 40), 520, (255, 203, 5), 0.20)
    glow(img, (1080, 560), 560, (248, 88, 136), 0.22)
    glow(img, (40, 640), 480, (91, 140, 255), 0.18)
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lines = ImageDraw.Draw(grid)
    for x in range(0, W, 48):
        lines.line([(x, 0), (x, H)], fill=(255, 255, 255, 10))
    for y in range(0, H, 48):
        lines.line([(0, y), (W, y)], fill=(255, 255, 255, 10))
    img.alpha_composite(grid)

    # Fichas a la derecha: la competitiva asoma detrás de la normal
    place_card(img, competitive.crop((0, 0, competitive.width, round(competitive.width * 1.25))), 450, (905, 60), -5)
    place_card(img, normal, 410, (770, 160), 3)

    # Marca
    logo = Image.open(ICON).convert("RGBA").resize((76, 76), Image.Resampling.LANCZOS)
    img.alpha_composite(logo, (72, 64))
    draw = ImageDraw.Draw(img)
    draw.text((166, 76), "BattleLens", font=font("segoeuib.ttf", 42), fill=TEXT)

    # Titular
    big = font("seguibl.ttf", 58)
    draw.text((72, 200), "Know your opponent", font=big, fill=TEXT)
    gradient_text(img, (72, 272), "before you make", big)
    gradient_text(img, (72, 344), "a move.", big)

    draw = ImageDraw.Draw(img)
    draw.text((74, 446), "Instant Pokémon battle info", font=font("segoeui.ttf", 27), fill=MUTED)
    draw.text((74, 482), "next to any PC emulator. Free for Windows.", font=font("segoeui.ttf", 27), fill=MUTED)
    draw.text((74, 552), "battlelens.minim-labs.app", font=font("segoeuib.ttf", 27), fill=ACCENT)

    img.convert("RGB").save(OUT, optimize=True)
    print(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
