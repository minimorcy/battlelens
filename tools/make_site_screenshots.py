"""Genera las capturas de la web (site/assets/) a partir de la interfaz real de BattleLens.

Uso:  uv run python tools/make_site_screenshots.py

Solo usa la ficha de la app (sin imágenes de los juegos). Se renderiza a doble resolución
para que se vea nítida en pantallas HiDPI.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "site" / "assets"
GAME = "sword-shield"

# (archivo, modo, rivales [(especie, nivel)], tu Pokémon (especie, nivel) o None)
SHOTS = [
    ("card-normal.png", "normal", [(759, 10)], (813, 14)),  # Stufful contra tu Scorbunny
    ("card-competitive.png", "competitive", [(759, 10)], (813, 14)),
    ("card-double.png", "normal", [(263, 8), (759, 10)], (813, 14)),  # Zigzagoon de Galar + Stufful
]


def sync_html_sizes() -> None:
    """Actualiza width/height de las capturas en index.html (tamaño lógico = la mitad del PNG)."""
    from PIL import Image

    index = ROOT / "site" / "index.html"
    html = index.read_text(encoding="utf-8")

    def fix(match: re.Match) -> str:
        width, height = Image.open(ASSETS / match.group(1)).size
        return f'src="assets/{match.group(1)}" width="{width // 2}" height="{height // 2}"'

    html = re.sub(r'src="assets/(card-[a-z-]+\.png)" width="\d+" height="\d+"', fix, html)
    index.write_text(html, encoding="utf-8")


def main() -> int:
    os.environ.setdefault("QT_SCALE_FACTOR", "2")
    sys.path.insert(0, str(ROOT / "src"))
    from PyQt6.QtWidgets import QApplication

    app = QApplication([])
    from battlelens.core.pokedex import Pokedex
    from battlelens.ui.overlay import Overlay

    dex = Pokedex.load()
    ASSETS.mkdir(parents=True, exist_ok=True)
    for filename, mode, rivals, own in SHOTS:
        overlay = Overlay(dex, "es", mode=mode)
        overlay._available_height = lambda rect: 100_000  # captura de la ficha completa, sin desplazamiento
        views = [dex.view(sid, GAME, "es") for sid, _ in rivals]
        own_view = dex.view(own[0], GAME, "es") if own else None
        overlay.show_battle(views, own_view, None, [lvl for _, lvl in rivals], own[1] if own else None)
        for _ in range(5):
            app.processEvents()
        overlay.grab().save(str(ASSETS / filename))
        overlay.close()
        print(ASSETS / filename)
    sync_html_sizes()
    shutil.copy2(ROOT / "src" / "battlelens" / "assets" / "icon.png", ASSETS / "icon.png")
    shutil.copy2(ROOT / "packaging" / "battlelens.ico", ASSETS / "favicon.ico")
    print(ASSETS / "icon.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
