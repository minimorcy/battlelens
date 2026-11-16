## Why

En la maqueta del rediseño (`improve-card-visuals`), una imagen pequeña del Pokémon en la cabecera permite reconocerlo de un vistazo y separa mejor las tarjetas en los combates dobles. Los sprites son propiedad de Nintendo/Game Freak y la licencia BSD-3 de PokéAPI no los cubre, así que no podemos incluirlos en el repo ni en el instalador. La app los descargará bajo demanda desde el repositorio público de sprites de PokéAPI y los guardará en la carpeta de datos del usuario.

## What Changes

- La cabecera de la ficha muestra a la izquierda el sprite del Pokémon (de la forma mostrada), recortado a su contorno visible y centrado en un recuadro de 60 px.
- El sprite se descarga la primera vez que aparece cada Pokémon, en segundo plano, y se guarda en `%APPDATA%\BattleLens\sprites\`. La ficha se muestra en el acto y la imagen aparece en cuanto llega.
- Sin conexión, o si la descarga falla, la cabecera se muestra sin imagen y el resto de la ficha no cambia.
- Opción `overlay.sprites` (activada por defecto) en `config.toml` y en Ajustes, que explica que las imágenes se descargan de Internet.
- El dataset guarda el número de Pokémon de PokéAPI de cada especie y forma, que es la clave de los sprites (p. ej. Zigzagoon de Galar = 10174).
- La ficha del stream muestra la misma imagen, servida por el servidor local desde la caché.
- Aviso en el README sobre el origen y la propiedad de las imágenes.

## Capabilities

### New Capabilities
- `pokemon-sprites`: descarga, recorte y caché de los sprites.

### Modified Capabilities
- `battle-overlay`: imagen en la cabecera de la ficha.
- `app-settings`: opción para activar o desactivar las imágenes.
- `stream-mode`: imagen en la ficha del stream y ruta para servirla.
- `pokemon-data`: número de Pokémon de PokéAPI por especie y forma.

## Impact

- Nuevo `core/sprites.py`; cambios en `ui/overlay.py`, `ui/settings.py`, `core/config.py`, `stream/server.py`, `stream/payload.py`, `stream/static/card.js`, `tools/build_dataset.py` y `data/pokedex.json` (regenerado).
- Depende de `improve-card-visuals` (cabecera nueva).
- Red: peticiones HTTPS a `raw.githubusercontent.com`, una por Pokémon nuevo, con el mismo `User-Agent` que la comprobación de actualizaciones.
