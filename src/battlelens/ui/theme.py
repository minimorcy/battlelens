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
