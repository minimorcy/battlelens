"""Tabla de naturalezas flotante: qué estadística sube (fila) y cuál baja (columna). Reutiliza la ventana de tipos."""

from __future__ import annotations

from PyQt6.QtCore import QPoint, QRect, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen

from ..i18n import _, get_language
from . import theme
from .type_chart import CLOSE, PAD, TITLE_H, TypeChartWindow

STATS = ("attack", "defense", "special_attack", "special_defense", "speed")
# NATURES[fila +][columna −] = (es, en); la diagonal son las neutras
NATURES = (
    (("Fuerte", "Hardy"), ("Huraña", "Lonely"), ("Firme", "Adamant"), ("Pícara", "Naughty"), ("Audaz", "Brave")),
    (("Osada", "Bold"), ("Dócil", "Docile"), ("Agitada", "Impish"), ("Floja", "Lax"), ("Plácida", "Relaxed")),
    (("Modesta", "Modest"), ("Afable", "Mild"), ("Tímida", "Bashful"), ("Alocada", "Rash"), ("Mansa", "Quiet")),
    (("Serena", "Calm"), ("Amable", "Gentle"), ("Cauta", "Careful"), ("Rara", "Quirky"), ("Grosera", "Sassy")),
    (("Miedosa", "Timid"), ("Activa", "Hasty"), ("Alegre", "Jolly"), ("Ingenua", "Naive"), ("Seria", "Serious")),
)
HEAD_W = 74
HEAD_H = 24
CELL_W = 68
CELL_H = 26


def nature(raised: int, lowered: int) -> str:
    return NATURES[raised][lowered][get_language() == "en"]


class NatureChartWindow(TypeChartWindow):
    """Misma ventana que la tabla de tipos (mover, reescalar, ✕), con otro contenido."""

    def __init__(self) -> None:
        super().__init__()
        n = len(STATS)
        self._base = QRect(0, 0, 2 * PAD + HEAD_W + n * CELL_W, PAD + TITLE_H + HEAD_H + n * CELL_H + PAD)
        self.set_scale(self.scale)

    def title(self) -> str:
        """Las naturalezas llegan en Gen 3: en Rojo/Azul/Oro/Plata se avisa (generation 0 = sin juego)."""
        if 0 < self.generation < 3:
            return _("Naturalezas (desde Gen 3)")
        return _("Naturalezas")

    def _type_at(self, pos: QPoint) -> str | None:
        return None

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.scale(self.scale, self.scale)
        p.setPen(QPen(QColor(theme.PANEL_BORDER), 1))
        p.setBrush(QColor(theme.PANEL_SOLID))
        p.drawRoundedRect(QRectF(self._base).adjusted(0.5, 0.5, -0.5, -0.5), 12, 12)

        font = QFont(self.font())
        font.setPixelSize(14)
        font.setWeight(QFont.Weight.Bold)
        p.setFont(font)
        p.setPen(QColor(theme.TEXT))
        p.drawText(QRect(PAD, PAD, self._base.width() - 2 * PAD - CLOSE, TITLE_H - 6),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.title())
        p.setPen(QColor(theme.TEXT_MUTED))
        if self.isWindow():  # dentro del panel no se cierra ni se reescala a mano
            p.drawText(self._close_rect(), Qt.AlignmentFlag.AlignCenter, "✕")

        font.setPixelSize(10)
        font.setWeight(QFont.Weight.DemiBold)
        p.setFont(font)
        x0, y0 = PAD + HEAD_W, PAD + TITLE_H + HEAD_H
        p.drawText(QRect(PAD, y0 - HEAD_H, HEAD_W - 4, HEAD_H),
                   Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, _("Baja →") + "\n" + _("Sube ↓"))
        for i, stat in enumerate(STATS):
            label = _(theme.STAT_LABELS[stat])
            p.setPen(QColor(theme.BAD))
            p.drawText(QRect(x0 + i * CELL_W, y0 - HEAD_H, CELL_W, HEAD_H), Qt.AlignmentFlag.AlignCenter, "−" + label)
            p.setPen(QColor(theme.GOOD))
            p.drawText(QRect(PAD, y0 + i * CELL_H, HEAD_W - 6, CELL_H),
                       Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "+" + label)
        for row in range(len(STATS)):
            for col in range(len(STATS)):
                rect = QRectF(x0 + col * CELL_W + 1, y0 + row * CELL_H + 1, CELL_W - 2, CELL_H - 2)
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QColor(255, 255, 255, 8 if row == col else 22))
                p.drawRoundedRect(rect, 3, 3)
                p.setPen(QColor(theme.TEXT_MUTED if row == col else theme.TEXT))
                p.drawText(rect, Qt.AlignmentFlag.AlignCenter, nature(row, col))
        grip = self._grip_rect()
        p.setPen(QPen(QColor(theme.TEXT_MUTED), 1.2))
        for offset in (4, 8, 12) if self.isWindow() else ():
            p.drawLine(grip.right() - offset, grip.bottom(), grip.right(), grip.bottom() - offset)
        p.end()
