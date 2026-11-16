"""Sprites de los Pokémon descargados bajo demanda (add-pokemon-sprites D2).

Tienen copyright y no van en el instalador: el de cada Pokémon se baja del repositorio público de PokéAPI
la primera vez que aparece, se recorta a su contorno visible y se guarda en la carpeta de datos.
"""

from __future__ import annotations

import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QGuiApplication, QPixmap

from .remote_images import Download, _download, fetch_png

log = logging.getLogger(__name__)

SPRITE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{id}.png"
SPRITES_DIR = "sprites"
MAX_SPRITE_BYTES = 256 * 1024
MAX_UPSCALE = 2  # el pixel art se amplía como mucho ×2 para que no se vea gigante


def crop_to_content(path: Path) -> None:
    """Quita el margen transparente del PNG (los sprites vienen abajo a la izquierda en un lienzo de 96×96)."""
    with Image.open(path) as image:
        image = image.convert("RGBA")
        box = image.getchannel("A").getbbox()
        if box is None:
            raise ValueError(f"{path}: sprite vacío")
        cropped = image.crop(box)
    tmp = path.with_name(path.name + ".crop")
    cropped.save(tmp, "PNG")
    os.replace(tmp, path)


class Sprites(QObject):
    """Caché de sprites por número de Pokémon de PokéAPI (`SpeciesView.sprite_id`)."""

    arrived = pyqtSignal(int)  # sprite_id recién guardado (se emite desde otro hilo: llega en cola)

    def __init__(self, directory: Path, download: Download = _download) -> None:
        super().__init__()
        self.directory = directory
        self._download = download
        self._failed: set[int] = set()  # no se reintentan en la sesión
        self._pending: set[int] = set()
        self._lock = threading.Lock()
        self._pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="battlelens-sprites")
        self._cache: dict[tuple[int, int], QPixmap] = {}

    def path(self, sprite_id: int) -> Path:
        return self.directory / f"{int(sprite_id)}.png"

    def has(self, sprite_id: int) -> bool:
        return self.path(sprite_id).is_file()

    def request(self, sprite_id: int) -> bool:
        """True si el sprite está o va a llegar (descarga lanzada o en curso); False si falló en la sesión."""
        sprite_id = int(sprite_id)
        if self.has(sprite_id):
            return True
        with self._lock:
            if sprite_id in self._failed:
                return False
            if sprite_id not in self._pending:
                self._pending.add(sprite_id)
                self._pool.submit(self._fetch, sprite_id)
        return True

    def _fetch(self, sprite_id: int) -> None:
        dest = self.path(sprite_id)
        raw = dest.with_name(dest.name + ".download")
        try:
            fetch_png(SPRITE_URL.format(id=sprite_id), raw, MAX_SPRITE_BYTES, self._download)
            crop_to_content(raw)
            os.replace(raw, dest)
        except Exception as exc:  # red, HTTP, tamaño o PNG no válido: el Pokémon queda sin imagen
            log.debug("Sprite %s no descargado: %s", sprite_id, exc)
            raw.unlink(missing_ok=True)
            with self._lock:
                self._failed.add(sprite_id)
                self._pending.discard(sprite_id)
            return
        with self._lock:
            self._pending.discard(sprite_id)
        self.arrived.emit(sprite_id)

    def pixmap(self, sprite_id: int, box: int) -> QPixmap | None:
        """Sprite escalado sin suavizado para caber en `box` px lógicos (como mucho ×2); None si no está."""
        key = (int(sprite_id), box)
        if key not in self._cache:
            original = QPixmap(str(self.path(sprite_id)))
            if original.isNull():
                return None
            factor = min(MAX_UPSCALE, box / max(original.width(), original.height()))
            if factor >= 1:
                factor = int(factor)  # factor entero: píxeles nítidos
            ratio = QGuiApplication.instance().devicePixelRatio() if QGuiApplication.instance() else 1.0
            scaled = original.scaled(round(original.width() * factor * ratio), round(original.height() * factor * ratio),
                                     Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
            scaled.setDevicePixelRatio(ratio)
            self._cache[key] = scaled
        return self._cache[key]
