## Context

`Pokedex.type_chart(generation)` ya devuelve la tabla atacante → defensor → multiplicador de cada generación: 15, 17 o 18 tipos, con las excepciones históricas. `ui/overlay.py` tiene la exclusión de captura (`WDA_EXCLUDEFROMCAPTURE` + `WS_EX_NOACTIVATE`) y `_bring_to_top`. El atajo se registra igual que el del buscador (`add-pokemon-search`).

## Goals / Non-Goals

**Goals:** chuleta de tipos fiel a la generación del juego, siempre a mano y sin estorbar al OCR. Resaltar los tipos del rival.

**Non-Goals:** combinar tipos dobles en una columna calculada (ya lo hace la ficha con sus eficacias); elegir la generación desde la tabla; habilidades (Levitación, etc.); llevarla al stream.

## Decisions

- **D1 · Un widget pintado con `QPainter`** (`TypeChartWindow` en `ui/type_chart.py`) en lugar de una rejilla de 324 `QLabel`: es más ligero y no tiene problemas de layout. Las filas llevan el nombre completo del tipo en una píldora. Las columnas llevan una abreviatura de 3 letras del nombre traducido en una píldora de su color; el nombre completo sale como tooltip.
- **D2 · Colores:** los de veredicto de la ficha (`theme.GOOD`, `theme.BAD`), y ×0 en gris oscuro. El texto de la celda es `MULTIPLIER_LABELS` (×2, ×½, ×0).
- **D3 · Resaltado:** `set_highlight(types)` dibuja un fondo claro en las columnas de esos tipos y realza su cabecera. `Controller` lo fija en `_show_battle`, después de mostrar la ficha, con los tipos de sus rivales. La ficha emite `became_hidden` en su `hideEvent` y la tabla se queda sin resaltado, así que vale para el ✕, el atajo, el fin del combate y el temporizador. Se repinta en cada cambio, visible o no.
- **D4 · Comportamiento de ventana:** sin marco, `Tool`, siempre encima, con `WA_ShowWithoutActivating`. La exclusión de captura y la no activación se aplican al primer `show`, reutilizando `_exclude_from_capture_and_activation` y `_bring_to_top` de `overlay.py`. Se arrastra con el ratón y el ✕ se pinta en la cabecera. `keep_on_top` se llama en el ciclo de vigilancia como con la ficha.
- **D5 · Posición y escala:** la primera vez, a la izquierda del emulador si cabe y, si no, centrada en la pantalla. Después, posición y escala se guardan en `state.json` (`type_chart_pos`, `type_chart_scale`) al soltar el arrastre o el tirador y con cada paso de la rueda. Se validan al cargar y la posición se ajusta a la pantalla al mostrarse.
- **D7 · Reescalado:** la tabla se pinta en coordenadas base y `QPainter.scale` la agranda entera, así que celdas, textos y píldoras crecen a la vez y la proporción no cambia (mejor que recolocar celdas para un tamaño libre). Tirador de 16 px en la esquina inferior derecha (el ancho manda) y `Ctrl` + rueda en pasos del 10 %, de 0,6 a 2,0.
- **D6 · `Ctrl+Alt+T`** («Tipos»), libre.

## Risks / Trade-offs

- [Con 18 tipos la tabla ocupa unos 504×476 px y puede tapar el juego] → se arrastra, se reduce hasta el 60 % y se cierra con el atajo.
- [Abreviaturas ambiguas en algún idioma] → un test comprueba que son únicas en es y en en; el tooltip da el nombre completo.
- [Pantalla completa exclusiva] → igual que la ficha: la guía ya recomienda la ventana sin bordes.
