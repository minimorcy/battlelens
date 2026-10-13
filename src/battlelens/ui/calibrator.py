"""Calibración interactiva: dibujar sobre una captura la región del nombre del rival."""

from __future__ import annotations

import numpy as np
from PyQt6.QtCore import QPoint, QRect, QRectF, Qt
from PyQt6.QtGui import QColor, QGuiApplication, QImage, QKeyEvent, QMouseEvent, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QDialog, QInputDialog, QLabel, QVBoxLayout, QWidget

from ..core.profiles import Region, RegionTooSmallError


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
    """Devuelve la región elegida en `self.region` si el usuario confirma con Enter."""

    def __init__(self, image: np.ndarray, title: str) -> None:
        super().__init__(None, Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle(title)
        self.region: Region | None = None
        screen = QGuiApplication.primaryScreen().availableGeometry()
        max_size = screen.size() * 0.85

        help_text = QLabel(
            "Dibuja un rectángulo que cubra el <b>nombre del Pokémon rival</b>; cuanto más ajustado, mejor "
            "(no pasa nada si incluye el nivel). "
            "<b>Enter</b> confirma · <b>Esc</b> cancela."
        )
        help_text.setTextFormat(Qt.TextFormat.RichText)
        self._error = QLabel()
        self._error.setStyleSheet("color:#e5484d; font-weight:600;")
        self._selector = _Selector(image, max_size)

        layout = QVBoxLayout(self)
        layout.addWidget(help_text)
        layout.addWidget(self._selector, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._error)

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
            self._error.setText("Primero dibuja un rectángulo sobre el nombre.")
            return
        w, h = self._selector.image_size
        try:
            self.region = Region.from_pixels(*selection, w, h)
        except RegionTooSmallError as exc:
            self._error.setText(str(exc))
            return
        self.accept()


def ask_profile_name(default: str) -> str | None:
    name, ok = QInputDialog.getText(None, "Nuevo perfil", "Nombre del perfil (p. ej. el juego):", text=default)
    name = name.strip()
    return name if ok and name else None
