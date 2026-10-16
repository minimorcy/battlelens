"""Colores y textos compartidos por la interfaz."""

from ..i18n import N_

TYPE_COLORS = {
    "normal": "#A8A77A",
    "fire": "#EE8130",
    "water": "#6390F0",
    "electric": "#F7D02C",
    "grass": "#7AC74C",
    "ice": "#96D9D6",
    "fighting": "#C22E28",
    "poison": "#A33EA1",
    "ground": "#E2BF65",
    "flying": "#A98FF3",
    "psychic": "#F95587",
    "bug": "#A6B91A",
    "rock": "#B6A136",
    "ghost": "#735797",
    "dragon": "#6F35FC",
    "dark": "#705746",
    "steel": "#B7B7CE",
    "fairy": "#D685AD",
}
# Tipos con fondo claro que necesitan texto oscuro para ser legibles
DARK_TEXT_TYPES = {"electric", "ice", "ground", "steel"}

STAT_LABELS = {
    "hp": N_("PS"),
    "attack": N_("Ataque"),
    "defense": N_("Defensa"),
    "special": N_("Especial"),
    "special_attack": N_("At. Esp."),
    "special_defense": N_("Def. Esp."),
    "speed": N_("Velocidad"),
}
# Claves: dificultad de captura en español (clave interna; se traduce al mostrarla)
CAPTURE_COLORS = {"Fácil": "#3ddc97", "Media": "#ffcb05", "Difícil": "#ff8c42", "Muy difícil": "#e5484d"}
MULTIPLIER_LABELS = {4.0: "×4", 2.0: "×2", 0.5: "×½", 0.25: "×¼", 0.0: "×0"}

PANEL_BG = "rgba(24, 26, 34, 235)"
PANEL_BORDER = "#3a3f4f"
TEXT = "#e8e8ee"
TEXT_MUTED = "#9aa0b4"
ACCENT = "#ffcb05"


def stat_color(value: int) -> str:
    if value < 50:
        return "#f34444"
    if value < 70:
        return "#ff7f0f"
    if value < 90:
        return "#ffdd57"
    if value < 120:
        return "#a0e515"
    return "#23cd5e"


# ---- ficha: bloques, pastillas suaves y colores semánticos (improve-card-visuals D1) ----
PANEL_SOLID = "#181a22"  # PANEL_BG sin transparencia, para mezclar colores
SURFACE = "rgba(255, 255, 255, 9)"  # fondo de los bloques (alfa 0-255, como en Qt)
SURFACE_BORDER = "rgba(255, 255, 255, 16)"
GOOD = "#3ddc97"  # bueno para el jugador
BAD = "#e5484d"  # malo para el jugador
NEUTRAL = "#8a90a3"
VERDICT_COLORS = {"advantage": "#2e9d5b", "neutral": "#5b6274", "disadvantage": "#c8414b"}
STAT_BAR = "#7f9be0"
STAT_BAR_MAX = "#a9c1ff"
SOFT_PILL_BASE = "#1b1d26"


def _rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def blend(color: str, base: str, amount: float) -> str:
    """`amount` de `color` sobre `base` (0 = base, 1 = color), como hex opaco."""
    c, b = _rgb(color), _rgb(base)
    return "#" + "".join(f"{round(b[i] + (c[i] - b[i]) * amount):02x}" for i in range(3))


def rgba(color: str, alpha: float) -> str:
    r, g, b = _rgb(color)
    return f"rgba({r}, {g}, {b}, {round(alpha * 255)})"


def soft_type_colors(type_id: str | None) -> tuple[str, str]:
    """Fondo y borde de la pastilla suave de un tipo (texto siempre `TEXT`)."""
    color = TYPE_COLORS.get(type_id or "", "#555555")
    return blend(color, SOFT_PILL_BASE, 0.24), blend(color, PANEL_SOLID, 0.58)


def tone_color(tone: str) -> str:
    return {"good": GOOD, "bad": BAD}.get(tone, NEUTRAL)


def stat_bar_color(value: int, highest: int, lowest: int) -> str:
    """Una sola gama: la estadística más alta en el color pleno y la más baja en rojo atenuado (P2)."""
    if value == highest:
        return STAT_BAR_MAX
    if value == lowest and lowest != highest:
        return blend(BAD, PANEL_SOLID, 0.65)
    return blend(STAT_BAR, PANEL_SOLID, 0.7)


def contrast_ratio(fg: str, bg: str) -> float:
    def luminance(color: str) -> float:
        channels = [c / 255 for c in _rgb(color)]
        lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

    high, low = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (high + 0.05) / (low + 0.05)


# ---- ventana de Ajustes (redesign-settings-window D2) ----
SETTINGS_BG = "#14161d"
SETTINGS_SIDEBAR = "#1b1e27"
SETTINGS_CARD = "#20232d"
SETTINGS_FIELD = "#2a2e3a"
DANGER = "#e5484d"
SUCCESS = "#3ddc97"

def settings_qss(down_arrow: str, up_arrow: str) -> str:
    """Hoja de estilos de Ajustes; las flechas son rutas a PNG (ver `icons.arrow_images`)."""
    return f"""
#settings-window {{ background: {SETTINGS_BG}; }}
#settings-window QWidget {{ color: {TEXT}; font-size: 13px; }}
#settings-window QScrollArea, #settings-window #settings-page {{ background: transparent; border: none; }}
#settings-sidebar {{ background: {SETTINGS_SIDEBAR}; border-right: 1px solid {PANEL_BORDER}; }}
#settings-window #settings-brand {{ font-size: 15px; font-weight: 700; }}
#settings-nav {{ background: transparent; border: none; outline: none; }}
#settings-nav::item {{ padding: 9px 12px; margin: 2px 0; border-radius: 8px; color: {TEXT_MUTED}; }}
#settings-nav::item:hover {{ background: {SETTINGS_CARD}; color: {TEXT}; }}
#settings-nav::item:selected {{ background: {SETTINGS_FIELD}; color: {ACCENT}; font-weight: 600; }}
#settings-window #page-title {{ font-size: 22px; font-weight: 700; }}
#settings-window #page-subtitle, #settings-window #row-hint, #settings-window #footer-note {{
    color: {TEXT_MUTED}; font-size: 12px;
}}
#settings-window #card-title {{
    color: {TEXT_MUTED}; font-size: 11px; font-weight: 700; letter-spacing: 1px;
}}
#settings-card {{ background: {SETTINGS_CARD}; border: 1px solid {PANEL_BORDER}; border-radius: 12px; }}
#settings-card QLabel {{ background: transparent; }}
#row-separator {{ background: {PANEL_BORDER}; max-height: 1px; min-height: 1px; border: none; }}
#settings-window #row-label {{ font-weight: 600; }}
#settings-window #field-error {{ color: {DANGER}; font-size: 12px; }}
#settings-window #badge-ok {{ color: {SUCCESS}; font-size: 12px; font-weight: 600; }}
#settings-window #badge-missing {{ color: {TEXT_MUTED}; font-size: 12px; }}
#settings-window #footer-dirty {{ color: {ACCENT}; font-size: 12px; font-weight: 600; }}
#settings-window #about-title {{ font-size: 20px; font-weight: 700; }}
#settings-window a {{ color: {ACCENT}; }}
#settings-footer {{ background: {SETTINGS_SIDEBAR}; border-top: 1px solid {PANEL_BORDER}; }}

#settings-window QLineEdit, #settings-window QComboBox, #settings-window QAbstractSpinBox {{
    background: {SETTINGS_FIELD}; border: 1px solid {PANEL_BORDER}; border-radius: 7px;
    padding: 5px 9px; min-height: 20px; selection-background-color: {ACCENT}; selection-color: #111;
}}
#settings-window QLineEdit:focus, #settings-window QComboBox:focus, #settings-window QAbstractSpinBox:focus {{
    border-color: {ACCENT};
}}
#settings-window QLineEdit[invalid="true"] {{ border-color: {DANGER}; }}
#settings-window QLineEdit:read-only {{ color: {TEXT_MUTED}; }}
#settings-window QComboBox::drop-down {{ border: none; width: 22px; }}
#settings-window QComboBox::down-arrow {{ image: url({down_arrow}); width: 14px; height: 14px; }}
#settings-window QComboBox QAbstractItemView {{
    background: {SETTINGS_FIELD}; border: 1px solid {PANEL_BORDER}; selection-background-color: {SETTINGS_CARD};
    selection-color: {ACCENT}; outline: none;
}}
#settings-window QAbstractSpinBox::up-button, #settings-window QAbstractSpinBox::down-button {{
    border: none; width: 18px; background: transparent;
}}
#settings-window QAbstractSpinBox::up-arrow {{ image: url({up_arrow}); width: 10px; height: 10px; }}
#settings-window QAbstractSpinBox::down-arrow {{ image: url({down_arrow}); width: 10px; height: 10px; }}
#settings-window QSlider::groove:horizontal {{ height: 4px; background: {SETTINGS_FIELD}; border-radius: 2px; }}
#settings-window QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 2px; }}
#settings-window QSlider::handle:horizontal {{
    background: {TEXT}; width: 14px; height: 14px; margin: -6px 0; border-radius: 7px;
}}
#settings-window QPushButton {{
    background: {SETTINGS_FIELD}; border: 1px solid {PANEL_BORDER}; border-radius: 7px; padding: 6px 14px;
}}
#settings-window QPushButton:hover {{ border-color: {TEXT_MUTED}; }}
#settings-window QPushButton:disabled {{ color: #5c6273; }}
#settings-window QPushButton#primary {{ background: {ACCENT}; color: #14161d; border: none; font-weight: 700; }}
#settings-window QPushButton#primary:disabled {{ background: {SETTINGS_FIELD}; color: #5c6273; }}
#settings-window QPushButton#danger {{ color: {DANGER}; }}
#settings-window QPushButton#danger:hover {{ border-color: {DANGER}; }}
#settings-window QListWidget#profile-list {{
    background: {SETTINGS_FIELD}; border: 1px solid {PANEL_BORDER}; border-radius: 8px; outline: none; padding: 4px;
}}
#settings-window QListWidget#profile-list::item {{ padding: 7px 10px; border-radius: 6px; }}
#settings-window QListWidget#profile-list::item:selected {{ background: {SETTINGS_CARD}; color: {ACCENT}; }}
#settings-window QScrollBar:vertical {{ background: transparent; width: 10px; }}
#settings-window QScrollBar::handle:vertical {{ background: {PANEL_BORDER}; border-radius: 5px; min-height: 30px; }}
#settings-window QScrollBar::add-line, #settings-window QScrollBar::sub-line {{ height: 0; }}
"""
