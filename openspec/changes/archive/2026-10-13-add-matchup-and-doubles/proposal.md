## Why

La ficha dice a qué es débil el rival, pero no si **tu** Pokémon le va bien. Esa es la pregunta real en cada turno: ¿lo cambio o ataco? Además, en los combates dobles (muy frecuentes en Espada/Escudo y en los juegos posteriores) solo se reconoce a uno de los dos rivales.

## What Changes

- El perfil admite dos regiones opcionales además del nombre del rival: **nombre del 2.º rival** (combates dobles) y **nombre de tu Pokémon**.
- Se calibran desde la bandeja (submenú «Regiones del perfil»), y también se pueden quitar.
- Cada reconocimiento, manual o automático, lee todas las regiones configuradas.
- **Combates dobles:** la ficha muestra dos tarjetas una al lado de la otra.
- **Tu Pokémon contra el rival:** si se reconoce tu Pokémon, cada tarjeta añade el apartado «Contra tu X», con el multiplicador de cada uno de tus tipos contra el rival (STAB), el de cada tipo del rival contra ti y un veredicto: **Ventaja**, **Neutral** o **Desventaja**.
- La detección automática vigila todas las regiones, así que la ficha se actualiza al cambiar de Pokémon o cuando entra un nuevo rival en un doble.

## Capabilities

### New Capabilities
- `type-matchup`: cálculo de la comparativa de tipos entre tu Pokémon y el rival, con veredicto.

### Modified Capabilities
- `game-profiles`: el perfil admite las regiones opcionales del 2.º rival y de tu Pokémon; calibrarlas y quitarlas.
- `name-recognition`: el recorte y la lectura se hacen en todas las regiones configuradas.
- `battle-overlay`: tarjetas para dos rivales, apartado «Contra tu X» y submenú «Regiones del perfil».
- `battle-detection`: la huella combina todas las regiones, y se muestra la ficha cuando cambia la combinación de especies reconocidas.

## Impact

- **Código:** `core/profiles.py` (regiones opcionales), nuevo `core/matchup.py`, `pipeline.py` (lectura de varias regiones), `core/detection.py` (clave de combate genérica), `ui/overlay.py` (varias tarjetas y comparativa), `ui/tray.py`, `app.py`.
- **Compatibilidad:** los perfiles existentes siguen funcionando igual (solo región del rival).
- **Rendimiento:** un OCR más por cada región adicional y reconocimiento (unos 15-80 ms cada uno).
