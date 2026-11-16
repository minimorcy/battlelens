## Why

Las etiquetas de tipo con texto ocupan mucho y cuesta leerlas de un vistazo en mitad del combate. Con el símbolo del tipo (la llama de Fuego, la gota de Agua) se reconoce antes y la ficha queda más compacta. Los iconos son propiedad de Nintendo/Game Freak, así que no se pueden incluir en el instalador: la app los descargará del repositorio público de sprites de PokéAPI, como plantea `add-pokemon-sprites`.

## What Changes

- Opción en Ajustes › Ficha para mostrar los tipos como **iconos** en vez de como etiquetas. Desactivada por defecto.
- Con la opción activa, los tipos salen como icono en todos los sitios de la ficha: cabecera, «Contra tu…», «Tus movimientos», Eficacias, Movimientos probables y Otras formas. También en la tabla de tipos y en la ficha del modo stream.
- Se usa el mismo juego de símbolos sin texto en todas las generaciones (los de Espada/Escudo, `sprites/types/generation-viii/sword-shield/small/<id>.png`). Los iconos de la 3.ª a la 7.ª generación solo son el nombre del tipo escrito en inglés, sin símbolo.
- Al activar la opción, los 18 iconos se descargan en segundo plano y se guardan en `%APPDATA%\BattleLens\type-icons\`. Hasta que están todos, o si la descarga falla, los tipos siguen saliendo como etiquetas.
- Aviso en el README sobre el origen y la propiedad de las imágenes.

## Capabilities

### New Capabilities
- `type-icons`: descarga, validación y caché de los iconos de tipo, y cuándo se usan.

### Modified Capabilities
- `app-settings`: opción para elegir etiquetas o iconos.
- `battle-overlay`: los tipos de la ficha se dibujan como icono si la opción está activa.
- `type-chart`: cabeceras de la tabla con iconos.
- `stream-mode`: iconos en la ficha del stream y ruta para servirlos desde la caché.

## Impact

- Nuevo `core/remote_images.py` (descarga validada a la caché), pensado para que `add-pokemon-sprites` lo reutilice. Cambios en `ui/overlay.py` (`_pill` y sus llamadas), `ui/type_chart.py`, `ui/settings.py`, `core/config.py`, `app.py`, `stream/server.py`, `stream/payload.py` y `stream/static/card.js`.
- Red: hasta 18 peticiones HTTPS a `raw.githubusercontent.com`, una sola vez, con el mismo `User-Agent` que la comprobación de actualizaciones.
- **Guía de uso** (`site/guide.html`, es/en): apartado de Ajustes › Ficha (opción nueva), descripción de la ficha y de la tabla de tipos, y una captura nueva de la ficha con iconos.
- README y CHANGELOG en los dos idiomas.
