## Why

No todos usan BattleLens igual. Quien juega la aventura o quiere capturarlos todos necesita una ficha rápida y pequeña que tape poco el juego: tipos, debilidades y lo fácil que es capturarlo. Quien va a por los combates quiere más: qué movimientos lleva el rival, sus estadísticas reales a su nivel, quién ataca primero y qué habilidades le cambian las debilidades.

## What Changes

- **Dos modos de ficha:** Normal (compacto, por defecto) y Competitivo (completo y ampliado). Se cambia desde la bandeja, con `Ctrl+Alt+M` o desde Ajustes, y la ficha visible se vuelve a dibujar al momento.
- **Lectura del nivel** del rival y de tu Pokémon a partir del texto que ya lee el OCR.
- El modo Competitivo añade:
  - movimientos probables (los 4 últimos aprendidos hasta su nivel en ese juego, con su eficacia contra ti);
  - estadísticas reales mínimas y máximas a su nivel;
  - «¿quién es más rápido?»;
  - habilidades con su descripción visible y los cambios de eficacia que provocan (Levitación → Tierra ×0…);
  - datos de entrenamiento (EVs que da, peso con la potencia de Patada Baja y Hierba Lazo, perfil de estadísticas).
- El dataset incorpora peso, altura, EVs, movimientos y la lista de movimientos que aprende cada Pokémon en cada juego (en un `learnsets.json` aparte, de unos 0,7 MB, que se carga solo al usarlo).

## Capabilities

### New Capabilities
- `display-modes`: modos Normal y Competitivo, su contenido y cómo se cambia de uno a otro.
- `level-reading`: extracción del nivel a partir de las lecturas de OCR.
- `competitive-data`: movimientos probables, estadísticas a su nivel, velocidad, efectos de habilidades y datos de entrenamiento.

### Modified Capabilities
- `pokemon-data`: el dataset incluye peso, altura, EVs, movimientos y `learnsets.json`, que se carga solo cuando hace falta.
- `battle-overlay`: el contenido de la tarjeta depende del modo; nuevo atajo y submenú para cambiar de modo.
- `app-settings`: modo de la ficha y atajo para cambiarlo.

## Impact

- **Código:** `tools/build_dataset.py`, nuevo `core/competitive.py` (estadísticas, velocidad, habilidades, entrenamiento), `core/learnsets.py` (carga diferida y movimientos probables), `core/normalize.py` (nivel), `pipeline.py` (niveles en el resultado), `ui/overlay.py` (tarjeta según el modo), `ui/tray.py`, `ui/settings.py`, `core/config.py`, `app.py`.
- **Datos:** `pokedex.json` crece poco (peso, altura, EVs); `learnsets.json` nuevo (~0,7 MB).
- **Cambio visible:** la ficha por defecto pasa a ser más compacta que la actual; la ficha completa está en el modo Competitivo.
