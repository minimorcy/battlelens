"""Asistente «Nuevo perfil con un preset» (spec game-presets, add-game-presets D3).

Dibuja sobre la captura del emulador la imagen del juego localizada y los recuadros del preset, con lo
que lee BattleLens en cada uno, para que el usuario confirme que caen sobre los nombres.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from ..core.presets import Preset, preset_for, region_pixels
from ..i18n import N_, _
from ..vision.viewport import Viewport, find_viewport
from .calibrator import CalibrationDialog
from .icons import app_icon

MAX_PREVIEW = (900, 560)
ROLE_COLORS = {"rival": "#e5484d", "own": "#3ddc97", "moves": "#ffcb05"}
ROLE_LABELS = {"rival": N_("Rival"), "own": N_("Tu Pokémon"), "moves": N_("Menú de ataques")}
GAME_AREA_TARGET = N_("imagen del juego (toda la pantalla del juego, sin barras del emulador)")

ReadFn = Callable[[str, np.ndarray], str]


class PresetWizard(QDialog):
    """Al cerrarse: `action` es "save" (con `preset` y `viewport`), "manual" o None (cancelado)."""

    def __init__(self, image: np.ndarray, games: list[tuple[str, str]], proposed_game: str | None,
                 read_fn: ReadFn) -> None:
        super().__init__(None, Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle(_("Nuevo perfil con un preset"))
        self.setWindowIcon(app_icon())
        self.image = np.ascontiguousarray(image[..., :3])
        self.read_fn = read_fn
        self.action: str | None = None
        self.preset: Preset | None = None
        self.viewport: Viewport | None = None
        self._manual_viewport = False

        self.game = QComboBox()
        for game_id, label in games:
            self.game.addItem(label, game_id)
        index = self.game.findData(proposed_game) if proposed_game else -1
        self.game.setCurrentIndex(max(index, 0))
        self.game.currentIndexChanged.connect(lambda _i: self._update(reset_viewport=True))

        intro = QLabel(_("Hazlo durante un combate, con los nombres en pantalla. "
                         "¿Caen los recuadros de colores sobre los nombres?"))
        intro.setWordWrap(True)
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.readings = QLabel()
        self.readings.setObjectName("preset-readings")
        self.readings.setWordWrap(True)
        self.warning = QLabel()
        self.warning.setObjectName("preset-warning")
        self.warning.setWordWrap(True)
        self.warning.setStyleSheet("color:#e5484d;")

        self.save_button = QPushButton(_("Guardar perfil"))
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self._save)
        adjust = QPushButton(_("Ajustar la imagen del juego…"))
        adjust.clicked.connect(self._adjust)
        manual = QPushButton(_("Calibrar a mano…"))
        manual.clicked.connect(self._manual)
        cancel = QPushButton(_("Cancelar"))
        cancel.clicked.connect(self.reject)

        game_row = QHBoxLayout()
        game_row.addWidget(QLabel(_("Juego:")))
        game_row.addWidget(self.game, 1)
        buttons = QHBoxLayout()
        buttons.addWidget(manual)
        buttons.addWidget(adjust)
        buttons.addStretch(1)
        buttons.addWidget(cancel)
        buttons.addWidget(self.save_button)
        layout = QVBoxLayout(self)
        layout.addLayout(game_row)
        layout.addWidget(intro)
        layout.addWidget(self.preview)
        layout.addWidget(self.readings)
        layout.addWidget(self.warning)
        layout.addLayout(buttons)
        self._update(reset_viewport=True)

    # ---- estado ---------------------------------------------------------------

    @property
    def game_id(self) -> str | None:
        return self.game.currentData()

    def _update(self, reset_viewport: bool = False) -> None:
        self.preset = preset_for(self.game_id)
        if self.preset is not None and (reset_viewport or self.viewport is None):
            self.viewport = find_viewport(self.image, self.preset.aspect, self.preset.ds)
            self._manual_viewport = False
        reliable = self.viewport is not None and (self.viewport.reliable or self._manual_viewport)
        if self.preset is None:
            self.warning.setText(_("Este juego aún no tiene preset: calibra a mano."))
        elif not reliable:
            self.warning.setText(_("No he podido localizar la imagen del juego: pulsa «Ajustar la imagen del juego…» "
                                   "y dibuja su rectángulo."))
        else:
            self.warning.setText("")
        self.save_button.setEnabled(self.preset is not None and reliable)
        self._draw()
        self._read()

    def _crops(self) -> dict[str, np.ndarray]:
        if self.preset is None or self.viewport is None:
            return {}
        h, w = self.image.shape[:2]
        crops = {}
        for role, box in self.preset.regions.items():
            x, y, rw, rh = region_pixels(box, self.viewport)
            x0, y0 = max(0, x), max(0, y)
            x1, y1 = min(w, x + rw), min(h, y + rh)
            if x1 > x0 and y1 > y0:
                crops[role] = self.image[y0:y1, x0:x1]
        return crops

    def _read(self) -> None:
        lines = []
        for role, crop in self._crops().items():
            text = self.read_fn(role, crop) or _("(no leo nada)")
            lines.append(f"<b>{_(ROLE_LABELS[role])}:</b> {_escape(text)}")
        self.readings.setText("<br>".join(lines))

    # ---- dibujo -----------------------------------------------------------------

    def _draw(self) -> None:
        h, w = self.image.shape[:2]
        qimage = QImage(self.image.data, w, h, self.image.strides[0], QImage.Format.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(qimage)
        scale = min(MAX_PREVIEW[0] / w, MAX_PREVIEW[1] / h, 1.0)
        pixmap = pixmap.scaled(round(w * scale), round(h * scale), Qt.AspectRatioMode.IgnoreAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        painter = QPainter(pixmap)
        if self.viewport is not None:
            painter.setPen(QPen(QColor("#ffffff"), 2, Qt.PenStyle.DashLine))
            v = self.viewport
            painter.drawRect(QRect(round(v.x * scale), round(v.y * scale), round(v.width * scale), round(v.height * scale)))
        if self.preset is not None and self.viewport is not None:
            for role, box in self.preset.regions.items():
                x, y, rw, rh = region_pixels(box, self.viewport)
                rect = QRect(round(x * scale), round(y * scale), round(rw * scale), round(rh * scale))
                painter.setPen(QPen(QColor(ROLE_COLORS[role]), 3))
                painter.drawRect(rect)
                painter.drawText(rect.adjusted(4, 2, 0, 0), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                                 _(ROLE_LABELS[role]))
        painter.end()
        self.preview.setPixmap(pixmap)

    # ---- acciones -----------------------------------------------------------------

    def _adjust(self) -> None:
        dialog = CalibrationDialog(self.image, _("Ajustar la imagen del juego"), GAME_AREA_TARGET)
        if dialog.exec() and dialog.region is not None:
            h, w = self.image.shape[:2]
            x, y, rw, rh = dialog.region.to_pixels(w, h)
            self.viewport = Viewport(x, y, rw, rh)
            self._manual_viewport = True
            self._update()

    def _save(self) -> None:
        self.action = "save"
        self.accept()

    def _manual(self) -> None:
        self.action = "manual"
        self.accept()


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
