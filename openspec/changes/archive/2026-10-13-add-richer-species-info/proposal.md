## Why

Durante el combate surgen más preguntas que los tipos: ¿merece la pena intentar capturarlo?, ¿qué hace exactamente su habilidad?, ¿en qué evoluciona y cuándo? Ahora hay que salir del juego para buscarlo. Los datos ya están en PokéAPI.

## What Changes

- **Ratio de captura** con su dificultad (Fácil / Media / Difícil / Muy difícil).
- **Descripción de cada habilidad** al pasar el ratón por ella, en el idioma de la ficha.
- **Cadena evolutiva** con la condición de cada evolución (nivel, piedra, intercambio, amistad…), filtrada por la generación del juego.
- El dataset incorpora estos datos (ratio de captura, evoluciones, descripciones de habilidades y nombres de objetos de evolución).

## Capabilities

### New Capabilities
<!-- Ninguna. -->

### Modified Capabilities
- `pokemon-data`: el dataset incluye ratio de captura, evoluciones, descripciones de habilidades y objetos; se añaden la cadena evolutiva según el juego y la dificultad de captura.
- `battle-overlay`: la tarjeta muestra el ratio de captura, la evolución y la descripción de las habilidades.

## Impact

- **Código:** `tools/build_dataset.py` (CSV: pokemon_evolution, evolution_triggers, items, item_names, ability_flavor_text), `core/pokedex.py` (evolución, captura, descripciones), `ui/overlay.py`.
- **Datos:** `pokedex.json` crece (unos 150-250 KB por las descripciones).
- **Sin dependencias nuevas.**
