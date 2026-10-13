## Context

La tarjeta actual es una ficha completa única. El OCR ya lee el nivel cuando la región lo incluye (p. ej. «Stufful Nv. 10» o «Stufiul 10» en Espada), pero la normalización lo elimina para comparar nombres. PokéAPI ofrece `pokemon_moves` (161 805 filas de aprendizaje por nivel), `moves`, `move_names`, `pokemon.weight` (en hectogramos), `pokemon.height` (en decímetros) y `pokemon_stats.effort` (EVs).

## Goals / Non-Goals

**Goals:**
- Ficha Normal pequeña y Competitiva rica, intercambiables al momento.
- Datos competitivos correctos para la Gen 3 en adelante.
- Sin coste de arranque por los datos nuevos.

**Non-Goals:**
- Movimientos de MT, tutor o huevo, y movimientos reales del rival (no se ven en pantalla).
- Fórmulas de las Gen 1-2 (DVs y Stat Exp.) y sistemas de Let's Go / Leyendas (AVs, niveles de esfuerzo). Se usa la fórmula de la Gen 3+ y se documenta.
- Cálculo de daño completo (requiere estadísticas exactas, objetos, clima…).

## Decisions

### D1. Una tarjeta, dos niveles de detalle
`Overlay` recibe `mode` y construye secciones según una tabla del modo: Normal incluye `header, types, capture, matchup, weaknesses, immunities, evolution, stat_total, other_forms`; Competitivo incluye todas, más `level, resistances, stats_with_ranges, abilities_detailed, moves, training`. El ancho de la tarjeta es de 300 px en Normal y 360 px en Competitivo. El controlador guarda la última batalla mostrada (clave, juego y niveles) para volver a dibujarla al cambiar de modo sin repetir el OCR.

### D2. Nivel extraído de todas las lecturas
`extract_level(readings)` aplica primero el patrón con prefijo («Nv», «Lv», «N», «L», «:L») a todas las lecturas, empezando por la de mejor coincidencia, y después un número suelto al final. Solo acepta 1-100. `read_crop` ya guarda todas las lecturas, así que no hace falta más OCR. El nivel no forma parte de la clave de la detección automática, para que el ruido del OCR no provoque parpadeos. Se actualiza en cada reconocimiento.

### D3. `learnsets.json` deduplicado y de carga diferida
Formato: `{"moves": {id: {...}}, "sets": [[[nivel, id_mov], ...], ...], "pokemon": {identificador: {grupo_de_versiones: índice}}}`. Las listas idénticas entre juegos se guardan una sola vez (4615 únicas, unos 0,7 MB). `Learnsets.load()` se llama la primera vez en modo Competitivo y se cachea. Las formas regionales usan su propio identificador de Pokémon (`zigzagoon-galar`).
Elección del juego: primero el grupo de versiones del perfil; si no tiene datos para esa especie, el de orden más alto dentro de su generación; y si no, el más reciente con datos.

### D4. Movimientos probables = últimos 4 distintos con nivel ≤ L
Es la regla que usan los juegos para los Pokémon salvajes y la mayoría de entrenadores sin movimientos personalizados. Se presenta como «probables», no como seguros.

### D5. Fórmulas (Gen 3+)
PS = ⌊(2B + IV + ⌊EV/4⌋)·L/100⌋ + L + 10; resto = ⌊(⌊(2B + IV + ⌊EV/4⌋)·L/100⌋ + 5)·N⌋. Mínimo: IV 0, EV 0, N 0,9 (PS sin N). Máximo: IV 31, EV 252, N 1,1. Shedinja: PS 1. La velocidad se compara entre los dos rangos.

### D6. Habilidades que cambian la eficacia: tabla propia
PokéAPI no da los efectos de forma estructurada, así que `core/competitive.py` mantiene una tabla de unas 20 habilidades conocidas: multiplicadores por tipo o notas especiales como Superguarda y Filtro. Como no se sabe qué habilidad tiene el rival, se anota en cada una.

### D7. Modo en la configuración
`overlay.mode = "normal" | "competitive"` y `hotkeys.toggle_mode = "Ctrl+Alt+M"`. Cambiar de modo desde la bandeja o con el atajo llama a `save_config`, de modo que el `config.toml` se reescribe con la plantilla comentada, como desde Ajustes.

## Risks / Trade-offs

- [Nivel no leído si la región es muy ajustada] → La ficha competitiva lo dice y sugiere recalibrar incluyendo el nivel. El modo Normal no lo necesita.
- [Movimientos personalizados de líderes, rivales y equipos competitivos] → Se presentan como «probables» y se documenta.
- [Fórmula de la Gen 3+ en juegos antiguos] → Se documenta como limitación.
- [Ficha competitiva alta] → 360 px de ancho y textos compactos. Se puede arrastrar y ocultar.

## Migration Plan

Los `config.toml` sin `overlay.mode` ni `hotkeys.toggle_mode` usan los valores por defecto (Normal, `Ctrl+Alt+M`). La ficha por defecto pasa a ser la compacta; quien prefiera la completa elige Competitivo una vez y queda guardado.

## Open Questions

Ninguna.
