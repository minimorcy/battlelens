## Context

`Species.stats` y `Form.stats` son las estadísticas actuales, con 6 claves fijas (`STAT_ORDER`). `competitive.stat_ranges` aplica siempre la fórmula de la Gen 3. La interfaz recorre `STAT_ORDER`. PokéAPI publica `pokemon_stats_past.csv` (`pokemon_id, generation_id, stat_id, base_stat`), donde `generation_id` es la última generación con ese valor (la misma convención que `pokemon_types_past`), y el `stat_id` 9 es «special».

## Goals / Non-Goals

**Goals:**
- Valores base y rangos fieles al juego del perfil.
- Ningún cambio para la Gen 3 en adelante salvo las estadísticas base que cambiaron (Gen 6 y otras).

**Non-Goals:**
- Experiencia de estadística, AVs o niveles de esfuerzo reales del rival (no se ven en pantalla).
- Fórmulas de Leyendas Z-A y Champions: se usa la de la Gen 3 en adelante hasta que haya una fuente fiable.
- Mecánicas de la Gen 1 como los críticos o el DV de PS derivado: el rango ya cubre DV 0-15.

## Decisions

### D1. `past_stats` en el dataset
`build_dataset.py` agrupa `pokemon_stats_past.csv` por (Pokémon, generación) y produce `past_stats: [{until_generation, stats: {clave: valor}}]`. El `stat_id` 9 se traduce a `special`. Se añade `pokemon_stats_past` a `CSV_FILES`.

### D2. `stats_in(generation)`
Por cada clave, se toma la entrada con el menor `until_generation >= generation`, como en `types_in`. En la Gen 1, si hay `special`, se quitan `special_attack` y `special_defense` y queda `special`. Si una especie no tiene Especial (no debería pasar en la Gen 1), se usa At. Esp. como Especial. `Pokedex.view` usa `stats_in` en la especie y en la forma.

### D3. Orden de estadísticas de la vista
`STAT_DISPLAY_ORDER = ("hp", "attack", "defense", "special", "special_attack", "special_defense", "speed")`. `SpeciesView.stat_keys` devuelve las claves presentes en ese orden, y la interfaz (filas de estadísticas y EVs) lo recorre en lugar de `STAT_ORDER`. `theme.STAT_LABELS` añade `"special": "Especial"`.

### D4. Fórmula por juego
`competitive.stat_formula(game_id, generation) -> "gen12" | "lets-go" | "legends-arceus" | "modern"`. `stat_ranges(stats, level, pokemon=None, formula="modern", own=False)` recorre las claves de `stats`.
- `gen12`: `core = ⌊((B + DV) × 2 + ⌊⌈√EXP⌉ / 4⌋) × L / 100⌋`. El término de experiencia vale 0 (mín.) o 64 (máx., ⌈√65 535⌉ = 256).
- `lets-go`: amistad ×1,0 o ×1,1, y AV de 0 a 200 solo si `own` (los rivales no tienen AVs).
- `legends-arceus`: aritmética entera para los términos del nivel (`(L + 50) × B / 75` y `(L + 100) × B / 100`), y `√Base` en coma flotante para el bonus de nivel de esfuerzo.
- `modern`: la fórmula actual.

Se toma el redondeo hacia abajo en cada paso según Pokébip y Bulbapedia. Si se detecta una diferencia de ±1 en el juego real, se ajusta. Se acepta ese margen porque la ficha da un rango orientativo, no un valor exacto.

*Alternativa descartada:* restringir los rangos de Let's Go y Arceus a los valores habituales de un salvaje (por ejemplo, NE 0-3). Necesita datos que no tenemos para entrenadores y alfas.

### D5. Dónde se elige la fórmula
`SpeciesView` ya tiene `game_id` y `generation`. Se añade `competitive.view_ranges(view, level, own=False)`, que elige la fórmula y llama a `stat_ranges`. El overlay la usa para el rival y para tu velocidad (`own=True`). `stat_profile` usa `special` cuando no hay At. Esp. ni Def. Esp.

## Risks / Trade-offs

- [Fórmulas de Let's Go y Arceus sin verificar en un juego real] → Están documentadas en la spec con sus fuentes. El test fija los valores calculados y `docs/manual-validation.md` añade una comprobación.
- [Máximos teóricos amplios en Arceus (NE 10)] → Es coherente con el criterio actual de mínimo/máximo teórico.

## Migration Plan

Se regenera el dataset. Sin `past_stats`, `stats_in` devuelve las estadísticas actuales.

## Open Questions

Ninguna.
