"""Genera las capturas de la guía de uso (site/assets/guide/{es,en}/) a partir de la interfaz real.

Uso:  uv run python tools/make_guide_screenshots.py

Renderiza a doble resolución, en español y en inglés: menú de la bandeja, páginas de Ajustes, asistente de
presets, calibración a mano y fichas. Los perfiles y ventanas son de ejemplo (no lee tu configuración).
La imagen del juego del asistente y de la calibración es tools/data/sword-battle.jpg: el mismo combate de
site/assets/gameplay.jpg, sin la ficha. También sirve para regenerar gameplay.jpg sin el emulador:
    uv run python tools/make_gameplay_shot.py --frame <png con la imagen y barras de emulador>
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "assets" / "guide"
GAME = "sword-shield"
BATTLE = ROOT / "tools" / "data" / "sword-battle.jpg"
# Barras del emulador alrededor de la imagen del juego (como en la ventana real)
MENU_BAR, STATUS_BAR = 30, 24


def game_frame() -> np.ndarray:
    """La imagen del combate con barras de emulador arriba y abajo, como la ventana real."""
    from PIL import Image

    game = np.array(Image.open(BATTLE).convert("RGB"))
    gh, gw = game.shape[:2]
    frame = np.zeros((gh + MENU_BAR + STATUS_BAR, gw, 3), np.uint8)
    frame[:MENU_BAR] = (240, 240, 240)
    frame[MENU_BAR : MENU_BAR + gh] = game
    frame[MENU_BAR + gh :] = (225, 225, 225)
    return frame


def save(widget, name: str, lang: str) -> None:
    from PyQt6.QtWidgets import QApplication

    for _ in range(5):
        QApplication.processEvents()
    path = OUT / lang / name
    widget.grab().save(str(path), None, 85)  # la calidad solo cuenta en .jpg (imágenes del juego)
    print(path.relative_to(ROOT))


def sync_html_sizes() -> None:
    """Actualiza width/height de las capturas en guide.html (tamaño lógico = la mitad de la imagen)."""
    import re

    from PIL import Image

    page = ROOT / "site" / "guide.html"
    html = page.read_text(encoding="utf-8")

    def fix(match: re.Match) -> str:
        width, height = Image.open(OUT / match.group(1)).size
        return f'src="assets/guide/{match.group(1)}" width="{width // 2}" height="{height // 2}"'

    html = re.sub(r'src="assets/guide/([a-z]+/[a-z-]+\.(?:png|jpg))" width="\d+" height="\d+"', fix, html)
    page.write_text(html, encoding="utf-8")


def main() -> int:
    os.environ.setdefault("QT_SCALE_FACTOR", "2")
    sys.path.insert(0, str(ROOT / "src"))
    from PyQt6.QtCore import QRect
    from PyQt6.QtWidgets import QApplication, QWidget

    app = QApplication([])
    app.setStyle("Fusion")  # igual en cualquier PC; el menú nativo de Windows depende del tema
    from battlelens.core.config import Config
    from battlelens.core.learnsets import Learnsets
    from battlelens.core.pokedex import Pokedex
    from battlelens.core.profiles import Profile, Region
    from battlelens.i18n import set_language
    from battlelens.platform.windows import WindowInfo
    from battlelens.ui.calibrator import CalibrationDialog
    from battlelens.ui.overlay import Overlay
    from battlelens.ui.preset_wizard import PresetWizard
    from battlelens.ui.settings import SettingsWindow
    from battlelens.ui.tray import Tray

    dex = Pokedex.load()
    learnsets = Learnsets.get()
    frame = game_frame()
    window = WindowInfo(1, "eden | Pokémon Sword", "eden.exe", 1)
    windows = [window, WindowInfo(2, "mGBA - Pokémon Emerald", "mGBA.exe", 2)]
    names = {"es": ("Pokémon Espada", "Pokémon Esmeralda"), "en": ("Pokémon Sword", "Pokémon Emerald")}

    for lang in ("es", "en"):
        set_language(lang)
        (OUT / lang).mkdir(parents=True, exist_ok=True)
        games = [(g.id, g.name(lang)) for g in dex.games]
        sword = Profile(names[lang][0], Region(0.72, 0.04, 0.27, 0.09), game=GAME, id="sword",
                        own_region=Region(0.0, 0.85, 0.25, 0.08), moves_region=Region(0.79, 0.55, 0.21, 0.42))
        emerald = Profile(names[lang][1], Region(0.05, 0.08, 0.45, 0.1), game="emerald", id="emerald")
        profiles = ([sword, emerald], "sword")

        # ---- bandeja ----
        tray = Tray(lambda: windows, lambda: window, lambda: profiles,
                    {"recognize": "Ctrl+Alt+P", "toggle_mode": "Ctrl+Alt+M"})
        tray.set_auto_detect(True)
        tray.set_mode("normal")
        tray.set_stream(True, "http://localhost:17320/")
        tray.menu.adjustSize()
        save(tray.menu, "tray.png", lang)

        # ---- ajustes ----
        config = Config(language=lang, interface_language=lang, stream_enabled=True)
        settings = SettingsWindow(config, lambda: windows, lambda: window, lambda: profiles, lambda: games)
        settings.set_stream(True, "http://localhost:17320/")
        settings.refresh()
        settings.show()
        for key in ("general", "card", "recognition", "hotkeys", "stream", "profiles"):
            settings.show_section(key)
            QApplication.processEvents()
            # Ventana tan alta como la página, para que se vea entera sin desplazamiento
            footer = settings.findChild(QWidget, "settings-footer")
            content = settings.pages.currentWidget().widget().sizeHint().height()
            settings.resize(880, max(600, content + footer.sizeHint().height()))
            save(settings, f"settings-{key}.png", lang)
        settings.close()

        # ---- asistente de presets ----
        readings = {"rival": "Machop" + (" · Lv. 16" if lang == "en" else " · Nv. 16"),
                    "own": "Scorbunny" + (" · Lv. 15" if lang == "en" else " · Nv. 15"), "moves": ""}
        wizard = PresetWizard(frame, [(g, n) for g, n in games if g == GAME or g == "emerald"], GAME,
                              lambda role, _crop: readings[role])
        wizard.show()
        save(wizard, "preset-wizard.jpg", lang)
        wizard.close()

        # ---- calibración a mano: recuadro ya dibujado sobre el nombre del rival ----
        dialog = CalibrationDialog(frame, "BattleLens")
        selector = dialog._selector
        sx = selector.width() / frame.shape[1]
        sy = selector.height() / frame.shape[0]
        selector._rect = QRect(round(1212 * sx), round((MENU_BAR + 34) * sy), round(360 * sx), round(46 * sy))
        dialog.show()
        save(dialog, "calibrate.jpg", lang)
        dialog.close()

        # ---- fichas ----
        def card(name: str, mode: str, rivals, own=None, own_level=None, hidden=None, form=None, own_moves=None):
            overlay = Overlay(dex, lang, mode=mode)
            overlay.form_hotkey = "Ctrl+Alt+F"
            overlay._available_height = lambda rect: 100_000  # ficha completa, sin desplazamiento
            if hidden is not None:
                overlay.hidden = {mode: frozenset(hidden)}
            views = [dex.view(sid, GAME, lang, form) for sid, _ in rivals]
            own_view = dex.view(own, GAME, lang) if own else None
            moves = [learnsets.move(m) for m in own_moves] if own_moves else None
            overlay.show_battle(views, own_view, None, [lvl for _, lvl in rivals], own_level, moves, False)
            save(overlay, name, lang)
            overlay.close()

        defaults = Config()
        card("card-default.png", "normal", [(66, 16)], 813, 15, hidden=defaults.hidden_sections("normal"))
        card("card-normal.png", "normal", [(66, 16)], 813, 15, hidden=())
        card("card-competitive.png", "competitive", [(66, 16)], 813, 15, hidden=(),
             own_moves=["ember", "quick-attack", "double-kick", "tackle"])
        card("card-double.png", "normal", [(263, 8), (759, 10)], 813, 14,
             hidden=("own_moves", "evo", "forms"))
        card("card-form.png", "normal", [(479, 40)], hidden=("matchup", "own_moves", "evo"), form="rotom-wash")
    sync_html_sizes()
    return 0


if __name__ == "__main__":
    sys.exit(main())
