"""Genera el icono original de BattleLens: una lupa sobre barras de estadísticas.

Uso:  uv run python packaging/make_icon.py
Salidas: src/battlelens/assets/icon.png (256 px, para Qt) y packaging/battlelens.ico (16-256 px).
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
PNG_OUT = ROOT / "src" / "battlelens" / "assets" / "icon.png"
ICO_OUT = ROOT / "packaging" / "battlelens.ico"
ICO_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

BG = (31, 36, 48, 255)
BARS = [(242, 95, 92, 255), (255, 200, 87, 255), (61, 220, 151, 255)]
LENS_RING = (240, 244, 250, 255)
LENS_GLASS = (120, 190, 255, 70)
HANDLE = (240, 244, 250, 255)


def render(size: int = 1024) -> Image.Image:
    s = size / 1024
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((32 * s, 32 * s, 992 * s, 992 * s), radius=200 * s, fill=BG)

    # Barras de estadísticas (izquierda a derecha, de baja a alta)
    base = 820 * s
    for i, (height, color) in enumerate(zip((260, 420, 580), BARS)):
        x0 = (170 + i * 190) * s
        d.rounded_rectangle((x0, base - height * s, x0 + 130 * s, base), radius=36 * s, fill=color)

    # Lupa
    cx, cy, r = 600 * s, 430 * s, 230 * s
    glass = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glass).ellipse((cx - r, cy - r, cx + r, cy + r), fill=LENS_GLASS)
    img.alpha_composite(glass)
    d = ImageDraw.Draw(img)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=LENS_RING, width=round(54 * s))
    d.line((cx + 0.70 * r, cy + 0.70 * r, 900 * s, 880 * s), fill=HANDLE, width=round(92 * s))
    d.ellipse((900 * s - 46 * s, 880 * s - 46 * s, 900 * s + 46 * s, 880 * s + 46 * s), fill=HANDLE)
    return img


def main() -> None:
    master = render(1024)
    PNG_OUT.parent.mkdir(parents=True, exist_ok=True)
    master.resize((256, 256), Image.Resampling.LANCZOS).save(PNG_OUT)
    master.resize((256, 256), Image.Resampling.LANCZOS).save(ICO_OUT, sizes=ICO_SIZES)
    print(f"{PNG_OUT}\n{ICO_OUT}")


if __name__ == "__main__":
    main()
