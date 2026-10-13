## Why

«Contra tu X» compara tipos, es decir, ataques con STAB. Pero la decisión real de cada turno es **qué movimiento usar**, y tu Pokémon suele llevar movimientos de otros tipos (MT, tutores). La ficha no sabe qué movimientos tienes.

## What Changes

- **Nueva región opcional del perfil: «menú de ataques».** Se calibra desde «Regiones del perfil», sobre los 4 movimientos que aparecen al elegir «Luchar».
- **Lectura del menú:** la app vigila esa región por separado de la detección del combate (no la incluye en su huella). Cuando la imagen se estabiliza, la lee con el OCR y busca nombres de movimiento en los 5 idiomas. Si encuentra al menos 2, son los movimientos de tu Pokémon reconocido. También se lee al reconocer a mano.
- **Memoria por especie:** los movimientos leídos se guardan por perfil y especie (`moves.json`), así que la próxima vez que salga ese Pokémon ya se conocen sin abrir el menú.
- **Respaldo:** si todavía no se han leído, se usan los movimientos probables de tu Pokémon según su nivel (los 4 últimos que aprende), marcados como «probables».
- **Apartado «Tus movimientos»** en cada tarjeta, en ambos modos: tipo, nombre y multiplicador contra ese rival, aplicando sus habilidades seguras y marcando con «*» las posibles. Los de estado se indican como «Estado».
- El catálogo de movimientos (`learnsets.json`) pasa a incluir **todos** los movimientos, no solo los que se aprenden por nivel.

## Capabilities

### New Capabilities
- `own-moves`: lectura del menú de ataques, coincidencia con el catálogo de movimientos, memoria por especie, respaldo con los probables y apartado «Tus movimientos».

### Modified Capabilities
- `game-profiles`: nueva región opcional «menú de ataques».
- `pokemon-data`: el catálogo de movimientos incluye todos los movimientos.

## Impact

- **Código:** nuevo `core/moves.py` (coincidencia y memoria), `core/profiles.py` (`moves_region`), `core/learnsets.py` (búsqueda por identificador y catálogo completo), `core/detection.py` (`RegionWatcher`), `pipeline.py`, `app.py`, `ui/tray.py`, `ui/overlay.py` y `tools/build_dataset.py`.
- **Datos:** `learnsets.json` crece unos 100 KB, y el directorio de datos guarda `moves.json`.
- **Rendimiento:** un OCR más (2-3 variantes) cuando cambia el menú de ataques. No afecta a la detección del rival.
- **Compatibilidad:** los perfiles existentes siguen igual. El apartado aparece con la región de tu Pokémon, aunque no se calibre el menú (usa los probables).
