## Why

Al probar la 0.6 salieron dos huecos. Recalibrar un perfil solo se descubre con `Ctrl+Alt+C`: la bandeja únicamente ofrece crear uno con un preset. Y la tabla de tipos resalta solo al rival, aunque el perfil lea tu Pokémon. Lo útil en combate es ver a la vez lo que tus tipos le hacen a los suyos.

## What Changes

- Bandeja: opción **«Modificar o crear perfil…»**, con la pista del atajo, que hace lo mismo que `Ctrl+Alt+C`: recalibrar una región del perfil activo o crear uno nuevo.
- Tabla de tipos: si la ficha lee tu Pokémon, sus tipos se resaltan como **filas** (atacante) con otro color, además de las **columnas** del rival (defensor). La casilla de cruce, tu ataque de tu tipo contra el rival, queda marcada. Una leyenda en la cabecera indica qué color es de quién.

## Capabilities

### New Capabilities
<!-- Ninguna. -->

### Modified Capabilities
- `type-chart`: el resaltado incluye los tipos del Pokémon propio como filas.
- `game-profiles`: opción de bandeja para modificar o crear un perfil.

## Impact

- Código: `ui/tray.py` (acción y señal), `app.py` (conexión, resaltado del Pokémon propio), `ui/type_chart.py` (filas resaltadas, cruce y leyenda), catálogos de `i18n`.
- Tests: acción de bandeja → `calibrate`; resaltado de filas propias y su limpieza.
- **Guía de uso (`site/guide.html`): sí la afecta.** Hay que tocar el menú de la bandeja (opción nueva y captura) y la tabla de tipos (cómo leer filas y columnas resaltadas, con captura regenerada).
- CHANGELOG.md, README y portada.
