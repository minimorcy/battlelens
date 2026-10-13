## Why

El usuario quiere que la web muestre BattleLens en una partida real, no solo la ficha aislada: se entiende mucho mejor qué hace al verla sobre el juego. Prefiere mostrar solo la imagen del juego, sin el emulador.

## What Changes

- Nueva sección «Así se ve en una partida» con una captura real de Pokémon Espada (combate contra un Machop salvaje) y la ficha que BattleLens genera para ella, con el crédito del juego.
- `tools/make_gameplay_shot.py`: captura el emulador, recorta solo la imagen del juego, reconoce rival y tu Pokémon con el pipeline real y compone la ficha.
- Se relaja el requisito de «sin imágenes de juegos» para permitir esta única captura, con crédito y sin interfaz del emulador.
- La imagen pasa a ser la vista previa al compartir la web (`og:image`).

## Capabilities

### New Capabilities
<!-- Ninguna. -->

### Modified Capabilities
- `project-website`: «Capturas reproducibles» admite la captura de partida con crédito.

## Impact

- `site/index.html`, `site/styles.css`, `site/assets/gameplay.jpg` (131 KB), `tools/make_gameplay_shot.py`, tests de la web.
- **Riesgo legal:** la imagen del juego es de Nintendo / Creatures / GAME FREAK. Se atribuye y no se muestra el emulador. Decisión del usuario.
