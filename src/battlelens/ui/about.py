"""Sección «Acerca de» de Ajustes (spec app-settings)."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .. import APP_NAME, LICENSE_NAME, REPO_URL, __version__
from ..i18n import N_, _
from .icons import app_icon
from .theme import ACCENT

# Mismos textos que DATA_ATTRIBUTION y DISCLAIMER (battlelens/__init__.py), marcados aquí para traducirlos;
# un test comprueba que siguen iguales.
ATTRIBUTION_TEXT = N_("Datos de Pokémon: PokéAPI (BSD-3-Clause)")
DISCLAIMER_TEXT = N_(
    "BattleLens es un proyecto de fans no oficial. No está afiliado ni respaldado por Nintendo, "
    "The Pokémon Company, Creatures Inc. ni GAME FREAK inc. Pokémon y los nombres de los Pokémon "
    "son marcas registradas de sus respectivos titulares."
)


class AboutPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        logo = QLabel()
        logo.setPixmap(app_icon().pixmap(72, 72))
        title = QLabel(APP_NAME)
        title.setObjectName("about-title")
        version = QLabel(_("Versión {version}", version=__version__))
        version.setObjectName("row-hint")
        tagline = QLabel(_("Ficha instantánea del Pokémon rival en cualquier emulador."))
        tagline.setWordWrap(True)
        names = QVBoxLayout()
        names.setSpacing(2)
        names.addWidget(title)
        names.addWidget(version)
        names.addWidget(tagline)
        header = QHBoxLayout()
        header.setSpacing(16)
        header.addWidget(logo, 0, Qt.AlignmentFlag.AlignTop)
        header.addLayout(names, 1)

        link = QLabel(f"<a href='{REPO_URL}' style='color:{ACCENT}'>{REPO_URL}</a>")
        link.setTextFormat(Qt.TextFormat.RichText)
        link.setOpenExternalLinks(True)
        license_text = QLabel(_("Licencia {license}. {attribution}.", license=LICENSE_NAME,
                                attribution=_(ATTRIBUTION_TEXT)))
        license_text.setWordWrap(True)
        disclaimer = QLabel(_(DISCLAIMER_TEXT))
        disclaimer.setObjectName("row-hint")
        disclaimer.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addLayout(header)
        layout.addWidget(link)
        layout.addWidget(license_text)
        layout.addWidget(disclaimer)

    def text(self) -> str:
        return " ".join(label.text() for label in self.findChildren(QLabel))
