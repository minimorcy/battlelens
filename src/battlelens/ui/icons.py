"""Icono de la aplicación (diseño original, ver packaging/make_icon.py)."""

from __future__ import annotations

from functools import lru_cache
from importlib import resources

from PyQt6.QtGui import QIcon, QPixmap


@lru_cache(maxsize=1)
def app_icon() -> QIcon:
    data = (resources.files("battlelens") / "assets" / "icon.png").read_bytes()
    pixmap = QPixmap()
    pixmap.loadFromData(data, "PNG")
    return QIcon(pixmap)
