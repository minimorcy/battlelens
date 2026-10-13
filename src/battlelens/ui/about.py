"""Ventana «Acerca de»."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QVBoxLayout

from .. import APP_NAME, DATA_ATTRIBUTION, DISCLAIMER, LICENSE_NAME, REPO_URL, __version__
from .icons import app_icon


class AboutDialog(QDialog):
    def __init__(self) -> None:
        super().__init__(None, Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle(f"Acerca de {APP_NAME}")
        self.setWindowIcon(app_icon())
        self.setMinimumWidth(420)

        logo = QLabel()
        logo.setPixmap(app_icon().pixmap(64, 64))
        title = QLabel(f"<b style='font-size:16px'>{APP_NAME} {__version__}</b><br>"
                       "Ficha instantánea del Pokémon rival en cualquier emulador.")
        title.setTextFormat(Qt.TextFormat.RichText)
        header = QHBoxLayout()
        header.addWidget(logo)
        header.addWidget(title, 1)

        body = QLabel(
            f"<p><a href='{REPO_URL}'>{REPO_URL}</a></p>"
            f"<p>Licencia {LICENSE_NAME}. {DATA_ATTRIBUTION}.</p>"
            f"<p style='color:#777'>{DISCLAIMER}</p>"
        )
        body.setTextFormat(Qt.TextFormat.RichText)
        body.setOpenExternalLinks(True)
        body.setWordWrap(True)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(header)
        layout.addWidget(body)
        layout.addWidget(buttons)

    def text(self) -> str:
        return " ".join(label.text() for label in self.findChildren(QLabel))
