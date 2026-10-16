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


ICON_FONTS = ("Segoe Fluent Icons", "Segoe MDL2 Assets")  # vienen con Windows 10/11


def glyph_icon(glyph: str, fallback: str, color: str, selected_color: str, size: int = 18) -> QIcon:
    """Icono de un glifo de la fuente de iconos de Windows (o un símbolo Unicode si no está), en dos colores."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QColor, QFont, QFontDatabase, QPainter

    family = next((f for f in ICON_FONTS if f in QFontDatabase.families()), None)
    icon = QIcon()
    for mode, tint in ((QIcon.Mode.Normal, color), (QIcon.Mode.Selected, selected_color)):
        pixmap = QPixmap(size * 2, size * 2)  # a doble resolución para pantallas HiDPI
        pixmap.setDevicePixelRatio(2)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        font = QFont(family) if family else QFont()
        font.setPixelSize(size - 3 if family else size - 2)
        painter.setFont(font)
        painter.setPen(QColor(tint))
        painter.drawText(0, 0, size, size, Qt.AlignmentFlag.AlignCenter, glyph if family else fallback)
        painter.end()
        icon.addPixmap(pixmap, mode)
    return icon


@lru_cache(maxsize=1)
def arrow_images(color: str) -> dict[str, str]:
    """Flechas de combos y campos numéricos como PNG temporales, para usarlas con `image: url(...)` en QSS."""
    import tempfile
    from pathlib import Path

    from PyQt6.QtCore import QPointF, Qt
    from PyQt6.QtGui import QColor, QPainter, QPolygonF

    folder = Path(tempfile.mkdtemp(prefix="battlelens-qss-"))
    paths = {}
    for name, points in (("down", ((2, 4), (12, 4), (7, 10))), ("up", ((2, 10), (12, 10), (7, 4)))):
        pixmap = QPixmap(28, 28)
        pixmap.setDevicePixelRatio(2)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(color))
        painter.drawPolygon(QPolygonF([QPointF(x, y) for x, y in points]))
        painter.end()
        path = folder / f"{name}.png"
        pixmap.save(str(path), "PNG")
        paths[name] = path.as_posix()
    return paths
