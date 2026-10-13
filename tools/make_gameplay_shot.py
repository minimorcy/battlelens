"""Captura de la web «BattleLens en acción»: imagen del juego (sin la interfaz del emulador)
con la ficha real de BattleLens encima.

Uso (con el emulador abierto y en un combate):
    uv run python tools/make_gameplay_shot.py --exe eden.exe --game sword-shield

Pasos: captura la ventana (aunque esté tapada), recorta solo la imagen del juego (quita la barra de
menús, la de estado y las franjas negras), reconoce rival y tu Pokémon con el pipeline de BattleLens
y compone la ficha encima. Resultado: site/assets/gameplay.jpg (+ medidas actualizadas en index.html).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "site" / "assets" / "gameplay.jpg"
# Regiones de los nombres en fracciones de la imagen del juego (Espada/Escudo y juegos 3D parecidos)
DEFAULT_RIVAL = (0.73, 0.03, 0.24, 0.09)
DEFAULT_OWN = (0.0, 0.86, 0.26, 0.09)
OUTPUT_WIDTH = 1600
CARD_SCALE = "1.5"
CARD_MARGIN = 28


def crop_game(frame):
    """Quita barra de menús/estado del emulador (color uniforme en el centro) y franjas negras."""
    import numpy as np

    h, w = frame.shape[:2]
    xm = w // 2
    top = next(y for y in range(0, h // 4) if np.abs(frame[y, xm].astype(int) - frame[0, xm].astype(int)).sum() > 30)
    bottom = next(
        y for y in range(h - 1, 3 * h // 4, -1) if np.abs(frame[y, xm].astype(int) - frame[h - 1, xm].astype(int)).sum() > 30
    )
    body = frame[top : bottom + 1]
    lum = body.mean(axis=2)
    cols = np.where((lum > 12).mean(axis=0) > 0.5)[0]
    return body[:, cols.min() : cols.max() + 1]


def region(image, frac):
    h, w = image.shape[:2]
    x, y, rw, rh = frac
    return image[int(y * h) : int((y + rh) * h), int(x * w) : int((x + rw) * w)]


def render_card(rival: int, own: int | None, own_level: int | None, game: str, mode: str, out: Path) -> None:
    """Renderiza la ficha en un proceso aparte con escala fija (QT_SCALE_FACTOR)."""
    code = f"""
import sys
sys.path.insert(0, {str(ROOT / 'src')!r})
from PyQt6.QtWidgets import QApplication
app = QApplication([])
from battlelens.core.pokedex import Pokedex
from battlelens.ui.overlay import Overlay
dex = Pokedex.load()
o = Overlay(dex, "es", mode={mode!r})
o._available_height = lambda rect: 100_000
own = dex.view({own!r}, {game!r}, "es") if {own is not None!r} else None
o.show_battle([dex.view({rival}, {game!r}, "es")], own, None, [None], {own_level!r})
for _ in range(5):
    app.processEvents()
o.grab().save({str(out)!r})
"""
    env = {**os.environ, "QT_SCALE_FACTOR": CARD_SCALE}
    subprocess.run([sys.executable, "-c", code], env=env, check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--exe", default="eden.exe", help="ejecutable del emulador")
    parser.add_argument("--game", default="sword-shield", help="juego (id de grupo de versiones)")
    parser.add_argument("--mode", default="normal", choices=("normal", "competitive"))
    parser.add_argument("--frame", type=Path, help="usar una captura guardada en lugar de capturar la ventana")
    args = parser.parse_args(argv)

    sys.path.insert(0, str(ROOT / "src"))
    import numpy as np
    from PIL import Image

    from battlelens.core.matcher import NameMatcher
    from battlelens.core.pokedex import Pokedex
    from battlelens.pipeline import read_crop
    from battlelens.platform.ocr import recognize

    if args.frame:
        frame = np.array(Image.open(args.frame).convert("RGB"))
    else:
        from battlelens.platform.capture import capture_client
        from battlelens.platform.windows import list_windows

        windows = [w for w in list_windows() if w.exe.lower() == args.exe.lower()]
        if not windows:
            print(f"No hay ninguna ventana de {args.exe}", file=sys.stderr)
            return 1
        frame = capture_client(windows[0].hwnd)

    game = crop_game(frame)
    matcher = NameMatcher(Pokedex.load())
    rival = read_crop(region(game, DEFAULT_RIVAL), recognize, matcher, ("es", "en"))
    own = read_crop(region(game, DEFAULT_OWN), recognize, matcher, ("es", "en"))
    if rival.match.species_id is None:
        print(f"No se reconoce al rival (OCR: {rival.match.raw_text!r}); ¿estás en un combate?", file=sys.stderr)
        return 1
    print(f"Rival: {rival.match.matched_name} ({rival.match.score:.0f}) · Tuyo: {own.match.matched_name} nivel {own.level}")

    with tempfile.TemporaryDirectory() as tmp:
        card_path = Path(tmp) / "card.png"
        render_card(rival.match.species_id, own.match.species_id, own.level, args.game, args.mode, card_path)
        card = Image.open(card_path).convert("RGBA")

    scene = Image.fromarray(game).convert("RGBA")
    scene.alpha_composite(card, (CARD_MARGIN, CARD_MARGIN))  # esquina superior izquierda, como al arrastrarla
    scene = scene.convert("RGB")
    if scene.width > OUTPUT_WIDTH:
        scene = scene.resize((OUTPUT_WIDTH, round(scene.height * OUTPUT_WIDTH / scene.width)), Image.Resampling.LANCZOS)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    scene.save(OUTPUT, quality=86, optimize=True, progressive=True)
    print(f"{OUTPUT} ({scene.width}x{scene.height}, {OUTPUT.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
