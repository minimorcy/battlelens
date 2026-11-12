"""Buscador de Pokémon con atajo global (spec pokemon-search)."""

from __future__ import annotations

from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QCompleter, QDialog, QLabel, QLineEdit, QStyledItemDelegate, QVBoxLayout

from ..core.matcher import NameMatcher
from ..i18n import _
from . import theme
from .icons import app_icon

TYPES_ROLE = Qt.ItemDataRole.UserRole + 1  # [(nombre del tipo, id del tipo)]
PILL_GAP = 4


class _TypesDelegate(QStyledItemDelegate):
    """Fila de sugerencia: el nombre a la izquierda y los tipos en píldoras sólidas, como en la ficha."""

    def sizeHint(self, option, index) -> QSize:
        size = super().sizeHint(option, index)
        return QSize(size.width() + 140, max(size.height(), 26))

    def paint(self, painter: QPainter, option, index) -> None:
        super().paint(painter, option, index)
        font = QFont(option.font)
        font.setPixelSize(11)
        font.setWeight(QFont.Weight.DemiBold)
        metrics = QFontMetrics(font)
        right = option.rect.right() - 8
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(font)
        for label, type_id in reversed(index.data(TYPES_ROLE) or []):
            width = metrics.horizontalAdvance(label) + 16
            rect = QRectF(right - width, option.rect.center().y() - 8, width, 16)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(theme.TYPE_COLORS.get(type_id, "#555")))
            painter.drawRoundedRect(rect, 8, 8)
            painter.setPen(QColor("#1b1b1b" if type_id in theme.DARK_TEXT_TYPES else "#ffffff"))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)
            right -= width + PILL_GAP
        painter.restore()


class SearchDialog(QDialog):
    """Campo con sugerencias; al confirmar deja en `choice` la (especie, forma) elegida.

    `entries`: (nombre, [(tipo traducido, id del tipo)], (especie, forma)), una por forma. Un nombre que no está
    en la lista se resuelve con el emparejador aproximado, con la forma automática del juego (forma None).
    """

    def __init__(self, entries: list[tuple[str, list[tuple[str, str]], tuple[int, str]]], matcher: NameMatcher) -> None:
        super().__init__(None, Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle(_("Buscar Pokémon"))
        self.setWindowIcon(app_icon())
        self.setMinimumWidth(320)
        self._matcher = matcher
        self.choice: tuple[int, str | None] | None = None
        self._by_name = {name.casefold(): choice for name, _types, choice in entries}

        model = QStandardItemModel(self)
        for name, types, _choice in entries:
            item = QStandardItem(name)
            item.setData(types, TYPES_ROLE)
            model.appendRow(item)
        self.edit = QLineEdit()
        self.edit.setPlaceholderText(_("Nombre del Pokémon"))
        completer = QCompleter(model, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._delegate = _TypesDelegate(self)  # referencia propia: si no, Python lo recoge y se pierde el pintado
        completer.popup().setItemDelegate(self._delegate)
        completer.activated.connect(self._resolve)
        self.edit.setCompleter(completer)
        self.edit.returnPressed.connect(self._resolve)
        self.error = QLabel()
        self.error.setObjectName("field-error")
        self.error.hide()

        layout = QVBoxLayout(self)
        layout.addWidget(self.edit)
        layout.addWidget(self.error)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.activateWindow()  # el atajo llega con el emulador delante
        self.edit.setFocus()

    def _resolve(self, text: str | None = None) -> None:
        if self.choice is not None:  # el completer y Enter llegan a la vez al elegir una sugerencia
            return
        text = (text or self.edit.text()).strip()
        if text.casefold() in self._by_name:
            self.choice = self._by_name[text.casefold()]
            self.accept()
            return
        match = self._matcher.match(text) if text else None
        if match is None or not match.recognized:
            self.error.setText(_("No encuentro ese Pokémon."))
            self.error.show()
            return
        self.choice = (match.species_id, None)
        self.accept()
