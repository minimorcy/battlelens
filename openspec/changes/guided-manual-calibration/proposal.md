## Why

«Calibrar a mano» solo pedía la región del nombre del rival. La de tu Pokémon y la del menú de ataques había que añadirlas después, una a una, desde Ajustes › Perfiles, y el usuario no lo descubre: cree que la calibración a mano no permite medirlas. Además, el menú de ataques casi nunca está a la vista en la captura con la que se empieza.

## What Changes

- La calibración a mano de un perfil nuevo es una secuencia de tres pasos sobre la misma captura: rival (obligatorio), tu Pokémon y menú de ataques (opcionales, Esc o «Saltar» los saltan). Después se piden el nombre y el juego.
- El diálogo de calibración tiene «Volver a capturar» para cambiar la imagen por una captura nueva del emulador (p. ej. tras abrir el menú de Luchar). También al recalibrar una región desde Ajustes.
- Una región dibujada sobre una captura con otro tamaño de ventana se lleva a la imagen del juego de la primera captura (`anchor-regions-to-game`).

## Capabilities

### Modified Capabilities
- `game-profiles`: la calibración interactiva pide también las regiones opcionales y permite volver a capturar.

## Impact

- Código: `ui/calibrator.py`, `app.py`, `i18n/en_menus.py`.
- Tests: `tests/test_ui.py`, `tests/test_app.py`.
- **Guía de uso: sí.** Se actualizan los pasos de «Calibrar a mano» (es/en). La captura de calibración no cambia (primer paso). También `README.md`, `README.es.md` y `CHANGELOG.md`.
