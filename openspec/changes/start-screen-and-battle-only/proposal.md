## Why

- La detección automática muestra la ficha en cuanto lee un nombre de Pokémon estable en una región, así que también salta fuera del combate: en la Pokédex o en los datos de tus Pokémon. En el registro de un usuario, de 1081 detecciones automáticas, 820 tenían el rival con su nivel; muchas de las demás eran nombres sueltos sin nivel (p. ej. solo en la región del 2.º rival), típicos de esas pantallas.
- Al abrir la app no hay nada que ver: hay que ir a la bandeja para elegir la ventana del emulador y el perfil. El usuario quiere una pantalla de inicio para dejarlo todo listo antes de jugar.

## What Changes

- En la detección automática, un rival solo cuenta si se lee su nivel junto al nombre, como en la barra de vida del combate. Las regiones de los presets ya incluyen el nivel. Nueva opción `detection.require_level` (por defecto `true`), en Ajustes › Reconocimiento como «Solo en la pantalla de combate», para quien calibró regiones sin el nivel. El reconocimiento manual (Ctrl+Alt+P) no cambia.
- Pantalla de inicio al abrir la app (`ui/start.py`): ventana del emulador (con botón para actualizar la lista), perfil (con «Nuevo perfil con un preset…»), modo de la ficha y detección automática, y «Empezar». La ventana se aplica al momento, como en Ajustes. Nueva opción `interface.start_screen` (por defecto `true`), en la propia pantalla («Mostrar al abrir la app») y en Ajustes › General.
- La lista de ventanas de Ajustes y la de la pantalla de inicio comparten `fill_window_combo`.

## Capabilities

### Modified Capabilities
- `battle-detection`: la ficha automática exige el nivel del rival (si la opción está activa).
- `battle-overlay`: pantalla de inicio.
- `app-settings`: dos opciones nuevas (pantalla de inicio y solo en la pantalla de combate).

## Impact

- Código: `core/detection.py` (`with_levels_only`), `core/config.py`, `app.py`, `ui/start.py` (nuevo), `ui/settings.py`, `i18n/en_menus.py`, `tools/make_guide_screenshots.py`.
- Tests: `tests/test_detection.py`, `tests/test_app.py` (los fotogramas sintéticos sin nivel desactivan la opción), `tests/test_english_ui.py`.
- `config.toml`: dos claves nuevas con valor por defecto (compatible con los archivos anteriores).
- **Guía de uso: sí.** Nuevo apartado «La pantalla de inicio» con su captura, «Empieza en 3 minutos» la usa, opciones nuevas en «Resto de ajustes» y entrada en «La ficha no aparece» (es/en); capturas regeneradas. También README (es/en) y CHANGELOG.
