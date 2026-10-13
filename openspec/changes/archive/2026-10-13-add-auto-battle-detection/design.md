## Context

El reconocimiento manual tarda unos 15-80 ms y la captura con PrintWindow unos 15-20 ms. La región calibrada puede incluir el nivel y la barra de PS (caso real de Pokémon Espada), así que su contenido cambia también durante el combate.

## Goals / Non-Goals

**Goals:**
- Mostrar la ficha sin pulsar nada, en 1-1,5 s desde que aparece el nombre.
- Coste bajo fuera de los combates: sin OCR mientras la escena se mueve.
- Ningún aviso molesto fuera de los combates.

**Non-Goals:**
- Detectar el combate por otros indicios (música, transición de pantalla, barra de PS). La región del nombre basta y vale para cualquier juego.
- Combates dobles (cambio `add-matchup-and-doubles`).

## Decisions

### D1. Máquina de estados pura (`core/detection.py`)
`BattleDetector.on_frame(huella, ahora)` devuelve `RECOGNIZE`, `HIDE` o `NONE`; `on_result(especie|None, huella, ahora)` devuelve `SHOW` o `NONE`; `on_manual_result(...)` y `on_hidden_by_user()` mantienen el estado coherente con el modo manual. Al no depender de Qt ni del reloj real (`ahora` es un parámetro), todos los escenarios se prueban con secuencias de huellas sintéticas.

### D2. Huella = miniatura 32×12 en gris; diferencia = media absoluta
Barata (Pillow, sin OCR) e insensible al ruido de compresión. Umbral de 8/255: el parpadeo de un píxel no la supera, mientras que la aparición de un recuadro de texto la supera con mucho. Se usa una huella de tamaño fijo para que el resultado no dependa del tamaño de la ventana.

### D3. Estabilidad de 2 ciclos y memoria del último intento
Esperar 2 ciclos estables evita reconocer a mitad de una animación de entrada. Guardar la huella del último intento evita repetir el OCR sobre una pantalla que no ha cambiado; mientras el jugador está quieto fuera de combate, se intenta una vez y no más.

### D4. Ocultación por «ausencia» con tolerancia
Al mostrar una especie se guarda su huella (`shown_fp`). Si la huella actual difiere de `shown_fp` de forma continuada durante `hide_after_seconds`, se oculta. Cualquier reconocimiento correcto de la misma especie renueva `shown_fp` y reinicia el contador, lo que tolera los cambios de la barra de PS y las animaciones breves.

### D5. Integración en Qt
Un `QTimer` en el hilo de la interfaz lanza cada ciclo una `_Task` (QThreadPool) que captura y calcula la huella. Si el detector pide reconocer, se encola otra tarea con `read_crop` sobre el mismo recorte, sin volver a capturar. Hay un indicador de «ciclo en curso» para no acumular tareas, y se reutiliza `_busy` para no solaparse con el reconocimiento manual. El resultado manual también actualiza el detector (`on_manual_result`), de modo que un rival reconocido a mano no se vuelve a mostrar de forma automática.

### D6. Configuración y estado
`config.toml` → `[detection] enabled = true, interval_ms = 500, hide_after_seconds = 4`. El conmutador de la bandeja se guarda en `state.json` (`auto_detect`); si existe, tiene prioridad sobre `enabled`. Los `config.toml` antiguos sin la sección `[detection]` usan los valores por defecto.

## Risks / Trade-offs

- [Juegos cuya región cambia continuamente en combate (texto animado)] → No se estabilizaría nunca. Se mitiga recomendando una región ajustada al nombre; si no basta, el atajo manual sigue disponible.
- [Coste de CPU] → Unos 40 ms de trabajo por segundo en un hilo aparte. Desactivable desde la bandeja.
- [Falso positivo fuera de combate (un cartel con el nombre de un Pokémon en la región)] → Raro. Como mucho aparece una ficha, que se oculta sola al cambiar la escena.

## Migration Plan

Ninguna: los valores por defecto se aplican a las configuraciones existentes.

## Open Questions

Ninguna.
