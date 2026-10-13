## Why

Ahora hay que pulsar `Ctrl+Alt+P` en cada combate, y a veces más de una vez si el rival cambia. Es la principal fricción de uso. Como la captura ya funciona aunque el emulador esté tapado, se puede vigilar la región del nombre de forma continua y barata, y reconocer al rival en cuanto aparece.

## What Changes

- **Detección automática**, activada por defecto: cada `interval_ms` (500 ms por defecto) se captura la región del nombre del perfil activo y se calcula una huella pequeña. Cuando la huella cambia y se estabiliza, se reconoce. Si sale una especie distinta de la mostrada, se muestra su ficha.
- En modo automático **no** se muestra «No reconocido»: así no aparecen avisos fuera de los combates.
- **Ocultación automática** de la ficha cuando la región deja de mostrar a ese rival durante `hide_after_seconds` (4 s por defecto, 0 = nunca).
- Opción **«Detección automática»** activable en la bandeja (se recuerda entre sesiones) y nueva sección `[detection]` en `config.toml`.
- El atajo manual sigue funcionando igual, incluido el aviso de «No reconocido».

## Capabilities

### New Capabilities
- `battle-detection`: vigilancia periódica de la región, huella y estabilidad, cuándo reconocer, cuándo mostrar y cuándo ocultar.

### Modified Capabilities
- `battle-overlay`: el menú de la bandeja incluye «Detección automática».

## Impact

- **Código:** nuevo `core/detection.py` (máquina de estados pura, sin Qt), `vision/preprocess.py` (huella), `core/config.py` (sección `[detection]` y estado), `app.py` (temporizador y tareas), `ui/tray.py`.
- **Rendimiento:** una captura y una miniatura cada 500 ms (unos 15-20 ms en un hilo de trabajo). El OCR solo se ejecuta cuando la región cambia y se estabiliza.
- **Sin dependencias nuevas.**
