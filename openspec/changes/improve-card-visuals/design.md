## Context

`ui/overlay.py` construye la tarjeta con `QLabel` y hojas de estilo en línea. Todo elemento con tipo pasa por `_pill()`, que pinta el color pleno de `theme.TYPE_COLORS`. Las secciones se separan solo con `_section_title()` y un espaciado uniforme de 5 px. Los colores sueltos (veredictos, `#3ddc97`, `#e5484d`, `ABILITY_EFFECT_COLOR`, `stat_color()`) están repartidos entre `overlay.py` y `theme.py`. La ficha del stream replica la misma estructura en HTML/CSS (`stream/static`). Las capturas de la web se generan con `tools/make_site_screenshots.py`.

Problemas observados en `site/assets/card-competitive.png` y `card-double.png`:
1. Más de 20 pastillas saturadas del mismo tamaño y peso; los tipos del Pokémon no destacan frente a sus debilidades.
2. Amarillo para todos los multiplicadores (×4, ×½, ×0), para «Tú/Él» y para el nivel: el acento deja de ser acento.
3. «Fuego ×1» mezcla tipo y número dentro de la pastilla; los ×1 de «Contra tu X» ocupan mucho y aportan poco.
4. Barras de estadísticas en semáforo de cinco colores, que se suman al ruido.
5. Las secciones no tienen contenedor: la tarjeta se lee como una lista continua.

## Goals / Non-Goals

**Goals:**
- Jerarquía clara: nombre y tipos → «Contra tu X» → eficacias → resto.
- Menos saturación: color pleno solo donde identifica al Pokémon; en el resto, el color es una pista.
- Color semántico coherente (bueno/malo/neutral) en toda la ficha.
- Mismo lenguaje visual en la ficha privada y en la del stream.

**Non-Goals:**
- Cambiar qué datos muestra cada modo, los textos traducidos o el orden de las secciones decidido en `display-modes`.
- Tema claro o colores personalizables.
- Sprites o iconos de tipo (otro change: añaden assets y licencias).
- Cambiar los anchos (300/360 px) o el comportamiento de la ventana.

## Decisions

### D1. Tokens en `theme.py`
Se centralizan los colores que hoy están sueltos:
- `SURFACE` (fondo de bloque, p. ej. `rgba(255,255,255,0.04)`) y `SURFACE_BORDER`.
- `GOOD` `#3ddc97`, `BAD` `#e5484d`, `NEUTRAL` `#8a90a3`; los usan los veredictos y los multiplicadores.
- `soft_type_style(type_id)`: fondo del color del tipo al ~22 % de opacidad sobre el panel, borde de 1 px del color al ~60 % y texto `TEXT`. No necesita `DARK_TEXT_TYPES` (el texto siempre es claro).

`overlay.py` deja de definir colores propios.

### D2. Dos variantes de pastilla
`_pill(text, type_id, solid=False)`: `solid=True` solo en la cabecera (tipos del Pokémon). Todas las demás llamadas pasan a la variante suave. Contraste: comprobar AA (4,5:1) del texto claro sobre la pastilla suave de los 18 tipos, incluidos Eléctrico y Acero.

### D3. Bloques
Helper `_block(title) -> QVBoxLayout` que crea un `QFrame` con `SURFACE`, radio de 8 px, márgenes de 8/10 px y el título dentro. Espaciado: 8 px entre bloques y 4 px dentro. El cálculo de altura de `show_battle` (`totalHeightForWidth`) sigue valiendo porque los bloques son layouts anidados; se verifica con los tests de escala ×2.

### D4. Multiplicadores
Columna de multiplicador con ancho fijo y color semántico **desde el punto de vista del jugador**:
- Eficacias del rival: ×4/×2 en `GOOD` (le puedes pegar fuerte), ×½/×¼ en `BAD` y ×0 en `NEUTRAL`. *(Decidido: P1.)*
- «Tus movimientos»: >1 `GOOD`, <1 `BAD` (como ahora).
- Movimientos del rival contra ti: >1 `BAD`.

En «Contra tu X», el multiplicador pasa a una insignia pequeña a la derecha de la pastilla suave del tipo (`Fuego` `×2`), y los ×1 se muestran con la insignia en gris.

### D5. «Contra tu X»
Bloque con un borde izquierdo de 3 px del color del veredicto y el veredicto como pastilla sólida en la fila del título (P3). «Tú/Él» en `TEXT_MUTED`. La velocidad, en una línea propia con el veredicto en negrita.

### D6. Captura
En Normal: etiqueta «Captura» + barra de 6 px (valor/255) en el color de dificultad + «140 · Media». En Competitivo sigue siendo una línea discreta.

### D7. Estadísticas
Barras en un solo color (`ACCENT` atenuado o un azul), con la más alta en el color pleno y la más baja en `BAD` atenuado. El total, alineado con la columna de valores y separado por una línea fina. *(Decidido: P2.)*

### D8. Movimientos, habilidades, evolución y entrenamiento
- Movimientos: pastilla suave de tipo con ancho fijo (el del tipo más largo en el idioma) y categoría abreviada (`Fís.`/`Esp.`/`Est.` · potencia), alineada a la derecha y en gris.
- Habilidades: nombre en negrita, «oculta» como insignia de contorno; efectos como insignia de contorno neutra (sin el azul `#3a4a6b`).
- Evolución: nombres separados por `›`, con la especie actual en `TEXT` y negrita y el resto en gris; las condiciones, en gris y más pequeñas.
- Entrenamiento: pares etiqueta/valor en dos columnas en lugar de un párrafo con `<br>`.

### D9. Stream
`card.css` replica los tokens como variables CSS (`--surface`, `--good`…) y `card.js` usa las mismas variantes. Si al payload le falta algún dato (especie actual en la evolución, estadística máxima/mínima), se calcula en el cliente o se añade a `payload.py` sin cambiar los textos.

### D10. Identificadores para tests
Se mantienen los `objectName` actuales (`species-name`, `verdict`, `capture`, `stat-total`, `evolution`…). Si el multiplicador sale de la pastilla, la insignia recibe su propio `objectName` y se ajustan los tests que comparan «Tipo ×N».

### D11. Bloques plegables
- Cada bloque tiene una clave estable: `matchup`, `own_moves`, `eff`, `stats`, `abilities`, `moves`, `training`, `evo`. La cabecera no se pliega.
- El título es un `QLabel` con una flecha (▾ desplegado, ▸ plegado) y cursor de mano. En `mouseReleaseEvent`, si no hubo arrastre y el clic cae sobre un título, se alterna el bloque en lugar de ocultar la ficha; el clic en el resto la oculta como hasta ahora. El arrastre funciona igual desde cualquier punto.
- Plegado: se ocultan los widgets del bloque salvo la fila del título. En «Contra tu X», el veredicto está en esa fila y sigue visible.
- Tras alternar se llama a `_fit_to_screen` sin recolocar la ficha (se mantiene la esquina superior izquierda).
- Se guarda en `state.json` (`collapsed_sections`, p. ej. `{"competitive": ["abilities"]}`), junto a la posición de la ficha: es estado de la interfaz, no configuración. Así no pasa por `Config` ni por el `collect()` de Ajustes, que reconstruye la configuración desde el formulario y lo borraría al guardar. El overlay emite `collapsed_changed` y la app guarda el estado.
- La ventana usa `WS_EX_NOACTIVATE`, así que el clic no quita el foco al emulador; se comprueba en la validación manual.
- La ficha del stream no se pliega.

### D12. Textos nuevos
«Eficacias» (título del bloque que agrupa debilidades, resistencias e inmunidades), «Desplegar todas las secciones» y las categorías abreviadas (`Fís.`/`Esp.`/`Est.`) se añaden al catálogo de traducciones (`en_card.py`). El resto de textos no cambia.

## Risks / Trade-offs

- [Clic para plegar frente a clic para ocultar] → solo el título pliega, con el cursor de mano y la flecha como pista; el resto de la ficha mantiene el comportamiento actual.

- [Pastillas suaves menos legibles en tipos oscuros como Siniestro o Fantasma] → borde al 60 % y test de contraste de los 18 tipos sobre `soft_type_style`.
- [Los bloques añaden altura] → márgenes internos pequeños; la ficha competitiva no debería crecer más de un ~5 % (comprobar con la captura de Stufful).
- [Qt Style Sheets no admite sombras y tiene soporte irregular de `rgba` en algunos widgets] → solo fondos, bordes y radios, que sí funcionan en `QFrame`/`QLabel`.

## Resolved Questions

- **P1.** Debilidades del rival en verde (`GOOD`) y resistencias en rojo (`BAD`): el color se lee desde el punto de vista del jugador, como en «Tus movimientos».
- **P2.** Estadísticas en una sola gama, con la más alta en el color pleno y la más baja en `BAD` atenuado.
- **P3.** El veredicto sigue siendo una pastilla sólida, además del borde del bloque.
- **P4.** La web no se rediseña: solo se regeneran sus capturas.
