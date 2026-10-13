## Why

Los tipos y la tabla de eficacias ya siguen la generación del juego, pero las estadísticas no. En Rojo/Azul la ficha muestra At. Esp. y Def. Esp. aunque en la Gen 1 había una sola estadística «Especial», y en Blanco/Negro Pikachu aparece con Defensa 40 cuando entonces tenía 30. Los rangos a su nivel usan siempre la fórmula de la Gen 3, que no vale para la Gen 1-2 (DVs y experiencia de estadística), Let's Go (AVs y amistad) ni Leyendas: Arceus (niveles de esfuerzo). Son dos limitaciones documentadas en el README.

## What Changes

- **Estadísticas base de cada generación:** el dataset incluye las estadísticas base anteriores de cada Pokémon (`pokemon_stats_past` de PokéAPI), y la vista del juego usa las de su generación.
- **Gen 1:** la ficha muestra **Especial** en lugar de At. Esp. y Def. Esp., y el total suma 5 estadísticas.
- **Rangos a su nivel con la fórmula del juego:**
  - Gen 1-2: DV 0-15 y experiencia de estadística 0-65 535, sin naturaleza.
  - Let's Go Pikachu/Eevee: IV 0-31, naturaleza, multiplicador de amistad (×1,0-×1,1) y AVs. Los Pokémon rivales no tienen AVs, así que solo se suman en los de tu Pokémon (0-200).
  - Leyendas: Arceus: niveles de esfuerzo 0-10 y naturaleza.
  - El resto, como hasta ahora (Gen 3 en adelante).
- La comparación de velocidad y el perfil de estadísticas usan estos valores.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `pokemon-data`: estadísticas base de generaciones anteriores en el dataset y en la vista del juego.
- `competitive-data`: rangos a su nivel con la fórmula del juego del perfil.

## Impact

- **Código:** `tools/build_dataset.py`, `core/pokedex.py` (`stats_in`, orden de estadísticas de la vista), `core/competitive.py` (fórmulas), `ui/overlay.py` y `ui/theme.py` (etiqueta «Especial»).
- **Datos:** se regenera `pokedex.json` (`past_stats`, unos 230 registros).
- **Compatibilidad:** sin cambios de configuración ni de perfiles.
