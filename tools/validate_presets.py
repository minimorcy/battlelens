"""Comprueba los presets con capturas de referencia locales (add-game-presets D5).

Uso:  uv run python tools/validate_presets.py capturas-presets [--save-crops carpeta]

El juego sale del nombre del archivo (`<nn>-<juego>__<tipo>__<n>.<ext>`). Para cada imagen se localiza
la imagen del juego, se aplican las regiones del preset y se leen con el pipeline de BattleLens.
Las capturas no están en el repositorio (son de terceros): esto no es un test automático.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from battlelens.core.matcher import NameMatcher
from battlelens.core.pokedex import Pokedex
from battlelens.core.presets import preset_for, region_pixels
from battlelens.pipeline import read_crop
from battlelens.platform.ocr import recognize
from battlelens.vision.viewport import find_viewport

# Nombre de archivo → juego (grupo de versiones)
ALIASES = {
    "esmeralda": "emerald", "rojofuego-verdehoja": "firered-leafgreen", "rubi-zafiro": "ruby-sapphire",
    "platino": "platinum", "heartgold-soulsilver": "heartgold-soulsilver", "negro-blanco": "black-white",
    "espada-escudo": "sword-shield", "rojo-azul": "red-blue", "amarillo": "yellow", "oro-plata": "gold-silver",
    "cristal": "crystal",
}


def game_of(path: Path) -> str | None:
    stem = path.stem.split("__")[0]
    return ALIASES.get(stem.split("-", 1)[1] if "-" in stem else stem)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--save-crops", type=Path)
    parser.add_argument("--languages", default="es,en")
    parser.add_argument("--upscale", type=int, default=1,
                        help="amplía las capturas pequeñas (<500 px) como lo haría el emulador (vecino más próximo)")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")  # la consola de Windows usa cp1252
    matcher = NameMatcher(Pokedex.load())
    languages = tuple(args.languages.split(","))
    for path in sorted(p for p in args.folder.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg")):
        game = game_of(path)
        preset = preset_for(game)
        if preset is None:
            continue
        image = Image.open(path).convert("RGB")
        if args.upscale > 1 and image.width < 500:
            image = image.resize((image.width * args.upscale, image.height * args.upscale), Image.Resampling.NEAREST)
        frame = np.array(image)
        viewport = find_viewport(frame, preset.aspect, preset.ds)
        print(f"== {path.name}  [{preset.id}] viewport {viewport.x},{viewport.y} {viewport.width}x{viewport.height}"
              f"{'' if viewport.reliable else '  (NO FIABLE)'}")
        for role, box in preset.regions.items():
            if role == "moves" and "menu" not in path.name:
                continue
            x, y, w, h = region_pixels(box, viewport)
            crop = frame[max(0, y):y + h, max(0, x):x + w]
            if crop.size == 0:
                print(f"   {role:6} (fuera de la imagen)")
                continue
            reading = read_crop(crop, recognize, matcher, languages)
            match = reading.match
            print(f"   {role:6} {match.raw_text!r:30} → {match.matched_name or '-':12} {match.score:5.1f}"
                  f"  nivel {reading.level or '-'}")
            if args.save_crops:
                args.save_crops.mkdir(parents=True, exist_ok=True)
                Image.fromarray(crop).save(args.save_crops / f"{path.stem}__{role}.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
