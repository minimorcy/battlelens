"""Calibración interactiva: dibujar sobre una captura la región del nombre del rival."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from PyQt6.QtCore import QPoint, QRect, QRectF, Qt
from PyQt6.QtGui import QColor, QGuiApplication, QImage, QKeyEvent, QMouseEvent, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..core.pokedex import Game
from ..core.profiles import Region, RegionTooSmallError
from ..i18n import N_, _


class _Selector(QWidget):
    """Muestra la captura escalada y permite dibujar un rectángulo con el ratón."""

    def __init__(self, image: np.ndarray, max_size) -> None:
        super().__init__()
        h, w = image.shape[:2]
        self._image_size = (w, h)
        qimage = QImage(image.data, w, h, image.strides[0], QImage.Format.Format_RGB888).copy()
        self._pixmap = QPixmap.fromImage(qimage)
        scale = min(max_size.width() / w, max_size.height() / h, 4.0)
        self._display = self._pixmap.scaled(
            round(w * scale), round(h * scale), transformMode=Qt.TransformationMode.FastTransformation
        )
        self.setFixedSize(self._display.size())
        self.setCursor(Qt.CursorShape.CrossCursor)
        self._start: QPoint | None = None
        self._rect: QRect | None = None

    def selection_in_image_px(self) -> tuple[int, int, int, int] | None:
        if self._rect is None:
            return None
        sx = self._image_size[0] / self.width()
        sy = self._image_size[1] / self.height()
        r = self._rect.normalized()
        return round(r.x() * sx), round(r.y() * sy), round(r.width() * sx), round(r.height() * sy)

    @property
    def image_size(self) -> tuple[int, int]:
        return self._image_size

    def _clamp(self, p: QPoint) -> QPoint:
        return QPoint(min(max(p.x(), 0), self.width() - 1), min(max(p.y(), 0), self.height() - 1))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._start = self._clamp(event.position().toPoint())
            self._rect = QRect(self._start, self._start)
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._start is not None:
            self._rect = QRect(self._start, self._clamp(event.position().toPoint())).normalized()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._start = None

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._display)
        if self._rect is not None:
            shade = QColor(0, 0, 0, 110)
            full = QRectF(self.rect())
            r = QRectF(self._rect)
            painter.fillRect(QRectF(0, 0, full.width(), r.top()), shade)
            painter.fillRect(QRectF(0, r.bottom(), full.width(), full.height() - r.bottom()), shade)
            painter.fillRect(QRectF(0, r.top(), r.left(), r.height()), shade)
            painter.fillRect(QRectF(r.right(), r.top(), full.width() - r.right(), r.height()), shade)
            painter.setPen(QPen(QColor("#ffcb05"), 2))
            painter.drawRect(r)


class CalibrationDialog(QDialog):
    """Devuelve la región elegida en `self.region` si el usuario confirma con Enter.

    Con `optional`, Esc (o «Saltar») deja la región sin calibrar. Con `recapture`, «Volver a capturar»
    cambia la imagen por una captura nueva del emulador (p. ej. tras abrir el menú de Luchar); la imagen
    sobre la que se dibujó queda en `self.image`.
    """

    def __init__(self, image: np.ndarray, title: str, target: str = N_("nombre del Pokémon rival"),
                 optional: bool = False, recapture: Callable[[], np.ndarray | None] | None = None) -> None:
        super().__init__(None, Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle(title)
        self.region: Region | None = None
        self.image = image
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self._max_size = screen.size() * 0.85

        help_text = QLabel(_(
            "Dibuja un rectángulo que cubra el <b>{target}</b>; cuanto más ajustado, mejor "
            "(no pasa nada si incluye el nivel). "
            "<b>Enter</b> confirma · <b>Esc</b> cancela.",
            target=_(target),
        ) if not optional else _(
            "Dibuja un rectángulo que cubra el <b>{target}</b>; cuanto más ajustado, mejor. "
            "Es opcional: <b>Enter</b> confirma · <b>Esc</b> lo salta (puedes calibrarlo después "
            "en Ajustes › Perfiles).",
            target=_(target),
        ))
        help_text.setTextFormat(Qt.TextFormat.RichText)
        help_text.setWordWrap(True)
        self._error = QLabel()
        self._error.setStyleSheet("color:#e5484d; font-weight:600;")
        self._selector = _Selector(image, self._max_size)

        self._layout = QVBoxLayout(self)
        self._layout.addWidget(help_text)
        self._layout.addWidget(self._selector, alignment=Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._error)
        buttons = QDialogButtonBox()
        if recapture is not None:
            self._recapture = recapture
            hint = QLabel(_("¿No está a la vista? Haz que se vea en el emulador (por ejemplo, abre el menú de "
                            "Luchar) y pulsa «Volver a capturar»."))
            hint.setWordWrap(True)
            self._layout.insertWidget(1, hint)
            again = buttons.addButton(_("Volver a capturar"), QDialogButtonBox.ButtonRole.ActionRole)
            again.setAutoDefault(False)
            again.clicked.connect(self._capture_again)
        if optional:
            skip = buttons.addButton(_("Saltar"), QDialogButtonBox.ButtonRole.RejectRole)
            skip.setAutoDefault(False)
            skip.clicked.connect(self.reject)
        if buttons.buttons():
            self._layout.addWidget(buttons)

    def _capture_again(self) -> None:
        image = self._recapture()
        if image is None:
            return
        selector = _Selector(image, self._max_size)
        self._layout.replaceWidget(self._selector, selector)
        self._selector.deleteLater()
        self._selector, self.image = selector, image
        self._error.clear()
        self.adjustSize()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._confirm()
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)

    def _confirm(self) -> None:
        selection = self._selector.selection_in_image_px()
        if selection is None:
            self._error.setText(_("Primero dibuja un rectángulo sobre el nombre."))
            return
        w, h = self._selector.image_size
        try:
            self.region = Region.from_pixels(*selection, w, h)
        except RegionTooSmallError as exc:
            self._error.setText(str(exc))
            return
        self.accept()


class ProfileDialog(QDialog):
    """Nombre y juego de un perfil nuevo, propuestos a partir del título de la ventana."""

    def __init__(self, default_name: str, games: list[Game], default_game: str | None, lang: str = "es") -> None:
        super().__init__(None, Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle(_("Nuevo perfil"))
        self.name_edit = QLineEdit(default_name)
        self.game_combo = QComboBox()
        self.game_combo.addItem(_("Sin especificar (formas originales, tabla actual)"), None)
        for game in sorted(games, key=lambda g: g.generation):
            self.game_combo.addItem(f"Gen {game.generation} · {game.name(lang)}", game.id)
        index = self.game_combo.findData(default_game)
        self.game_combo.setCurrentIndex(max(index, 0))

        form = QFormLayout()
        form.addRow(_("Nombre del perfil:"), self.name_edit)
        form.addRow(_("Juego:"), self.game_combo)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _accept(self) -> None:
        if self.name_edit.text().strip():
            self.accept()

    @property
    def result_value(self) -> tuple[str, str | None]:
        return self.name_edit.text().strip(), self.game_combo.currentData()


def ask_profile(default_name: str, games: list[Game], default_game: str | None, lang: str = "es"):
    dialog = ProfileDialog(default_name, games, default_game, lang)
    return dialog.result_value if dialog.exec() else None
