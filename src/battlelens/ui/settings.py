"""Ventana «Ajustes» (spec app-settings)."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..core.config import LANGUAGES, MODES, Config
from ..platform.hotkeys import HotkeyParseError, parse_hotkey
from .icons import app_icon

LANGUAGE_LABELS = {"es": "Español", "en": "English", "fr": "Français", "de": "Deutsch", "it": "Italiano"}
HOTKEY_FIELDS = (
    ("hotkey_recognize", "Reconocer"),
    ("hotkey_calibrate", "Calibrar"),
    ("hotkey_hide", "Ocultar ficha"),
    ("hotkey_toggle_mode", "Cambiar de modo"),
)
MODE_LABELS = {"normal": "Normal (aventura y captura)", "competitive": "Competitivo (combate)"}


def _spin(minimum: float, maximum: float, value: float, step: float = 1, decimals: int = 0, suffix: str = ""):
    box = QDoubleSpinBox()
    box.setRange(minimum, maximum)
    box.setDecimals(decimals)
    box.setSingleStep(step)
    box.setValue(value)
    if suffix:
        box.setSuffix(suffix)
    return box


class SettingsDialog(QDialog):
    def __init__(self, config: Config) -> None:
        super().__init__(None, Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("Ajustes de BattleLens")
        self.setWindowIcon(app_icon())
        self.setMinimumWidth(440)
        self.result_config: Config | None = None

        # Atajos
        self.hotkey_edits: dict[str, QLineEdit] = {}
        self.hotkey_errors: dict[str, QLabel] = {}
        hotkeys = QFormLayout()
        for field, label in HOTKEY_FIELDS:
            edit = QLineEdit(getattr(config, field))
            edit.setPlaceholderText("p. ej. Ctrl+Alt+P")
            error = QLabel()
            error.setStyleSheet("color:#e5484d;")
            error.setWordWrap(True)
            error.hide()
            column = QVBoxLayout()
            column.setSpacing(2)
            column.addWidget(edit)
            column.addWidget(error)
            holder = QWidget()
            holder.setLayout(column)
            column.setContentsMargins(0, 0, 0, 0)
            hotkeys.addRow(f"{label}:", holder)
            self.hotkey_edits[field] = edit
            self.hotkey_errors[field] = error

        # Ficha y reconocimiento
        self.language = QComboBox()
        for code in LANGUAGES:
            self.language.addItem(LANGUAGE_LABELS[code], code)
        self.language.setCurrentIndex(max(self.language.findData(config.language), 0))
        self.mode = QComboBox()
        for code in MODES:
            self.mode.addItem(MODE_LABELS[code], code)
        self.mode.setCurrentIndex(max(self.mode.findData(config.overlay_mode), 0))
        self.threshold = _spin(0, 100, config.threshold, 1, 0)
        self.auto_hide = _spin(0, 600, config.auto_hide_seconds, 1, 0, " s")
        self.debug = QCheckBox("Guardar recortes de depuración")
        self.debug.setChecked(config.debug)
        card = QFormLayout()
        card.addRow("Modo de la ficha:", self.mode)
        card.addRow("Idioma de la ficha:", self.language)
        card.addRow("Umbral de reconocimiento:", self.threshold)
        card.addRow("Ocultar la ficha tras (0 = nunca):", self.auto_hide)
        card.addRow("", self.debug)

        # Detección automática
        self.detection_enabled = QCheckBox("Reconocer al rival automáticamente")
        self.detection_enabled.setChecked(config.detection_enabled)
        self.interval = QSpinBox()
        self.interval.setRange(200, 5000)
        self.interval.setSingleStep(100)
        self.interval.setSuffix(" ms")
        self.interval.setValue(config.detection_interval_ms)
        self.hide_after = _spin(0, 600, config.detection_hide_after_seconds, 1, 0, " s")
        detection = QFormLayout()
        detection.addRow("", self.detection_enabled)
        detection.addRow("Intervalo de vigilancia:", self.interval)
        detection.addRow("Ocultar al terminar el combate tras:", self.hide_after)

        # Actualizaciones
        self.updates = QCheckBox("Comprobar una vez al día si hay versión nueva")
        self.updates.setChecked(config.updates_check)

        note = QLabel("Guardar reescribe config.toml con sus comentarios explicativos; "
                      "los comentarios que hayas añadido a mano se perderán.")
        note.setWordWrap(True)
        note.setStyleSheet("color:#888; font-size:11px;")

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        for title, form in (("Atajos de teclado", hotkeys), ("Ficha y reconocimiento", card), ("Detección automática", detection)):
            group = QGroupBox(title)
            group.setLayout(form)
            layout.addWidget(group)
        layout.addWidget(self.updates)
        layout.addWidget(note)
        layout.addWidget(buttons)

    def collect(self) -> tuple[Config | None, dict[str, str]]:
        """Configuración del formulario y errores por campo (vacío si todo es válido)."""
        errors: dict[str, str] = {}
        parsed = {}
        for field, _ in HOTKEY_FIELDS:
            text = self.hotkey_edits[field].text().strip()
            try:
                parsed[field] = parse_hotkey(text)
            except HotkeyParseError as exc:
                errors[field] = str(exc)
        combos = [(hk.modifiers, hk.vk) for hk in parsed.values()]
        if len(parsed) == len(HOTKEY_FIELDS) and len(set(combos)) < len(combos):
            for field in parsed:
                errors.setdefault(field, "Hay dos acciones con el mismo atajo.")
        if errors:
            return None, errors
        config = Config(
            hotkey_recognize=self.hotkey_edits["hotkey_recognize"].text().strip(),
            hotkey_calibrate=self.hotkey_edits["hotkey_calibrate"].text().strip(),
            hotkey_hide=self.hotkey_edits["hotkey_hide"].text().strip(),
            hotkey_toggle_mode=self.hotkey_edits["hotkey_toggle_mode"].text().strip(),
            overlay_mode=self.mode.currentData(),
            threshold=float(self.threshold.value()),
            debug=self.debug.isChecked(),
            language=self.language.currentData(),
            auto_hide_seconds=float(self.auto_hide.value()),
            detection_enabled=self.detection_enabled.isChecked(),
            detection_interval_ms=int(self.interval.value()),
            detection_hide_after_seconds=float(self.hide_after.value()),
            updates_check=self.updates.isChecked(),
        )
        return config, {}

    def _save(self) -> None:
        config, errors = self.collect()
        for field, label in self.hotkey_errors.items():
            label.setText(errors.get(field, ""))
            label.setVisible(field in errors)
        if config is not None:
            self.result_config = config
            self.accept()
