"""Ventana «Ajustes» (spec app-settings, redesign-settings-window)."""

from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .. import APP_NAME, __version__
from ..core.config import CARD_SECTIONS, LANGUAGES, MODES, Config
from ..core.profiles import Profile
from ..i18n import N_, _
from ..platform.hotkeys import HotkeyParseError, parse_hotkey
from ..platform.windows import WindowInfo
from .about import AboutPanel
from .icons import app_icon, arrow_images, glyph_icon
from .theme import ACCENT, PANEL_BORDER, TEXT_MUTED, settings_qss

# Nombres de idioma en su propio idioma: no se traducen.
LANGUAGE_LABELS = {"es": "Español", "en": "English", "fr": "Français", "de": "Deutsch", "it": "Italiano"}
HOTKEY_FIELDS = (
    ("hotkey_recognize", N_("Reconocer")),
    ("hotkey_calibrate", N_("Calibrar")),
    ("hotkey_hide", N_("Ocultar ficha")),
    ("hotkey_toggle_mode", N_("Cambiar de modo")),
    ("hotkey_cycle_form", N_("Cambiar de forma")),
    ("hotkey_toggle_stream", N_("Ficha del stream")),
)
MODE_LABELS = {"normal": N_("Normal (aventura y captura)"), "competitive": N_("Competitivo (combate)")}
# Idioma de la interfaz: «Español» y «English» son nombres de idioma y no se traducen.
INTERFACE_LANGUAGE_LABELS = (("auto", N_("Automático (idioma de Windows)")), ("es", "Español"), ("en", "English"))
# Secciones de la barra lateral: clave, glifo de Segoe Fluent Icons / MDL2, símbolo de reserva y título (D1)
SECTIONS = (
    ("general", "", "⚙", N_("General")),
    ("card", "", "▤", N_("Ficha")),
    ("recognition", "", "◎", N_("Reconocimiento")),
    ("hotkeys", "", "⌨", N_("Atajos")),
    ("stream", "", "◉", N_("Modo stream")),
    ("profiles", "", "▣", N_("Perfiles")),
    ("about", "", "ⓘ", N_("Acerca de")),
)
# Secciones de la ficha que se pueden ocultar (D8): nombre y qué muestra
SECTION_LABELS = {
    "matchup": (N_("Contra tu Pokémon"), N_("Ventaja, eficacias de un lado y otro y velocidad.")),
    "own_moves": (N_("Tus movimientos"), N_("Cuánto hace cada uno de tus ataques al rival.")),
    "eff": (N_("Eficacias"), N_("Debilidades, resistencias e inmunidades del rival.")),
    "stats": (N_("Estadísticas"), N_("Base y rango a su nivel.")),
    "abilities": (N_("Habilidades"), N_("Las que puede tener y qué hacen.")),
    "moves": (N_("Movimientos probables"), N_("Los que ha podido aprender a su nivel.")),
    "training": (N_("Entrenamiento"), N_("EVs que da, peso y perfil.")),
    "evo": (N_("Evolución"), N_("Su línea evolutiva.")),
    "forms": (N_("Otras formas"), N_("Megas, regionales y demás formas.")),
}
# Regiones del perfil: rol, nombre y si se puede quitar (spec game-profiles)
REGION_ROWS = (
    ("rival", N_("Rival"), False),
    ("rival2", N_("2.º rival (combates dobles)"), True),
    ("own", N_("Tu Pokémon"), True),
    ("moves", N_("Menú de ataques"), True),
)


class Toggle(QCheckBox):
    """Interruptor con el aspecto de la ficha; sigue siendo un QCheckBox (isChecked, toggled…)."""

    def __init__(self, accessible_name: str = "") -> None:
        super().__init__()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAccessibleName(accessible_name)
        self.setFixedSize(self.sizeHint())

    def sizeHint(self) -> QSize:  # noqa: N802 - API de Qt
        return QSize(42, 24)

    def hitButton(self, pos) -> bool:  # noqa: N802 - API de Qt
        return self.rect().contains(pos)

    def paintEvent(self, _event) -> None:  # noqa: N802 - API de Qt
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self.isEnabled():
            p.setOpacity(0.4)
        track = QRectF(1, 3, self.width() - 2, self.height() - 6)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(ACCENT if self.isChecked() else PANEL_BORDER))
        p.drawRoundedRect(track, track.height() / 2, track.height() / 2)
        knob = self.height() - 4
        x = self.width() - knob - 2 if self.isChecked() else 2
        p.setBrush(QColor("#14161d" if self.isChecked() else TEXT_MUTED))
        p.drawEllipse(QRectF(x, 2, knob, knob))


def _spin(minimum: float, maximum: float, value: float, step: float = 1, decimals: int = 0, suffix: str = ""):
    box = QDoubleSpinBox()
    box.setRange(minimum, maximum)
    box.setDecimals(decimals)
    box.setSingleStep(step)
    box.setValue(value)
    box.setFixedWidth(110)
    if suffix:
        box.setSuffix(suffix)
    return box


def _label(text: str, name: str = "", wrap: bool = False) -> QLabel:
    label = QLabel(text)
    if name:
        label.setObjectName(name)
    label.setWordWrap(wrap)
    return label


def _button(text: str, name: str = "") -> QPushButton:
    button = QPushButton(text)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    if name:
        button.setObjectName(name)
    return button


class _Card(QFrame):
    """Tarjeta con filas «etiqueta + explicación | control» separadas por una línea."""

    def __init__(self, title: str = "") -> None:
        super().__init__()
        self.setObjectName("settings-card")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(18, 14, 18, 14)
        self._layout.setSpacing(10)
        self._rows = 0
        if title:
            self._layout.addWidget(_label(title.upper(), "card-title"))

    def add_row(self, label: str, control: QWidget | None = None, hint: str = "", below: QWidget | None = None):
        if self._rows:
            line = QFrame()
            line.setObjectName("row-separator")
            self._layout.addWidget(line)
        self._rows += 1
        texts = QVBoxLayout()
        texts.setSpacing(2)
        texts.addWidget(_label(label, "row-label"))
        if hint:
            texts.addWidget(_label(hint, "row-hint", wrap=True))
        row = QHBoxLayout()
        row.setSpacing(16)
        row.addLayout(texts, 1)
        if control is not None:
            row.addWidget(control, 0, Qt.AlignmentFlag.AlignVCenter)
        holder = QWidget()
        column = QVBoxLayout(holder)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(4)
        column.addLayout(row)
        if below is not None:
            column.addWidget(below)
        self._layout.addWidget(holder)
        return holder

    def add_widget(self, widget: QWidget) -> None:
        self._layout.addWidget(widget)


class _Page(QScrollArea):
    def __init__(self, title: str, subtitle: str) -> None:
        super().__init__()
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget()
        body.setObjectName("settings-page")
        self.body = QVBoxLayout(body)
        self.body.setContentsMargins(28, 24, 28, 24)
        self.body.setSpacing(14)
        self.body.addWidget(_label(title, "page-title"))
        self.body.addWidget(_label(subtitle, "page-subtitle", wrap=True))
        self.body.addSpacing(4)
        self.setWidget(body)

    def add(self, widget: QWidget) -> None:
        self.body.addWidget(widget)

    def finish(self) -> None:
        self.body.addStretch(1)


class SettingsWindow(QWidget):
    """Panel de ajustes con secciones (D1). Lo de config.toml se guarda con «Guardar»; lo de Perfiles, al momento."""

    saved = pyqtSignal(object)  # Config
    # Mismas señales que la bandeja (D4, D6)
    window_selected = pyqtSignal(object)  # WindowInfo
    profile_selected = pyqtSignal(str)
    profile_game_selected = pyqtSignal(object)  # id de juego o None
    preset_requested = pyqtSignal()
    calibrate_requested = pyqtSignal()
    region_requested = pyqtSignal(str)
    region_remove_requested = pyqtSignal(str)
    delete_profile_requested = pyqtSignal()
    open_data_requested = pyqtSignal()
    report_requested = pyqtSignal()
    install_ocr_requested = pyqtSignal()
    update_requested = pyqtSignal()
    copy_stream_url_requested = pyqtSignal()
    expand_sections_requested = pyqtSignal()  # «Desplegar todas las secciones» (improve-card-visuals)

    def __init__(
        self,
        config: Config,
        list_windows: Callable[[], list[WindowInfo]] = lambda: [],
        get_target: Callable[[], WindowInfo | None] = lambda: None,
        get_profiles: Callable[[], tuple[list[Profile], str | None]] = lambda: ([], None),
        get_games: Callable[[], list[tuple[str, str]]] = lambda: [],
    ) -> None:
        super().__init__(None, Qt.WindowType.Window)
        self.setObjectName("settings-window")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        arrows = arrow_images(TEXT_MUTED)
        self.setStyleSheet(settings_qss(arrows["down"], arrows["up"]))
        self.setWindowTitle(_("Ajustes de BattleLens"))
        self.setWindowIcon(app_icon())
        self.setMinimumSize(760, 500)
        self.resize(880, 600)
        self._list_windows = list_windows
        self._get_target = get_target
        self._get_profiles = get_profiles
        self._get_games = get_games
        self.result_config: Config | None = None

        self.pages = QStackedWidget()
        self._section_index: dict[str, int] = {}
        self.nav = QListWidget()
        self.nav.setObjectName("settings-nav")
        self.nav.setCursor(Qt.CursorShape.PointingHandCursor)
        self.nav.setIconSize(QSize(18, 18))
        for key, glyph, symbol, title in SECTIONS:
            item = QListWidgetItem(glyph_icon(glyph, symbol, TEXT_MUTED, ACCENT), "  " + _(title))
            item.setData(Qt.ItemDataRole.UserRole, key)
            self.nav.addItem(item)
        builders = {
            "general": self._general_page, "card": self._card_page, "recognition": self._recognition_page,
            "hotkeys": self._hotkeys_page, "stream": self._stream_page, "profiles": self._profiles_page,
            "about": self._about_page,
        }
        for key, *_rest in SECTIONS:
            self._section_index[key] = self.pages.addWidget(builders[key](config))
        self.nav.currentRowChanged.connect(self._on_section_changed)

        brand_icon = QLabel()
        brand_icon.setPixmap(app_icon().pixmap(28, 28))
        brand = QHBoxLayout()
        brand.setSpacing(10)
        brand.addWidget(brand_icon)
        names = QVBoxLayout()
        names.setSpacing(0)
        names.addWidget(_label(APP_NAME, "settings-brand"))
        names.addWidget(_label(f"v{__version__}", "row-hint"))
        brand.addLayout(names, 1)
        sidebar = QWidget()
        sidebar.setObjectName("settings-sidebar")
        sidebar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        sidebar.setFixedWidth(210)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(14, 18, 14, 14)
        side.setSpacing(14)
        side.addLayout(brand)
        side.addWidget(self.nav, 1)

        # Pie: aviso o «cambios sin guardar» y botones (D3)
        self.footer_note = _label(_("Guardar reescribe config.toml con sus comentarios explicativos; "
                                    "los comentarios que hayas añadido a mano se perderán."), "footer-note", wrap=True)
        self.dirty_label = _label(_("Cambios sin guardar"), "footer-dirty")
        self.dirty_label.hide()
        self.close_button = _button(_("Cerrar"))
        self.close_button.clicked.connect(self.close)
        self.save_button = _button(_("Guardar"), "primary")
        self.save_button.clicked.connect(self._save)
        footer = QWidget()
        footer.setObjectName("settings-footer")
        footer.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        foot = QHBoxLayout(footer)
        foot.setContentsMargins(20, 12, 20, 12)
        foot.setSpacing(12)
        foot.addWidget(self.dirty_label)
        foot.addWidget(self.footer_note, 1)
        foot.addWidget(self.close_button)
        foot.addWidget(self.save_button)

        content = QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)
        content.addWidget(self.pages, 1)
        content.addWidget(footer)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(sidebar)
        layout.addLayout(content, 1)

        self._base: dict[str, object] = {}
        self.set_config(config)
        self._connect_dirty()
        self.nav.setCurrentRow(0)

    # ---- páginas ---------------------------------------------------------------------

    def _general_page(self, config: Config) -> QWidget:
        page = _Page(_("General"), _("Idioma, actualizaciones y mantenimiento."))
        self.interface_language = QComboBox()
        for code, label in INTERFACE_LANGUAGE_LABELS:
            self.interface_language.addItem(_(label) if code == "auto" else label, code)
        self.updates = Toggle(_("Comprobar una vez al día si hay versión nueva"))
        main = _Card()
        main.add_row(_("Idioma de la interfaz"), self.interface_language,
                     _("Menús, avisos y textos de la ficha. Los menús cambian al reiniciar."))
        main.add_row(_("Buscar actualizaciones"), self.updates, _("Comprobar una vez al día si hay versión nueva"))
        page.add(main)

        self.update_button = _button(_("Descargar versión nueva…"), "primary")
        self.update_button.clicked.connect(self.update_requested)
        self.ocr_button = _button(_("Instalar OCR de Windows…"), "primary")
        self.ocr_button.clicked.connect(self.install_ocr_requested)
        data = _button(_("Abrir carpeta"))
        data.clicked.connect(self.open_data_requested)
        report = _button(_("Crear informe…"))
        report.clicked.connect(self.report_requested)
        tools = _Card(_("Mantenimiento"))
        self._update_row = tools.add_row(_("Hay una versión nueva"), self.update_button,
                                         _("Se abre su página de descarga en el navegador."))
        self._ocr_row = tools.add_row(_("Falta el OCR de Windows"), self.ocr_button,
                                      _("BattleLens lo necesita para leer los nombres."))
        tools.add_row(_("Carpeta de datos"), data, _("Configuración, perfiles, registro y recortes de depuración."))
        tools.add_row(_("Informar de un problema"), report, _("Crea un ZIP para adjuntarlo en GitHub."))
        self._update_row.hide()
        self._ocr_row.hide()
        page.add(tools)
        page.finish()
        return page

    def _card_page(self, config: Config) -> QWidget:
        page = _Page(_("Ficha"), _("Qué muestra la ficha del rival y cuándo se oculta."))
        self.mode = QComboBox()
        for code in MODES:
            self.mode.addItem(_(MODE_LABELS[code]), code)
        self.language = QComboBox()
        for code in LANGUAGES:
            self.language.addItem(LANGUAGE_LABELS[code], code)
        self.auto_hide = _spin(0, 600, config.auto_hide_seconds, 1, 0, " s")
        card = _Card()
        card.add_row(_("Modo de la ficha"), self.mode,
                     _("Normal es compacta (aventura y captura); Competitivo muestra todos los datos de combate."))
        card.add_row(_("Idioma de los datos Pokémon"), self.language, _("Nombres, tipos, movimientos y habilidades."))
        card.add_row(_("Ocultar la ficha tras"), self.auto_hide, _("Segundos; 0 = no se oculta sola."))
        page.add(card)

        page.add(self._sections_card())

        self.expand_button = _button(_("Desplegar todas las secciones"))
        self.expand_button.clicked.connect(self.expand_sections_requested)
        sections = _Card()
        sections.add_row(_("Secciones plegadas"), self.expand_button,
                         _("Un clic en el título de una sección de la ficha la pliega. Se aplica al momento."))
        page.add(sections)
        page.finish()
        return page

    def _sections_card(self) -> QWidget:
        """Tu ficha a medida: qué secciones se ven en cada modo (también en la del stream) (D8)."""
        self.section_toggles: dict[tuple[str, str], Toggle] = {}
        card = _Card(_("Secciones de la ficha"))
        card.add_widget(_label(_("Elige qué ves en cada modo; la ficha del stream sigue lo mismo. El nombre, "
                                 "los tipos y la captura siempre se muestran."), "row-hint", wrap=True))
        heads = QWidget()
        head = QHBoxLayout(heads)
        head.setContentsMargins(0, 4, 0, 0)
        head.addStretch(1)
        for mode in MODES:
            title = _label(_("Normal") if mode == "normal" else _("Competitivo"), "card-title")
            title.setFixedWidth(90)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            head.addWidget(title)
        card.add_widget(heads)
        for key in CARD_SECTIONS["competitive"]:
            label, hint = SECTION_LABELS[key]
            cells = QWidget()
            row = QHBoxLayout(cells)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(0)
            for mode in MODES:
                cell = QWidget()
                cell.setFixedWidth(90)
                inner = QHBoxLayout(cell)
                inner.setContentsMargins(0, 0, 0, 0)
                inner.setAlignment(Qt.AlignmentFlag.AlignCenter)
                if key in CARD_SECTIONS[mode]:
                    toggle = Toggle(f"{_(label)} · {mode}")
                    self.section_toggles[(mode, key)] = toggle
                    inner.addWidget(toggle)
                else:
                    inner.addWidget(_label("—", "row-hint"))  # esta sección no existe en la ficha Normal
                row.addWidget(cell)
            card.add_row(_(label), cells, _(hint))
        reset = _button(_("Mostrar todas"))
        reset.clicked.connect(lambda: [t.setChecked(True) for t in self.section_toggles.values()])
        card.add_row(_("Ficha completa"), reset, _("Vuelve a mostrar todas las secciones."))
        return card

    def _recognition_page(self, config: Config) -> QWidget:
        page = _Page(_("Reconocimiento"), _("Cómo lee BattleLens los nombres y cuándo vigila el combate."))
        self.threshold = QSlider(Qt.Orientation.Horizontal)
        self.threshold.setRange(0, 100)
        self.threshold.setFixedWidth(160)
        self._threshold_value = _label("", "row-label")
        self._threshold_value.setFixedWidth(28)
        self._threshold_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.threshold.valueChanged.connect(lambda v: self._threshold_value.setText(str(v)))
        threshold = QWidget()
        row = QHBoxLayout(threshold)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(self.threshold)
        row.addWidget(self._threshold_value)
        self.debug = Toggle(_("Guardar recortes de depuración"))
        reading = _Card(_("Lectura"))
        reading.add_row(_("Umbral de reconocimiento"), threshold,
                        _("Puntuación mínima (0-100) para dar por bueno un nombre."))
        reading.add_row(_("Guardar recortes de depuración"), self.debug, _("En la carpeta debug/ de los datos."))
        page.add(reading)

        self.detection_enabled = Toggle(_("Reconocer al rival automáticamente"))
        self.interval = QSpinBox()
        self.interval.setRange(200, 5000)
        self.interval.setSingleStep(100)
        self.interval.setSuffix(" ms")
        self.interval.setFixedWidth(110)
        self.hide_after = _spin(0, 600, config.detection_hide_after_seconds, 1, 0, " s")
        detection = _Card(_("Detección automática"))
        detection.add_row(_("Reconocer al rival automáticamente"), self.detection_enabled,
                          _("Al entrar en combate, sin pulsar el atajo."))
        detection.add_row(_("Intervalo de vigilancia"), self.interval, _("Cada cuánto se mira la región del nombre."))
        detection.add_row(_("Ocultar al terminar el combate tras"), self.hide_after,
                          _("Segundos sin ver al rival; 0 = no se oculta sola."))
        page.add(detection)
        page.finish()
        return page

    def _hotkeys_page(self, config: Config) -> QWidget:
        page = _Page(_("Atajos"), _("Combinaciones con al menos un modificador (Ctrl, Alt, Shift o Win). "
                                    "Las teclas F solas no se permiten: los emuladores las usan."))
        self.hotkey_edits: dict[str, QLineEdit] = {}
        self.hotkey_errors: dict[str, QLabel] = {}
        card = _Card()
        for field, label in HOTKEY_FIELDS:
            edit = QLineEdit()
            edit.setPlaceholderText(_("p. ej. Ctrl+Alt+P"))
            edit.setFixedWidth(180)
            error = _label("", "field-error", wrap=True)
            error.hide()
            card.add_row(_(label), edit, below=error)
            self.hotkey_edits[field] = edit
            self.hotkey_errors[field] = error
        page.add(card)
        page.finish()
        return page

    def _stream_page(self, config: Config) -> QWidget:
        page = _Page(_("Modo stream"), _("Una ficha para OBS como fuente de navegador, aparte de la ficha privada."))
        self.stream_enabled = Toggle(_("Fuente de navegador para OBS"))
        self.stream_port = QSpinBox()
        self.stream_port.setRange(1024, 65535)
        self.stream_port.setFixedWidth(110)
        self.stream_mode = QComboBox()
        for code in MODES:
            self.stream_mode.addItem(_(MODE_LABELS[code]), code)
        card = _Card()
        card.add_row(_("Fuente de navegador para OBS"), self.stream_enabled,
                     _("Sirve la ficha solo en este equipo (localhost)."))
        card.add_row(_("Puerto"), self.stream_port, "http://localhost:…/")
        card.add_row(_("Ficha del stream"), self.stream_mode, _("Puede ser distinta de la tuya."))
        page.add(card)

        self.stream_url = QLineEdit()
        self.stream_url.setReadOnly(True)
        self.stream_url.setPlaceholderText(_("Activa el modo stream y guarda"))
        self.copy_url_button = _button(_("Copiar"))
        self.copy_url_button.clicked.connect(self.copy_stream_url_requested)
        url = QWidget()
        row = QHBoxLayout(url)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(self.stream_url, 1)
        row.addWidget(self.copy_url_button)
        obs = _Card(_("URL para OBS"))
        obs.add_widget(url)
        obs.add_widget(_label(_("Añádela en OBS como «Navegador». Con ?scale=1.5 al final se ve más grande."),
                              "row-hint", wrap=True))
        page.add(obs)
        page.finish()
        self.set_stream(False, None)
        return page

    def _profiles_page(self, config: Config) -> QWidget:
        page = _Page(_("Perfiles"), _("Dónde está cada nombre en la pantalla de tu juego. "
                                      "Estos cambios se aplican al momento, sin pulsar «Guardar»."))
        self.window_combo = QComboBox()
        self.window_combo.setMinimumWidth(260)
        self.window_combo.activated.connect(self._on_window_activated)
        refresh = _button(_("Actualizar"))
        refresh.clicked.connect(self._populate_windows)
        target = QWidget()
        row = QHBoxLayout(target)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(self.window_combo, 1)
        row.addWidget(refresh)
        emulator = _Card(_("Emulador"))
        emulator.add_row(_("Ventana del emulador"), target, _("La ventana que se captura."))
        page.add(emulator)

        self.profile_list = QListWidget()
        self.profile_list.setObjectName("profile-list")
        self.profile_list.itemSelectionChanged.connect(self._on_profile_clicked)
        self.preset_button = _button(_("Nuevo con un preset…"), "primary")
        self.preset_button.clicked.connect(self.preset_requested)
        self.manual_button = _button(_("Calibrar a mano…"))
        self.manual_button.clicked.connect(self.calibrate_requested)
        self.delete_button = _button(_("Eliminar…"), "danger")
        self.delete_button.clicked.connect(self.delete_profile_requested)
        actions = QHBoxLayout()
        actions.addWidget(self.preset_button)
        actions.addWidget(self.manual_button)
        actions.addStretch(1)
        actions.addWidget(self.delete_button)
        holder = QWidget()
        holder.setLayout(actions)
        actions.setContentsMargins(0, 0, 0, 0)
        self.no_profiles = _label(_("Aún no tienes perfiles. Entra en un combate y crea uno con un preset: "
                                    "BattleLens coloca las regiones por ti."), "row-hint", wrap=True)
        profiles = _Card(_("Perfiles"))
        profiles.add_widget(self.no_profiles)
        profiles.add_widget(self.profile_list)
        profiles.add_widget(holder)
        page.add(profiles)

        self.game_combo = QComboBox()
        self.game_combo.setMinimumWidth(260)
        self.game_combo.activated.connect(self._on_game_activated)
        self.active_card = _Card(_("Perfil activo"))
        self.active_card.add_row(_("Juego"), self.game_combo, _("Decide las formas regionales y la tabla de tipos."))
        self.region_rows: dict[str, tuple[QLabel, QPushButton, QPushButton | None]] = {}
        for role, label, removable in REGION_ROWS:
            status = _label("", "badge-missing")
            calibrate = _button("")
            calibrate.setMinimumWidth(110)
            calibrate.clicked.connect(lambda _=False, r=role: self.region_requested.emit(r))
            remove = None
            buttons = QHBoxLayout()
            buttons.setContentsMargins(0, 0, 0, 0)
            buttons.addWidget(status)
            buttons.addSpacing(8)
            buttons.addWidget(calibrate)
            if not removable:
                buttons.addSpacing(86)  # el hueco de «Quitar»
            if removable:
                remove = _button(_("Quitar"), "danger")
                remove.setMinimumWidth(80)
                policy = remove.sizePolicy()
                policy.setRetainSizeWhenHidden(True)  # los botones quedan en columna
                remove.setSizePolicy(policy)
                remove.clicked.connect(lambda _=False, r=role: self.region_remove_requested.emit(r))
                buttons.addWidget(remove)
            controls = QWidget()
            controls.setLayout(buttons)
            self.active_card.add_row(_(label), controls)
            self.region_rows[role] = (status, calibrate, remove)
        page.add(self.active_card)
        page.finish()
        return page

    def _about_page(self, config: Config) -> QWidget:
        page = _Page(_("Acerca de"), _("Créditos y licencia."))
        card = _Card()
        self.about = AboutPanel()
        card.add_widget(self.about)
        page.add(card)
        page.finish()
        return page

    # ---- navegación -----------------------------------------------------------------

    def show_section(self, key: str) -> None:
        self.nav.setCurrentRow(self._section_index[key])

    def current_section(self) -> str:
        return SECTIONS[self.nav.currentRow()][0]

    def _on_section_changed(self, row: int) -> None:
        self.pages.setCurrentIndex(row)
        if SECTIONS[row][0] == "profiles":
            self.refresh()

    # ---- valores de config.toml ------------------------------------------------------

    def set_config(self, config: Config) -> None:
        """Muestra `config` y la toma como base: no quedan cambios pendientes."""
        for field, _label_text in HOTKEY_FIELDS:
            self.hotkey_edits[field].setText(getattr(config, field))
        for combo, value in ((self.interface_language, config.interface_language), (self.language, config.language),
                             (self.mode, config.overlay_mode), (self.stream_mode, config.stream_card_mode)):
            combo.setCurrentIndex(max(combo.findData(value), 0))
        self.threshold.setValue(round(config.threshold))
        self._threshold_value.setText(str(self.threshold.value()))
        self.auto_hide.setValue(config.auto_hide_seconds)
        self.debug.setChecked(config.debug)
        self.detection_enabled.setChecked(config.detection_enabled)
        self.interval.setValue(config.detection_interval_ms)
        self.hide_after.setValue(config.detection_hide_after_seconds)
        self.stream_enabled.setChecked(config.stream_enabled)
        self.stream_port.setValue(config.stream_port)
        self.updates.setChecked(config.updates_check)
        for (mode, key), toggle in self.section_toggles.items():
            toggle.setChecked(key not in config.hidden_sections(mode))
        self._show_errors({})
        self._base = self._values()
        self._update_dirty()

    def sync_value(self, name: str, value) -> None:
        """Refleja un cambio hecho fuera (bandeja) sin marcarlo como pendiente (spec app-settings)."""
        widget = getattr(self, name)
        if isinstance(widget, QComboBox):
            widget.setCurrentIndex(max(widget.findData(value), 0))
        elif isinstance(widget, QCheckBox):
            widget.setChecked(bool(value))
        self._base[name] = self._values()[name]
        self._update_dirty()

    def _value_widgets(self) -> dict[str, QWidget]:
        widgets: dict[str, QWidget] = {f: e for f, e in self.hotkey_edits.items()}
        widgets.update({f"section:{mode}:{key}": t for (mode, key), t in self.section_toggles.items()})
        for name in ("interface_language", "language", "mode", "stream_mode", "threshold", "auto_hide", "debug",
                     "detection_enabled", "interval", "hide_after", "stream_enabled", "stream_port", "updates"):
            widgets[name] = getattr(self, name)
        return widgets

    def _values(self) -> dict[str, object]:
        values: dict[str, object] = {}
        for name, widget in self._value_widgets().items():
            if isinstance(widget, QLineEdit):
                values[name] = widget.text().strip()
            elif isinstance(widget, QComboBox):
                values[name] = widget.currentData()
            elif isinstance(widget, QCheckBox):
                values[name] = widget.isChecked()
            else:
                values[name] = widget.value()
        return values

    def _connect_dirty(self) -> None:
        for widget in self._value_widgets().values():
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self._update_dirty)
            elif isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(self._update_dirty)
            elif isinstance(widget, QCheckBox):
                widget.toggled.connect(self._update_dirty)
            else:
                widget.valueChanged.connect(self._update_dirty)

    def has_changes(self) -> bool:
        return self._values() != self._base

    def _update_dirty(self, *_args) -> None:
        dirty = self.has_changes()
        self.save_button.setEnabled(dirty)
        self.dirty_label.setVisible(dirty)
        self.footer_note.setVisible(not dirty)

    def collect(self) -> tuple[Config | None, dict[str, str]]:
        """Configuración del formulario y errores por campo (vacío si todo es válido)."""
        errors: dict[str, str] = {}
        parsed = {}
        for field, _label_text in HOTKEY_FIELDS:
            text = self.hotkey_edits[field].text().strip()
            try:
                parsed[field] = parse_hotkey(text)
            except HotkeyParseError as exc:
                errors[field] = str(exc)
        combos = [(hk.modifiers, hk.vk) for hk in parsed.values()]
        if len(parsed) == len(HOTKEY_FIELDS) and len(set(combos)) < len(combos):
            for field in parsed:
                errors.setdefault(field, _("Hay dos acciones con el mismo atajo."))
        if errors:
            return None, errors
        config = Config(
            hotkey_recognize=self.hotkey_edits["hotkey_recognize"].text().strip(),
            hotkey_calibrate=self.hotkey_edits["hotkey_calibrate"].text().strip(),
            hotkey_hide=self.hotkey_edits["hotkey_hide"].text().strip(),
            hotkey_toggle_mode=self.hotkey_edits["hotkey_toggle_mode"].text().strip(),
            hotkey_cycle_form=self.hotkey_edits["hotkey_cycle_form"].text().strip(),
            hotkey_toggle_stream=self.hotkey_edits["hotkey_toggle_stream"].text().strip(),
            stream_enabled=self.stream_enabled.isChecked(),
            stream_port=int(self.stream_port.value()),
            stream_card_mode=self.stream_mode.currentData(),
            overlay_mode=self.mode.currentData(),
            threshold=float(self.threshold.value()),
            debug=self.debug.isChecked(),
            language=self.language.currentData(),
            interface_language=self.interface_language.currentData(),
            auto_hide_seconds=float(self.auto_hide.value()),
            detection_enabled=self.detection_enabled.isChecked(),
            detection_interval_ms=int(self.interval.value()),
            detection_hide_after_seconds=float(self.hide_after.value()),
            updates_check=self.updates.isChecked(),
            hidden_sections_normal=self._hidden("normal"),
            hidden_sections_competitive=self._hidden("competitive"),
        )
        return config, {}

    def _hidden(self, mode: str) -> tuple[str, ...]:
        return tuple(key for key in CARD_SECTIONS[mode] if not self.section_toggles[(mode, key)].isChecked())

    def _show_errors(self, errors: dict[str, str]) -> None:
        for field, label in self.hotkey_errors.items():
            label.setText(errors.get(field, ""))
            label.setVisible(field in errors)
            edit = self.hotkey_edits[field]
            edit.setProperty("invalid", field in errors)
            edit.style().unpolish(edit)
            edit.style().polish(edit)

    def _save(self) -> bool:
        config, errors = self.collect()
        self._show_errors(errors)
        if config is None:
            self.show_section("hotkeys")  # hoy solo los atajos pueden ser inválidos
            first = next(f for f, _label_text in HOTKEY_FIELDS if f in errors)
            self.hotkey_edits[first].setFocus()
            return False
        self.result_config = config
        self._base = self._values()
        self._update_dirty()
        self.saved.emit(config)
        return True

    # ---- cerrar con cambios pendientes (D3) ------------------------------------------

    def ask_unsaved(self) -> str:
        """«save», «discard» o «cancel»; aparte para poder sustituirlo en los tests."""
        box = QMessageBox(QMessageBox.Icon.Question, _("Cambios sin guardar"),
                          _("¿Quieres guardar los cambios antes de cerrar?"), parent=self)
        save = box.addButton(_("Guardar"), QMessageBox.ButtonRole.AcceptRole)
        discard = box.addButton(_("Descartar"), QMessageBox.ButtonRole.DestructiveRole)
        box.addButton(_("Cancelar"), QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(save)
        box.exec()
        clicked = box.clickedButton()
        return "save" if clicked is save else "discard" if clicked is discard else "cancel"

    def closeEvent(self, event) -> None:  # noqa: N802 - API de Qt
        if self.has_changes():
            answer = self.ask_unsaved()
            if answer == "cancel" or (answer == "save" and not self._save()):
                event.ignore()
                return
            if answer == "discard":
                self._restore_base()
        event.accept()

    def _restore_base(self) -> None:
        for name, widget in self._value_widgets().items():
            value = self._base[name]
            if isinstance(widget, QLineEdit):
                widget.setText(str(value))
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(max(widget.findData(value), 0))
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))
            else:
                widget.setValue(value)
        self._show_errors({})

    # ---- estado que viene del controlador (D6) ---------------------------------------

    def set_stream(self, enabled: bool, url: str | None) -> None:
        self.stream_url.setText(url or "")
        self.copy_url_button.setEnabled(url is not None)

    def set_update(self, version: str | None) -> None:
        if version:
            self.update_button.setText(_("Descargar BattleLens {version}…", version=version))
        self._update_row.setVisible(bool(version))

    def set_ocr_missing(self, missing: bool) -> None:
        self._ocr_row.setVisible(missing)

    # ---- perfiles (D4) ---------------------------------------------------------------

    def refresh(self) -> None:
        """Vuelve a leer ventana, perfiles y regiones."""
        self._populate_windows()
        profiles, active_id = self._get_profiles()
        active = next((p for p in profiles if p.id == active_id), None)
        games = dict(self._get_games())

        self.profile_list.blockSignals(True)
        self.profile_list.clear()
        for profile in profiles:
            game = games.get(profile.game) if profile.game else None
            item = QListWidgetItem(f"{profile.name}   ·   {game}" if game else profile.name)
            item.setData(Qt.ItemDataRole.UserRole, profile.id)
            self.profile_list.addItem(item)
            if profile.id == active_id:
                item.setSelected(True)
                self.profile_list.setCurrentItem(item)
        self.profile_list.blockSignals(False)
        rows = min(len(profiles), 5)
        row_height = self.profile_list.sizeHintForRow(0) if profiles else 0
        self.profile_list.setFixedHeight(rows * (row_height + 4) + 2 * self.profile_list.frameWidth() + 8)
        self.profile_list.setVisible(bool(profiles))
        self.no_profiles.setVisible(not profiles)
        self.manual_button.setEnabled(True)
        self.delete_button.setEnabled(active is not None)

        self.active_card.setVisible(active is not None)
        if active is None:
            return
        self.game_combo.clear()
        for game_id, label in [(None, _("Sin especificar")), *self._get_games()]:
            self.game_combo.addItem(label, game_id)
        self.game_combo.setCurrentIndex(max(self.game_combo.findData(active.game), 0))
        regions = {"rival": active.region, "rival2": active.rival2_region, "own": active.own_region,
                   "moves": active.moves_region}
        for role, (status, calibrate, remove) in self.region_rows.items():
            present = regions[role] is not None
            status.setText(_("✓ Calibrada") if present else _("Sin calibrar"))
            status.setObjectName("badge-ok" if present else "badge-missing")
            status.style().unpolish(status)
            status.style().polish(status)
            calibrate.setText(_("Recalibrar…") if present else _("Calibrar…"))
            if remove is not None:
                remove.setVisible(present)

    def _populate_windows(self) -> None:
        target = self._get_target()
        windows = self._list_windows()
        self.window_combo.clear()
        if target is not None and all(w.hwnd != target.hwnd for w in windows):
            windows = [target, *windows]
        if not windows:
            self.window_combo.addItem(_("(no hay ventanas)"), None)
        for info in windows:
            self.window_combo.addItem(info.label, info)
        index = next((i for i, w in enumerate(windows) if target is not None and w.hwnd == target.hwnd), -1)
        if target is None and windows:
            self.window_combo.insertItem(0, _("— selecciona una —"), None)
            index = 0
        self.window_combo.setCurrentIndex(max(index, 0))

    def _on_window_activated(self, index: int) -> None:
        info = self.window_combo.itemData(index)
        if info is not None:
            self.window_selected.emit(info)

    def _on_profile_clicked(self) -> None:
        items = self.profile_list.selectedItems()
        if items:
            profile_id = items[0].data(Qt.ItemDataRole.UserRole)
            _profiles, active_id = self._get_profiles()
            if profile_id != active_id:
                self.profile_selected.emit(profile_id)

    def _on_game_activated(self, index: int) -> None:
        self.profile_game_selected.emit(self.game_combo.itemData(index))
