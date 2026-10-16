"""Regiones ancladas a la imagen del juego (anchor-regions-to-game)."""

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from battlelens.core.presets import preset_for, to_profile_regions
from battlelens.core.profiles import Profile, Region
from battlelens.pipeline import GameAreaTracker
from battlelens.vision.viewport import find_viewport

BATTLE = Path(__file__).resolve().parent.parent / "tools" / "data" / "sword-battle.jpg"
GAME = "sword-shield"


def _game(width: int) -> np.ndarray:
    image = Image.open(BATTLE).convert("RGB")
    return np.array(image.resize((width, round(width * 9 / 16)), Image.Resampling.BILINEAR))


def _windowed() -> np.ndarray:
    """Ventana maximizada: barra de menús clara arriba y de estado abajo."""
    game = _game(1280)
    frame = np.full((game.shape[0] + 30 + 24, game.shape[1], 3), 236, np.uint8)
    frame[30 : 30 + game.shape[0]] = game
    return frame


def _fullscreen() -> np.ndarray:
    """Pantalla completa a 1920×1200: sin barras del emulador y con bandas negras arriba y abajo."""
    game = _game(1920)
    frame = np.zeros((1200, 1920, 3), np.uint8)
    top = (1200 - game.shape[0]) // 2
    frame[top : top + game.shape[0]] = game
    return frame


def _preset_profile(frame: np.ndarray) -> Profile:
    preset = preset_for(GAME)
    viewport = find_viewport(frame, preset.aspect)
    assert viewport.reliable
    h, w = frame.shape[:2]
    regions = to_profile_regions(preset, viewport, w, h)
    area = Region.from_pixels(viewport.x, viewport.y, viewport.width, viewport.height, w, h)
    return Profile("Espada", regions["rival"], game=GAME, own_region=regions["own"], game_area=area)


def _expected(frame: np.ndarray, role: str) -> Region:
    """Dónde cae la región del preset en esta captura, medida directamente sobre ella."""
    preset = preset_for(GAME)
    h, w = frame.shape[:2]
    return to_profile_regions(preset, find_viewport(frame, preset.aspect), w, h)[role]


def _close(a: Region, b: Region, tol: float = 0.01) -> bool:
    return all(abs(x - y) <= tol for x, y in zip(vars(a).values(), vars(b).values()))


@pytest.mark.parametrize("calibrated, played", [(_windowed, _fullscreen), (_fullscreen, _windowed)])
def test_las_regiones_siguen_a_la_imagen_del_juego(calibrated, played):
    profile = _preset_profile(calibrated())
    frame = played()
    placed = GameAreaTracker().place(profile, frame)
    assert _close(placed.region, _expected(frame, "rival"))
    assert _close(placed.own_region, _expected(frame, "own"))
    # sin anclar, la región del rival caería en otro sitio
    assert not _close(profile.region, _expected(frame, "rival"))


def test_misma_ventana_no_cambia_nada():
    frame = _windowed()
    profile = _preset_profile(frame)
    assert GameAreaTracker().place(profile, frame).region == profile.region


def test_perfiles_antiguos_y_juegos_sin_proporcion_no_se_mueven():
    frame = _fullscreen()
    legacy = Profile("Antiguo", Region(0.7, 0.05, 0.25, 0.1), game=GAME)
    assert GameAreaTracker().place(legacy, frame) is legacy
    unknown = Profile("3DS", Region(0.7, 0.05, 0.25, 0.1), game="sun-moon", game_area=Region(0, 0, 1, 1))
    assert GameAreaTracker().place(unknown, frame) is unknown


def test_imagen_no_localizada_deja_las_regiones_como_estan():
    profile = _preset_profile(_windowed())
    black = np.zeros((900, 1600, 3), np.uint8)  # pantalla en negro entre escenas
    assert GameAreaTracker().place(profile, black) is profile


def test_se_busca_una_vez_por_tamano(monkeypatch):
    import battlelens.pipeline as pipeline

    calls = []
    real = pipeline.find_viewport
    monkeypatch.setattr(pipeline, "find_viewport", lambda *a: calls.append(1) or real(*a))
    tracker = GameAreaTracker()
    profile = _preset_profile(_windowed())
    for _ in range(3):
        tracker.place(profile, _fullscreen())
    assert len(calls) == 1


def test_recalibrar_con_otra_ventana_guarda_la_region_en_su_sitio():
    """Una región medida a pantalla completa se guarda donde estaría en la ventana con la que se calibró."""
    windowed, fullscreen = _windowed(), _fullscreen()
    profile = _preset_profile(windowed)
    tracker = GameAreaTracker()
    measured = _expected(fullscreen, "own")  # el usuario dibuja sobre tu Pokémon a pantalla completa
    stored = measured.remap(tracker.area(fullscreen, GAME), profile.game_area)
    assert _close(stored, profile.own_region)


def test_game_area_se_guarda_y_se_lee():
    profile = _preset_profile(_windowed())
    again = Profile.from_dict(profile.to_dict())
    assert again.game_area == profile.game_area
    assert Profile.from_dict({**profile.to_dict(), "game_area": None}).game_area is None
