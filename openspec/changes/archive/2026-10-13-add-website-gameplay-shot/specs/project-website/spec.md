## MODIFIED Requirements

### Requirement: Capturas reproducibles
El proyecto SHALL incluir `tools/make_site_screenshots.py`, que genera las capturas de `site/assets/` a doble resolución a partir de la interfaz real de BattleLens. La única imagen de un juego permitida es la captura de una partida real (`site/assets/gameplay.jpg`), que MUST mostrar solo la imagen del juego (sin la interfaz del emulador) e ir acompañada del crédito del juego en ambos idiomas.

#### Scenario: Regenerar capturas
- **WHEN** se ejecuta `uv run python tools/make_site_screenshots.py`
- **THEN** se generan `card-normal.png`, `card-competitive.png` y `card-double.png` en `site/assets/`

#### Scenario: Captura de partida
- **WHEN** se ejecuta `uv run python tools/make_gameplay_shot.py` con el emulador en un combate
- **THEN** se genera `site/assets/gameplay.jpg` con la imagen del juego recortada (sin barra de menús, barra de estado ni franjas negras del emulador) y la ficha real de BattleLens superpuesta, reconocida con su pipeline

#### Scenario: Crédito visible
- **WHEN** un visitante ve la captura de la partida
- **THEN** debajo aparece el crédito de Pokémon Espada a Nintendo, Creatures Inc. y GAME FREAK inc.
