## Why

Hoy la ficha solo aparece cuando BattleLens lee un nombre en la pantalla de combate. Para consultar un Pokémon en cualquier otro momento (planear un equipo, mirar el rival del próximo gimnasio, comprobar una debilidad) hay que salir a una web. Un buscador con atajo global da esa consulta sin dejar el juego.

## What Changes

- Nuevo atajo global «Buscar Pokémon» (por defecto `Ctrl+Alt+B`, configurable en `hotkeys.search` y en *Ajustes → Atajos*).
- El atajo abre un buscador pequeño y siempre encima: un campo de texto que sugiere nombres mientras se escribe. Al pulsar Enter se muestra la ficha de ese Pokémon.
- El nombre se resuelve con el mismo emparejador aproximado del OCR, así que acepta nombres en cualquier idioma del índice, sin tildes y con pequeñas erratas.
- La ficha usa el juego del perfil activo; sin perfil, la generación actual. Aparece sobre la ventana del juego si la hay y, si no, en la pantalla principal.
- La ficha buscada admite cambiar de forma y de modo como la de combate, pero no se publica en la ficha del stream (es una consulta privada).
- Opción «Buscar Pokémon…» en la bandeja, con la pista del atajo.

## Capabilities

### New Capabilities
- `pokemon-search`: buscador de Pokémon con atajo global y ficha a demanda fuera del combate.

### Modified Capabilities
<!-- Ninguna: el atajo nuevo se define en pokemon-search; la ficha del stream solo cambia para fichas de combate, que siguen igual. -->

## Impact

- Código: `core/config.py` (`hotkey_search`), `app.py` (atajo, `search_pokemon`, la ficha buscada no se publica en el stream), `ui/search.py` (diálogo nuevo), `ui/settings.py` (campo del atajo), `ui/tray.py` (opción de menú), catálogos de `i18n`.
- Tests: config, diálogo de búsqueda y flujo en `Controller`.
- **Guía de uso (`site/guide.html`): sí la afecta.** Hay que tocar los apartados de atajos (tabla y Ajustes → Atajos) y el menú de la bandeja, y añadir un apartado «Buscar un Pokémon» con una captura nueva del buscador en `tools/make_guide_screenshots.py`. Se regeneran las capturas de Ajustes → Atajos y de la bandeja.
- README.md, README.es.md y CHANGELOG.md (cambio visible para el usuario).
