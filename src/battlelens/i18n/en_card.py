"""Catálogo inglés: card (add-english-ui D2). Clave: texto en español; valor: inglés."""

EN: dict[str, str] = {
    # ---- cabecera y captura (ui/overlay.py, stream/payload.py) ----
    "Nv. {level}": "Lv. {level}",
    "Nv. ?": "Lv. ?",
    "Captura: {rate} · {difficulty}": "Catch rate: {rate} · {difficulty}",
    # Dificultad de captura (core/pokedex.py; claves internas en español)
    "Fácil": "Easy",
    "Media": "Medium",
    "Difícil": "Hard",
    "Muy difícil": "Very hard",
    # ---- contra tu Pokémon ----
    "Contra tu {name}": "Against your {name}",
    "Ventaja": "Advantage",
    "Neutral": "Neutral",
    "Desventaja": "Disadvantage",
    "Tú": "You",
    "Él": "Them",
    "Velocidad: {verdict} (tú {own_min}-{own_max}, él {rival_min}-{rival_max})":
        "Speed: {verdict} (you {own_min}-{own_max}, them {rival_min}-{rival_max})",
    "Eres más rápido": "You are faster",
    "Es más rápido": "It is faster",
    "Depende de IVs/EVs": "Depends on IVs/EVs",
    # ---- tus movimientos ----
    "Tus movimientos": "Your moves",
    "Tus movimientos (probables)": "Your moves (likely)",
    "Estado": "Status",
    # ---- eficacia ----
    "Eficacias": "Type matchups",
    "Debilidades": "Weaknesses",
    "Resistencias": "Resistances",
    "Inmunidades": "Immunities",
    # Notas de habilidades (core/card_text.py, core/abilities.py)
    "{type}: {mult} por {abilities}": "{type}: {mult} due to {abilities}",
    "{type}: {mult} si tiene {abilities}": "{type}: {mult} if it has {abilities}",
    "{abilities}: {detail}": "{abilities}: {detail}",
    "Si tiene {abilities}: {detail}": "If it has {abilities}: {detail}",
    "Solo le afectan los ataques supereficaces": "Only super-effective moves hit it",
    "Los supereficaces le hacen ×0,75": "Super-effective moves deal ×0.75",
    # ---- estadísticas (ui/theme.py STAT_LABELS) ----
    "Estadísticas base": "Base stats",
    "Estadísticas base · rango a su nivel": "Base stats · range at its level",
    "Total estadísticas base: {total}": "Base stat total: {total}",
    "Total": "Total",
    "PS": "HP",
    "Ataque": "Attack",
    "Defensa": "Defense",
    "Especial": "Special",  # estadística de la Gen 1 y categoría de movimiento
    "At. Esp.": "Sp. Atk",
    "Def. Esp.": "Sp. Def",
    "Velocidad": "Speed",
    # ---- habilidades y movimientos probables ----
    "Habilidades": "Abilities",
    "(oculta)": "(hidden)",
    "Movimientos probables": "Likely moves",
    # Categoría abreviada de los movimientos (improve-card-visuals D8)
    "Fís.": "Phys.",
    "Esp.": "Spec.",
    "Est.": "Status",
    "Nivel no leído: recalibra la región del rival incluyendo el nivel para ver sus movimientos.":
        "Level not read: recalibrate the opponent region including the level to see its moves.",
    "Sin datos de movimientos para este Pokémon.": "No move data for this Pokémon.",
    "Falta learnsets.json: genera los datos con tools/build_dataset.py":
        "learnsets.json is missing: generate the data with tools/build_dataset.py",
    # ---- entrenamiento ----
    "Entrenamiento": "Training",
    "EVs que da: {evs}": "EV yield: {evs}",
    "Peso: {weight} kg (Patada Baja/Hierba Lazo: {power})": "Weight: {weight} kg (Low Kick/Grass Knot: {power})",
    "Atacante físico": "Physical attacker",
    "Atacante especial": "Special attacker",
    "Atacante mixto": "Mixed attacker",
    "defensivo": "defensive",
    "rápido": "fast",
    # ---- evolución y otras formas ----
    "Evolución": "Evolution",
    "Otras formas": "Other forms",
    "{hotkey}: cambiar de forma": "{hotkey}: switch form",
    # ---- no reconocido ----
    "No reconocido": "Not recognized",
    "(vacío)": "(empty)",
    "Texto leído: {text}": "Text read: {text}",
    "Si el texto no es el nombre del rival, recalibra la región del rival en Ajustes › Perfiles.":
        "If the text is not the opponent's name, recalibrate the opponent region in Settings › Profiles.",
    "No se encuentra el dataset ({path}). Genéralo con: uv run python tools/build_dataset.py":
        "Dataset not found ({path}). Generate it with: uv run python tools/build_dataset.py",
}
