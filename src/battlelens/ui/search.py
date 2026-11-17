"""Buscador de Pokémon con atajo global (spec pokemon-search)."""

from __future__ import annotations

from PyQt6.QtCore import QRectF, QSize, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QCompleter, QDialog, QLabel, QLineEdit, QStyledItemDelegate, QVBoxLayout, QWidget

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


class SearchField(QWidget):
    """Campo con sugerencias; al resolver emite `chosen(especie, forma)` (spec pokemon-search).

    `entries`: (nombre, [(tipo traducido, id del tipo)], (especie, forma)), una por forma. Un nombre que no está
    en la lista se resuelve con el emparejador aproximado, con la forma automática del juego (forma None).
    Lo usan el diálogo del modo overlay y la columna del buscador del panel.
    """

    chosen = pyqtSignal(int, object)

    def __init__(self, entries: list[tuple[str, list[tuple[str, str]], tuple[int, str]]], matcher: NameMatcher,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._matcher = matcher
        self._model = QStandardItemModel(self)
        self.edit = QLineEdit()
        self.edit.setPlaceholderText(_("Nombre del Pokémon"))
        completer = QCompleter(self._model, self)
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
        self._resolving = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.edit)
        layout.addWidget(self.error)
        self.set_entries(entries)

    def set_entries(self, entries: list[tuple[str, list[tuple[str, str]], tuple[int, str]]]) -> None:
        """Sugerencias nuevas (otro perfil u otro idioma)."""
        self._by_name = {name.casefold(): choice for name, _types, choice in entries}
        self._model.clear()
        for name, types, _choice in entries:
            item = QStandardItem(name)
            item.setData(types, TYPES_ROLE)
            self._model.appendRow(item)

    def clear(self) -> None:
        self.edit.clear()
        self.error.hide()

    def keyPressEvent(self, event) -> None:
        # Esc: en el diálogo lo cierra (le llega a él); en el panel vacía el campo
        if event.key() == Qt.Key.Key_Escape and not isinstance(self.window(), QDialog):
            self.clear()
            return
        super().keyPressEvent(event)

    def _resolve(self, text: str | None = None) -> None:
        if self._resolving:  # el completer y Enter llegan a la vez al elegir una sugerencia
            return
        text = (text or self.edit.text()).strip()
        if text.casefold() in self._by_name:
            choice = self._by_name[text.casefold()]
        else:
            match = self._matcher.match(text) if text else None
            if match is None or not match.recognized:
                self.error.setText(_("No encuentro ese Pokémon."))
                self.error.show()
                return
            choice = (match.species_id, None)
        self.error.hide()
        self._resolving = True
        try:
            self.chosen.emit(*choice)
        finally:
            QTimer.singleShot(0, self._done)  # tras el Enter que llega detrás del clic en la sugerencia

    def _done(self) -> None:
        self._resolving = False


class SearchDialog(QDialog):
    """Diálogo del buscador (modo overlay): al confirmar deja en `choice` la (especie, forma) elegida."""

    def __init__(self, entries: list[tuple[str, list[tuple[str, str]], tuple[int, str]]], matcher: NameMatcher) -> None:
        super().__init__(None, Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle(_("Buscar Pokémon"))
        self.setWindowIcon(app_icon())
        self.setMinimumWidth(320)
        self.choice: tuple[int, str | None] | None = None
        self.field = SearchField(entries, matcher, self)
        self.edit, self.error = self.field.edit, self.field.error
        self.field.chosen.connect(self._chosen)
        QVBoxLayout(self).addWidget(self.field)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.activateWindow()  # el atajo llega con el emulador delante
        self.edit.setFocus()

    def _chosen(self, species_id: int, form) -> None:
        if self.choice is None:
            self.choice = (species_id, form)
            self.accept()
