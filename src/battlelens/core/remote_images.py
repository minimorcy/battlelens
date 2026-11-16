"""Imágenes descargadas a una caché local: iconos de tipo (add-type-icons D2).

Las imágenes tienen copyright y no van en el instalador: se bajan del repositorio público de PokéAPI
la primera vez que el usuario las pide. `fetch_png` es la descarga validada que reutilizarán los sprites.
"""

from __future__ import annotations

import logging
import os
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QGuiApplication, QImage, QPixmap

from .. import __version__

log = logging.getLogger(__name__)

TIMEOUT_SECONDS = 5
MAX_ICON_BYTES = 64 * 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
TYPE_ICON_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/types/generation-viii/sword-shield/small/{id}.png"
)
TYPE_ICONS_DIR = "type-icons"

Download = Callable[[str, int], bytes]


def _download(url: str, max_bytes: int) -> bytes:
    """Hasta `max_bytes + 1` bytes de `url`: uno de más basta para saber que se pasa del límite."""
    request = urllib.request.Request(url, headers={"User-Agent": f"BattleLens/{__version__}"})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return response.read(max_bytes + 1)


def fetch_png(url: str, dest: Path, max_bytes: int, download: Download = _download) -> None:
    """Descarga un PNG válido en `dest` con escritura atómica. Lanza excepción en cualquier fallo."""
    data = download(url, max_bytes)
    if len(data) > max_bytes:
        raise ValueError(f"{url}: más de {max_bytes} bytes")
    if not data.startswith(PNG_SIGNATURE) or QImage.fromData(data, "PNG").isNull():
        raise ValueError(f"{url}: no es un PNG válido")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, dest)


class TypeIcons(QObject):
    """Caché de los iconos de tipo: se usan solo si están todos (spec type-icons)."""

    finished = pyqtSignal()  # terminó una descarga en segundo plano (se emite desde otro hilo: llega en cola)

    def __init__(self, directory: Path, numbers: dict[str, int], download: Download = _download) -> None:
        super().__init__()
        self.directory = directory
        self.numbers = dict(numbers)  # tipo -> número de PokéAPI
        self._download = download
        self._failed: set[int] = set()  # no se reintentan en la sesión
        self._running = False
        self._lock = threading.Lock()
        self._cache: dict[tuple[str, int], QPixmap] = {}

    def path(self, number: int) -> Path:
        return self.directory / f"{number}.png"

    def complete(self) -> bool:
        return all(self.path(n).is_file() for n in self.numbers.values())

    def ensure(self) -> bool:
        """Lanza en segundo plano la descarga de los que falten; False si no hay nada que hacer."""
        with self._lock:
            missing = [n for n in self.numbers.values() if n not in self._failed and not self.path(n).is_file()]
            if self._running or not missing:
                return False
            self._running = True
        threading.Thread(target=self._fetch_all, args=(missing,), name="battlelens-type-icons", daemon=True).start()
        return True

    def _fetch_one(self, number: int) -> None:
        try:
            fetch_png(TYPE_ICON_URL.format(id=number), self.path(number), MAX_ICON_BYTES, self._download)
        except Exception as exc:  # red, HTTP, tamaño o PNG no válido: el icono queda como no disponible
            log.debug("Icono de tipo %s no descargado: %s", number, exc)
            with self._lock:
                self._failed.add(number)

    def _fetch_all(self, missing: list[int]) -> None:
        try:
            with ThreadPoolExecutor(max_workers=2) as pool:
                list(pool.map(self._fetch_one, missing))
        finally:
            with self._lock:
                self._running = False
            self.finished.emit()

    def pixmap(self, type_id: str, size: int | None = None) -> QPixmap | None:
        """Icono escalado con suavizado a `size` px lógicos (o el original); None si no está."""
        number = self.numbers.get(type_id)
        if number is None:
            return None
        key = (type_id, size or 0)
        if key not in self._cache:
            original = QPixmap(str(self.path(number)))
            if original.isNull():
                return None
            if size:
                ratio = QGuiApplication.instance().devicePixelRatio() if QGuiApplication.instance() else 1.0
                side = round(size * ratio)
                original = original.scaled(side, side, Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation)
                original.setDevicePixelRatio(ratio)
            self._cache[key] = original
        return self._cache[key]
