## Context

`TypeChartWindow.set_highlight(types)` solo guarda columnas. `_show_battle` ya tiene `own_view` cuando el perfil lee tu Pokémon. La bandeja emite señales que `Controller` conecta; el atajo de calibrar ya llama a `Controller.calibrate()`.

## Decisions

- **D1 · Filas para tu Pokémon y columnas para el rival.** Es la lectura natural de la tabla: la fila es quien ataca y la columna quien defiende, así que el cruce es «mi ataque de mi tipo contra él». Descartado resaltar también las filas del rival y tus columnas («lo que él me hace»): mezcla dos lecturas en los mismos ejes y deja de entenderse de un vistazo. Eso ya lo da la ficha en «Contra tu X».
- **D2 · Colores:** las columnas del rival siguen en blanco translúcido y las filas propias van en el amarillo de acento (`theme.ACCENT`) translúcido. El cruce lleva un borde amarillo. La leyenda («▮ Rival · ▮ Tú») va en la cabecera, junto al título, solo cuando hay algo resaltado.
- **D3 · API:** `set_highlight(defending, attacking=())`, con `highlight` (columnas) y `highlight_rows`. `became_hidden` limpia ambos con `set_highlight(())`.
- **D4 · Bandeja:** acción «Modificar o crear perfil…» con `_hint("calibrate")` junto a «Nuevo perfil con un preset…» y la señal `calibrate_requested` → `Controller.calibrate`. Se actualiza en `set_hotkey_hints`.

## Risks / Trade-offs

- [En dobles no se distingue qué columna es de qué rival] → se acepta para esta versión; las fichas ya están en el orden de la pantalla. Se podría marcar cada columna con «1»/«2» más adelante.
