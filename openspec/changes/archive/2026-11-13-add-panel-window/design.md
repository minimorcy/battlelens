## Context

`Overlay` y `TypeChartWindow` son widgets de nivel superior: sin marco, «siempre encima», excluidos de la captura, con posición propia (junto al emulador o donde los dejó el usuario) y que se mueven arrastrándolos. `app.py` los controla con `show_battle`, `hide`, `isVisible`, `keep_on_top`, `set_highlight` y `present`.

## Goals / Non-Goals

**Goals:** mostrar la ficha y la tabla en una ventana normal sin duplicar el código de la ficha; cambiar de modo en caliente; no tocar el comportamiento del modo Overlay.

**Non-Goals:** colocar cada sección de la ficha en su propio hueco del panel; el modo stream (sigue igual); tener varios paneles.

## Decisions

**D1. Se reutilizan los mismos widgets dentro del panel, reparentándolos.** `PanelWindow` (en `ui/panel.py`) es un `QWidget` normal con un `QHBoxLayout`. A la izquierda tiene una columna con `Overlay` y un texto «Esperando combate…»; a la derecha, `TypeChartWindow`. Al pasar a Panel se hace `setParent(panel, Qt.WindowType.Widget)`, y al volver a Overlay, `setParent(None, <flags originales>)`. *Alternativa descartada:* un widget de ficha nuevo para el panel, que duplicaría casi 1000 líneas de dibujo.

**D2. «Estoy dentro del panel» = `not self.isWindow()`.** No hace falta un flag nuevo. Dentro del panel:
- `Overlay._present` solo muestra (no mueve la ventana, no la excluye de la captura, no la pone encima). Mantiene el temporizador de autoocultado.
- `_fit_to_screen` fija el ancho y deja libre la altura: limita la altura a la de la columna del panel en lugar de a la de la pantalla, y se desplaza si no cabe.
- No se arrastra. El clic en un título sigue plegando la sección.
- `keep_on_top` no hace nada.
- `TypeChartWindow` no pinta el ✕ ni el tirador, y no reacciona al arrastre ni a Ctrl+rueda. Su escala la fija el panel.

**D3. Estado vacío con `hide`/`show`.** `app.py` sigue llamando a `overlay.hide()` y `overlay.isVisible()` como siempre. El panel escucha `Show`/`Hide` del overlay (event filter) y alterna el texto «Esperando combate…». Así no cambian ni la detección ni `became_hidden`, que sigue limpiando el resaltado de la tabla.

**D4. Aparecer sin robar el foco.** Cuando el overlay se presenta dentro del panel y este está cerrado, se llama a `panel.show()` con `WA_ShowWithoutActivating`. El panel no es «siempre encima»: el usuario lo coloca en la otra pantalla. Cerrarlo (✕ del marco) solo lo oculta y reaparece con la siguiente ficha o desde la bandeja («Mostrar el panel»).

**D5. Tabla cargada siempre.** Se extrae `_load_type_chart()` de `toggle_type_chart` (generación del perfil activo) y se llama al entrar en Panel y antes de cada `show_battle`, para que la tabla corresponda a la generación del juego. Así la tabla está visible desde el principio. El atajo y el menú de la tabla la ocultan o muestran dentro del panel (mismo código, `present` = `show`).

**D6. Escalado de la tabla.** En `resizeEvent` del panel y tras cada ficha (cambia el ancho de la columna izquierda): `scale = min(ancho_libre/base_w, alto_libre/base_h)`, limitado a `[MIN_SCALE, MAX_SCALE]`. La escala del panel no se guarda; `type_chart_scale` sigue siendo la de la tabla flotante.

**D7. Configuración y estado.** `Config.overlay_display: "overlay" | "panel"` (TOML `[overlay] display`), validado como `overlay_mode`. `AppState.panel_geometry: [x, y, w, h] | None`, aplicado con comprobación de tipos (puede venir editado a mano) y limitado a una pantalla existente. El cambio en Ajustes se aplica en `_apply_settings` llamando a `_set_display(mode)`.

## Risks / Trade-offs

- [Reparentar una ventana a la que ya se aplicó `SetWindowDisplayAffinity` crea un HWND nuevo] → al volver a Overlay se pone `_capture_excluded = False` en los dos widgets para que se excluyan de nuevo.
- [El panel no está excluido de la captura] → la captura es de la ventana del emulador, así que solaparse no afecta al OCR. Además permite capturar el panel en OBS si se quiere.
- [En un monitor bajo, la tabla queda pequeña] → la escala mínima es 0.6 y la ventana se puede agrandar o maximizar.
