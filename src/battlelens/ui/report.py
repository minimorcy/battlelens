"""Diálogo «Informar de un problema» (spec problem-report)."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QLabel, QPlainTextEdit, QVBoxLayout

from ..i18n import _
from .icons import app_icon


class ReportDialog(QDialog):
    def __init__(self, has_window: bool) -> None:
        super().__init__(None, Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle(_("Informar de un problema"))
        self.setWindowIcon(app_icon())
        self.setMinimumWidth(460)

        intro = QLabel(_(
            "Se creará un ZIP con tu configuración, tus perfiles, el registro de la app y, si lo marcas, una captura "
            "del emulador con lo que lee BattleLens en cada región. No se envía nada: tú decides si lo adjuntas. "
            "En los textos se ocultan tu carpeta de usuario y tu nombre de usuario; la captura y el título de la "
            "ventana del emulador sí se incluyen."
        ))
        intro.setWordWrap(True)

        self.description = QPlainTextEdit()
        self.description.setPlaceholderText(_("¿Qué ha pasado? (opcional) p. ej. «No reconoce a Pidgey en Esmeralda»"))
        self.description.setMinimumHeight(90)

        self.include_capture = QCheckBox(_("Incluir una captura del emulador"))
        self.include_capture.setChecked(has_window)
        self.include_capture.setEnabled(has_window)
        if not has_window:
            self.include_capture.setToolTip(_("Selecciona antes la ventana del emulador en la bandeja."))
        self.open_form = QCheckBox(_("Abrir el formulario de GitHub al terminar"))
        self.open_form.setChecked(True)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(_("Crear informe"))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(intro)
        layout.addWidget(self.description)
        layout.addWidget(self.include_capture)
        layout.addWidget(self.open_form)
        layout.addWidget(buttons)

    def values(self) -> tuple[str, bool, bool]:
        """(descripción, incluir captura, abrir el formulario)."""
        return (self.description.toPlainText().strip(), self.include_capture.isChecked(),
                self.open_form.isChecked())
