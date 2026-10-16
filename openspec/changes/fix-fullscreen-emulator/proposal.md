## Why

Con el emulador a pantalla completa la ficha quedaba detrás: el emulador también se pone por encima de todo y Windows lo deja delante al tomar el foco. Además, las regiones se guardan como fracciones del área cliente de la ventana, así que al pasar de pantalla completa a maximizada (con barra de menús y de estado, o con bandas negras distintas) la imagen del juego se mueve y las regiones dejan de caer sobre los nombres.

## What Changes

- La ficha se vuelve a poner por encima de todo (`HWND_TOPMOST`, sin activarse) al mostrarse y en cada comprobación de la detección automática, para ganar al emulador a pantalla completa.
- Los perfiles guardan dónde estaba la imagen del juego al medir las regiones (`game_area`). Al leer, se localiza la imagen del juego en la captura actual (una vez por tamaño de ventana) y las regiones se llevan a su nuevo sitio. Funciona con los juegos de proporción conocida (GB, GBA, GameCube, DS y Switch).
- Lo guardan los perfiles creados con un preset y los creados a mano para juegos de proporción conocida; al recalibrar una región con otra ventana, se guarda en su sitio respecto a la imagen original. Los perfiles anteriores (sin `game_area`) siguen como estaban.
- La pantalla completa **exclusiva** (p. ej. Eden con Vulkan) no deja dibujar ninguna ventana encima: se documenta en la guía (problemas y limitaciones) cómo pasar a ventana sin bordes.
- Ctrl+C en la consola vuelve a cerrar la app (el gancho de errores no controlados lo registraba como un error).
- La localización de la imagen deja de ser fiable con pantallas lisas (negro entre escenas, fundidos), para no recordar una posición falsa.

## Capabilities

### Modified Capabilities
- `battle-overlay`: la ficha queda por delante del emulador a pantalla completa.
- `game-profiles`: regiones ancladas a la imagen del juego.
- `game-presets`: la localización no es fiable en pantallas lisas.

## Impact

- Código: `ui/overlay.py`, `app.py`, `pipeline.py`, `core/profiles.py`, `core/presets.py`, `vision/viewport.py`.
- Tests: `tests/test_game_area.py`, `tests/test_ui.py`.
- Formato de `profiles.json`: campo opcional `game_area` (compatible con los perfiles anteriores).
- **Guía de uso: sí.** Se explica que con un perfil creado con un preset la ventana del emulador puede cambiar (pantalla completa, maximizada) y se añaden los problemas de pantalla completa (regiones que no coinciden y pantalla completa exclusiva) y su limitación (es/en). Las capturas no cambian.
