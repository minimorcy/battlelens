## Why

La ficha enseña los datos correctos, pero visualmente es una sucesión de pastillas de colores saturados con el mismo peso: los tipos del Pokémon, cada debilidad, resistencia e inmunidad, los tipos de «Contra tu X», cada movimiento y los efectos de habilidad usan la misma pastilla de color pleno. En la ficha competitiva hay más de 20 pastillas, y además los multiplicadores en amarillo, las barras de estadísticas en cinco colores y la captura coloreada. No hay jerarquía: el ojo no sabe a dónde ir y todo parece «pegotes». Las secciones solo se separan por un título en mayúsculas, así que la tarjeta se lee como una lista larga.

## What Changes

- **Jerarquía por bloques**: la tarjeta se organiza en una cabecera (nombre, número, nivel y tipos) y bloques con un fondo apenas más claro que el panel (Combate, Eficacias, Estadísticas, Habilidades, Movimientos, Datos), con más aire entre bloques que dentro de ellos.
- **Color con intención**: el color pleno de tipo queda solo para los tipos del propio Pokémon (cabecera). En el resto de sitios, los tipos usan una **pastilla suave** (fondo oscuro teñido del color del tipo, borde del color y texto claro).
- **Multiplicadores con significado**: el color del multiplicador indica si es bueno o malo para el jugador (verde/rojo/gris) en vez del amarillo para todo.
- **«Contra tu X»** como bloque destacado: borde izquierdo del color del veredicto, el multiplicador como insignia aparte del tipo y «Tú/Él» en gris.
- **Captura** (modo Normal) como un medidor corto con el color de la dificultad, en lugar de una línea de texto en color.
- **Estadísticas**: barras en una sola gama de color, sin el semáforo de cinco colores; se resaltan la estadística más alta y la más baja.
- **Movimientos y habilidades**: tipo del movimiento como pastilla suave de ancho fijo y categoría abreviada; efectos de habilidad como insignia neutra con contorno.
- **Evolución** como una fila de nombres con flechas, con la especie actual resaltada.
- **Bloques plegables**: un clic en el título de un bloque lo pliega o despliega (también «Contra tu X», cuyo veredicto sigue visible plegado). Lo plegado se guarda por modo en `state.json` (`collapsed_sections`), se aplica a todas las tarjetas de un combate doble y Ajustes ofrece «Desplegar todas las secciones». El clic en el resto de la ficha la sigue ocultando.
- Para que todo bloque tenga título: debilidades, resistencias e inmunidades van en un bloque «Eficacias», y en modo Normal el total de estadísticas base pasa a la cabecera.
- La ficha del **modo stream** (`card.css`/`card.js`) adopta el mismo lenguaje visual.
- Los datos que muestra cada modo **no cambian** (specs `display-modes` y `stream-mode` intactas en contenido); tampoco los anchos, el ajuste a la pantalla ni el desplazamiento.

## Capabilities

### New Capabilities
<!-- Ninguna. -->

### Modified Capabilities
- `battle-overlay`: nuevo requisito de estilo visual de la ficha (jerarquía, uso del color, legibilidad).
- `stream-mode`: la ficha del stream sigue el mismo estilo que la privada (sin bloques plegados: el público la ve completa).
- `app-settings`: botón «Desplegar todas las secciones».

## Impact

- `ui/theme.py` (tokens nuevos: superficie de bloque, colores semánticos, pastilla suave) y `ui/overlay.py` (cabecera, bloques y secciones).
- `stream/static/card.css` y `card.js`; quizá `stream/payload.py` si hace falta marcar la especie actual en la evolución o la estadística más alta/baja.
- Tests de UI que lean el texto de las pastillas (p. ej. «Fuego ×1» si el multiplicador pasa a ser una insignia aparte) y de stream.
- `tools/make_site_screenshots.py`: regenerar `card-normal.png`, `card-competitive.png`, `card-double.png` y `og-image.png`.
