"""Colores y textos compartidos por la interfaz."""

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
    "hp": "PS",
    "attack": "Ataque",
    "defense": "Defensa",
    "special_attack": "At. Esp.",
    "special_defense": "Def. Esp.",
    "speed": "Velocidad",
}
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
