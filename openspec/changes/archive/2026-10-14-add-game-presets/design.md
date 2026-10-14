## Context

Los perfiles guardan regiones en fracciones del área cliente de la ventana del emulador (`Region`). La imagen del juego ocupa solo una parte de esa área: hay bandas negras al escalar sin deformar, barras de menús y de estado dibujadas por el propio emulador (mGBA y melonDS usan Qt, así que su barra de menús forma parte del área cliente) y, en DS, dos pantallas en vertical, en horizontal o una sola. Las medidas de los recuadros salen de capturas de referencia de internet (`capturas-presets/`, fuera del repositorio).

## Goals / Non-Goals

**Goals:**
- Crear un perfil útil sin dibujar nada en los emuladores habituales.
- Que el usuario vea y confirme dónde caen los recuadros antes de guardar.

**Non-Goals:**
- Juegos con el nombre del rival flotante (Escarlata/Púrpura, Leyendas Z-A): necesitan otro método de lectura (otro change).
- Combates dobles (región del 2.º rival) en los presets: se calibra a mano como hasta ahora.
- 3DS (X/Y a Ultrasol/Ultraluna) y Let's Go, hasta tener capturas de referencia fiables.

## Decisions

### D1. Datos (`core/presets.py`)
`Preset(id, games, aspect, ds, regions)` con `regions: dict[rol, (x, y, w, h)]` en fracciones de la imagen del juego (`rival`, `own` y, si se conoce, `moves`). Las regiones van holgadas: el lector ya tolera texto de más, y un recuadro holgado aguanta mejor las pequeñas diferencias entre emuladores. `preset_for(game_id)` devuelve el preset, o `None`. `to_profile_regions(preset, viewport, client_size)` convierte cada región a `Region` del área cliente.

### D2. Localización (`vision/viewport.py`)
`find_viewport(frame, aspect, ds=False) -> Viewport(x, y, w, h, reliable)` sigue tres pasos:
1. **Bandas uniformes:** desde cada borde se descartan las filas y columnas cuya desviación típica de luminancia es menor que 4.
2. **Ajuste a la proporción:** si el rectángulo que queda es más alto de lo esperado, se busca en la franja sobrante la fila con mayor salto de luminancia respecto a la siguiente (el borde entre la barra y el juego) y se toma la imagen a partir de ahí, o hasta ahí si la franja está abajo. Para las columnas sobrantes se hace lo mismo.
3. **DS:** antes del ajuste, si la proporción del resto es próxima a 4:6 o a 8:3, se toma la mitad de arriba o de la izquierda, descontando el hueco entre pantallas si lo hay (filas uniformes en el centro).

`reliable` es falso si la proporción final se aleja más de un 6 % de la esperada.

### D3. Asistente (`ui/preset_wizard.py`)
`PresetWizard(image, games_with_presets, proposed_game, read_fn)` es un `QDialog` con:
- un selector de juego;
- la captura escalada con el rectángulo de la imagen del juego (discontinuo) y los recuadros del preset (de colores, con su nombre);
- debajo, la lectura de cada recuadro (`read_fn(rol, recorte) -> texto`, que reutiliza `read_crop` y `read_moves`);
- los botones «Guardar perfil», «Ajustar la imagen del juego» y «Calibrar a mano».

«Ajustar» reutiliza el dibujo de rectángulos de `CalibrationDialog` para elegir la imagen del juego. El asistente devuelve el preset, el viewport y la acción. La app crea el perfil con `ask_profile` (nombre y juego propuestos) y las regiones convertidas.

### D4. Integración
- En la bandeja, «Nuevo perfil con un preset…» va encima de «Calibrar nuevo perfil…».
- El aviso de arranque sin perfiles cambia a: «Abre "Nuevo perfil con un preset…" en la bandeja durante un combate.».
- La lectura de los recuadros en el asistente se hace en el hilo de la interfaz: son pocas regiones y el usuario está esperando la confirmación.

### D5. Validación
`tools/validate_presets.py <carpeta> [--save-crops]` deduce el juego del nombre del archivo (`<nn>-<juego>__…`, con una tabla de alias a los identificadores de juego), localiza, aplica el preset y lee. No es un test automático porque las capturas no están en el repositorio. Los tests usan imágenes sintéticas para la localización y comprueban las regiones con números.

## Risks / Trade-offs

- [Medidas de capturas de internet] → Regiones holgadas, confirmación visual obligatoria y comprobación en emuladores reales (validación manual).
- [Barra de menús pegada a una zona lisa y clara del juego] → El borde entre ambas es débil y el corte puede desviarse unos píxeles (≈2 % del alto en las pruebas). Lo absorben los recuadros holgados, y si no, «Ajustar la imagen del juego».
- [Game Boy: nivel del rival] → En la Gen 1 el nivel («:L12») va a la izquierda, bajo el nombre, y la búsqueda adicional del nivel mira la mitad derecha, así que casi nunca se lee. No afecta al modo Normal; queda para un change de lectura del nivel por juego.
- [Marco del Super Game Boy] → El marco de 256×224 no se separa solo; se usa «Ajustar la imagen del juego».
- [Localización fallida con temas o barras raras] → «Ajustar la imagen del juego» la resuelve con un rectángulo.
- [Combates dobles en juegos con preset] → La región del rival cubre el recuadro del primer rival. El segundo se calibra a mano.

## Migration Plan

Nada que migrar: el asistente solo crea perfiles nuevos.

## Open Questions

Ninguna.
