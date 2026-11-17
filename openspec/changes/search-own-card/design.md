## Context

`App.search_pokemon` abre un `SearchDialog` modal y, al elegir, llama a `_show_battle((sid, None, None), …, searched=True)`: pinta la búsqueda en la misma `Overlay` del rival. Para que no se pisen, la detección se pausa con `_modal_open` y la marca `_searched` evita publicarla en el stream y la conserva al redibujar.

`PanelWindow` reparenta esa `Overlay` y las dos tablas (`TypeChartWindow`, `NatureChartWindow`) dentro de una ventana con dos huecos colocados a mano: `_column` (ficha, ancho fijo) y `_chart_slot` (tablas, `fit_chart` elige apiladas o lado a lado). `Overlay` ya sabe vivir dentro de otro widget: `_available_height` usa el alto de su padre y `_present` no la coloca ni la pone encima.

## Goals / Non-Goals

**Goals:**
- Dos fichas independientes: rival y buscada.
- Buscador siempre visible en el panel; diálogo en modo overlay.
- Reutilizar `Overlay`, el completer y el patrón de reparentado del panel sin duplicar código.

**Non-Goals:**
- Varias fichas buscadas a la vez (una sustituye a la anterior).
- Publicar la ficha buscada en el stream o darle su propio modo.
- Columnas configurables o reordenables en el panel.
- Cambiar el atajo de forma para que actúe sobre la ficha buscada.

## Decisions

**D1. Segunda instancia de `Overlay` (`App.search_card`).** Se crea igual que `self.overlay`, con `auto_hide_seconds=0` (el temporizador no la oculta) y sus propias conexiones: `moved` → `state.search_card_pos`, `form_step` → forma de la búsqueda, `dismissed` sin tocar `battle`. Comparte `hidden`, `type_icons`, `sprites`, `language` y `mode` con la del rival, así que todos los sitios que hoy los actualizan en `self.overlay` pasan por un bucle sobre las dos. El dict `collapsed` es el mismo objeto en las dos para que el plegado sea común y se guarde como hoy. *Alternativa descartada:* una sola `Overlay` con tarjetas de rival y buscada mezcladas; complica `show_battle`, la posición y la ocultación por separado.

**D2. Estado propio de la búsqueda.** `App._last_search = (sid, form, game)` sustituye a `_searched`. `_show_search()` pinta `search_card.show_battle([view], None, rect, [None])` y `_redraw_last_battle` redibuja también la búsqueda si está visible (cambio de modo, iconos, idioma). La forma se guarda en `_last_search`, no en `_form_choice`, que vuelve a ser solo del rival. `_show_battle` pierde el parámetro `searched` y siempre publica en el stream. Se elimina `_modal_open` del buscador (se mantiene donde lo usen otros diálogos).

**D3. `SearchField` reutilizable.** El contenido de `SearchDialog` (campo, completer con `_TypesDelegate`, aviso de error y resolución) pasa a `SearchField(QWidget)` con la señal `chosen(int, object)` y `set_entries(entries)`. `SearchDialog` queda como envoltorio: lo contiene, en `chosen` guarda `choice` y hace `accept()`. En el panel, tras `chosen` se vacía el campo; `Esc` lo vacía. La app construye las entradas en un método (`_search_entries()`) y las refresca en el campo del panel al cambiar de perfil o de idioma.

**D4. Panel en tres columnas.** Se añade `_search_column` a la derecha del `QHBoxLayout`, con el `SearchField` arriba (alto natural) y la `search_card` reparentada debajo, colocada a mano como la del rival. Para que `_available_height` siga siendo «el alto del padre», la ficha buscada vive en un hueco propio (`_search_slot`) bajo el campo. Ambas columnas de ficha tienen ancho fijo `_base_width`; la central (`_chart_slot`) se queda con el resto (`stretch=1`). `fit_chart` no cambia: en una columna estrecha ya elige apilar. `dock`/`undock` reparentan también la `search_card` y guardan/restauran sus flags. `PanelWindow` recibe `search_card` y el `SearchField` en el constructor; el resto de su API no cambia.

**D5. Atajo en modo panel.** `search_pokemon` en modo panel hace `panel.show(); panel.raise_(); panel.activateWindow(); field.edit.setFocus()`. El panel tiene `WA_ShowWithoutActivating` para no robar el foco al aparecer solo; aquí el usuario lo pide, así que se activa explícitamente.

**D6. Tamaño inicial.** `resize(1100, 720)` pasa a `resize(1440, 760)` y el mínimo a `(760, 400)`. Una geometría guardada sigue mandando. Se comprueba con la captura de la guía y se ajusta si la tabla queda pequeña.

## Risks / Trade-offs

- [Dos fichas flotantes se solapan en modo overlay] → la buscada usa su propia posición guardada; sin ella aparece desplazada respecto a la del rival (a la izquierda de la ventana del emulador o debajo de la del rival si no cabe).
- [`keep_on_top` y la exclusión de captura solo se aplicaban a una ficha] → el tick de vigilancia y `undock` las aplican a las dos.
- [Panel estrecho en pantallas de 1366 px] → el mínimo (760) deja la tabla muy pequeña; aceptable porque las fichas se desplazan y la tabla tiene `MIN_SCALE`. Se documenta en la guía.
- [Quitar la pausa de la detección: el OCR corre mientras se escribe] → la búsqueda ya no comparte ficha con la detección, así que no hay conflicto; el coste de CPU es el mismo que sin buscador.
- [Escribir en el panel cuando está detrás del juego] → se resuelve con el atajo (D5), que lo trae delante y enfoca el campo.

## Migration Plan

Sin migración de datos: `state.json` gana `search_card_pos` opcional (ausente = posición por defecto). `config.toml` no cambia.
