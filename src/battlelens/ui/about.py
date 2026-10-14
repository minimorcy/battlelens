"""Ventana «Acerca de»."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QVBoxLayout

from .. import APP_NAME, LICENSE_NAME, REPO_URL, __version__
from ..i18n import N_, _
from .icons import app_icon

# Mismos textos que DATA_ATTRIBUTION y DISCLAIMER (battlelens/__init__.py), marcados aquí para traducirlos;
# un test comprueba que siguen iguales.
ATTRIBUTION_TEXT = N_("Datos de Pokémon: PokéAPI (BSD-3-Clause)")
DISCLAIMER_TEXT = N_(
    "BattleLens es un proyecto de fans no oficial. No está afiliado ni respaldado por Nintendo, "
    "The Pokémon Company, Creatures Inc. ni GAME FREAK inc. Pokémon y los nombres de los Pokémon "
    "son marcas registradas de sus respectivos titulares."
)


class AboutDialog(QDialog):
    def __init__(self) -> None:
        super().__init__(None, Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle(_("Acerca de {app}", app=APP_NAME))
        self.setWindowIcon(app_icon())
        self.setMinimumWidth(420)

        logo = QLabel()
        logo.setPixmap(app_icon().pixmap(64, 64))
        title = QLabel(f"<b style='font-size:16px'>{APP_NAME} {__version__}</b><br>"
                       + _("Ficha instantánea del Pokémon rival en cualquier emulador."))
        title.setTextFormat(Qt.TextFormat.RichText)
        header = QHBoxLayout()
        header.addWidget(logo)
        header.addWidget(title, 1)

        license_text = _("Licencia {license}. {attribution}.", license=LICENSE_NAME, attribution=_(ATTRIBUTION_TEXT))
        body = QLabel(
            f"<p><a href='{REPO_URL}'>{REPO_URL}</a></p>"
            f"<p>{license_text}</p>"
            f"<p style='color:#777'>{_(DISCLAIMER_TEXT)}</p>"
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
