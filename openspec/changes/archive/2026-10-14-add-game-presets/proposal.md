## Why

Para empezar, un tester tiene que calibrar a mano: entrar en un combate, pulsar `Ctrl+Alt+C` y dibujar un rectángulo ajustado sobre el nombre del rival (y, para lo demás, sobre el de su Pokémon y el menú de ataques). Es el paso en el que más gente se atasca. En la mayoría de los juegos los recuadros están siempre en el mismo sitio de la imagen del juego, así que BattleLens puede traer esas regiones ya medidas.

## What Changes

- **Presets por juego** con las regiones del rival y de tu Pokémon (y del menú de ataques cuando se conoce), en fracciones de la imagen del juego: Rojo/Azul/Amarillo, Oro/Plata/Cristal, Rubí/Zafiro/Esmeralda, Rojo Fuego/Verde Hoja, Diamante/Perla/Platino, HeartGold/SoulSilver, Negro/Blanco y Negro 2/Blanco 2 (pantalla superior) y Espada/Escudo. Los juegos con el nombre del rival flotante (Escarlata/Púrpura) quedan fuera de este change.
- **Localización de la imagen del juego** dentro de la ventana del emulador: se descartan las bandas uniformes (negras o de color) y, con la proporción del juego, se separan la barra de menús o de estado y, en DS, la pantalla superior (en vertical u horizontal).
- **Asistente «Nuevo perfil con un preset…»:** con una captura del emulador en un combate, propone el juego (por el título de la ventana) y **dibuja los recuadros del preset sobre la captura** para que el usuario confirme que caen sobre los nombres. Muestra lo que lee BattleLens en cada recuadro y ofrece **guardar**, **ajustar la imagen del juego** (dibujando su rectángulo, si la localización automática falló) o **calibrar a mano** (el método actual).
- **Primer arranque:** si no hay perfiles, el aviso de bienvenida y la bandeja proponen el asistente.
- **Herramienta de validación** (`tools/validate_presets.py`): aplica los presets a capturas de referencia locales y muestra qué se lee en cada región. Las capturas no se incluyen en el repositorio.

## Capabilities

### New Capabilities
- `game-presets`: presets por juego, localización de la imagen del juego, asistente de confirmación y herramienta de validación.

### Modified Capabilities
- `game-profiles`: la calibración interactiva ofrece empezar con un preset.
- `name-recognition`: tolerancia a las letras que el OCR confunde en las fuentes pixeladas (A/R, D/O), detectada al validar los presets de GBA.

## Impact

- **Código:** nuevo `core/presets.py` (datos y conversión a regiones del perfil), nuevo `vision/viewport.py` (localización), nuevo `ui/preset_wizard.py` (confirmación), `app.py` y `ui/tray.py` (entrada de menú y primer arranque), catálogos `i18n` y `tools/validate_presets.py`.
- **Perfiles:** los creados con un preset son perfiles normales (regiones relativas al área cliente). Se pueden recalibrar como siempre.
- **Riesgo:** las medidas salen de capturas de referencia, no de emuladores reales. El asistente obliga a confirmarlas a ojo y la validación manual las comprobará en emuladores reales.
