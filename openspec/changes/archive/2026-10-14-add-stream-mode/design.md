## Context

La ficha privada (`ui/overlay.py`) se marca con `WDA_EXCLUDEFROMCAPTURE`. Es necesario porque, cuando `PrintWindow` no devuelve el contenido del emulador, `capture.py` copia esa zona de la pantalla con `mss`, y si la ficha estuviera encima, el OCR la leería a ella. OBS tampoco la ve. Los textos de la ficha (líneas de habilidades, notas de la comparativa) son métodos privados del overlay. La app ya concentra en `_show_battle` todo lo que se muestra, y la ocultación por fin de combate pasa por `Action.HIDE` en `_on_watch_frame`.

## Goals / Non-Goals

**Goals:**
- Que el público vea la ficha sin tocar el comportamiento de quien no emite.
- Configuración mínima para el streamer: activar, copiar la URL y pegarla en OBS.
- Sin exponer nada fuera del propio PC.

**Non-Goals:**
- Comandos de chat de Twitch y resumen del directo (otro change, sobre este servidor).
- Personalizar los colores o la plantilla de la ficha del stream.
- WebSocket o Server-Sent Events: el sondeo cada 400 ms basta y es más simple y robusto en el navegador de OBS.

## Decisions

### D1. Fuente de navegador en lugar de una ventana capturable
Una ficha visible en la captura volvería a provocar autolecturas del OCR con la copia de pantalla, y obligaría a capturar la ventana en OBS y a recortar o encajar. Una «Fuente de navegador» local se coloca y se escala libremente, tiene fondo transparente y es independiente de la ventana privada.
*Alternativa descartada:* quitar `WDA_EXCLUDEFROMCAPTURE` con una opción, porque reintroduce el problema del OCR.

### D2. Servidor (`stream/server.py`)
`StreamServer(state_provider)` envuelve un `ThreadingHTTPServer` ligado a `127.0.0.1`, que corre en un hilo daemon. `start(port) -> bool` devuelve `False` si el puerto está ocupado (`OSError`), y `stop()` lo cierra. El manejador:
- solo implementa `do_GET`; el resto de métodos da 501, como en `BaseHTTPRequestHandler`;
- comprueba que `Host` sea `localhost:<puerto>` o `127.0.0.1:<puerto>`, y si no, responde 403. Esto protege frente a *DNS rebinding* desde páginas web;
- `/` sirve `index.html`, y `/card.css` y `/card.js` su archivo. Esa lista fija es la única que se sirve (`importlib.resources`), sin rutas construidas a partir de la petición. `/state` devuelve el JSON del estado y cualquier otra ruta, 404;
- cabeceras: `Cache-Control: no-store`, `X-Content-Type-Options: nosniff` y `Content-Security-Policy: default-src 'self'`; sin CORS;
- sin registro por petición (`log_message` silenciado).

El estado se guarda en `StreamState` (con un candado): `publish(cards)`, `set_visible(bool)` y `snapshot() -> dict` con `seq`, `visible`, `mode` y `cards`. `seq` crece con cada cambio.

### D3. Textos compartidos (`core/card_text.py`)
`ability_effect_lines(view, type_name, lang)` y `matchup_note(effect, type_name, lang)` salen de `Overlay` y los usan el overlay y el payload. Así los textos coinciden por construcción.

### D4. Payload (`stream/payload.py`)
`build_cards(pokedex, rivals, own, levels, own_moves, probable, mode, lang) -> list[dict]` es una función pura. Genera datos ya listos para mostrar: nombres, textos de multiplicador, colores de tipo (`theme.TYPE_COLORS`) y si el texto es oscuro (`DARK_TEXT_TYPES`). El JS no repite ninguna regla del juego. Las secciones son `header`, `types`, `capture`, `versus`, `moves`, `weaknesses`, `resistances` (solo en Competitivo), `immunities`, `ability_lines`, `stats` y `total` (Competitivo) y `evolution`. Los títulos van en español, como la ficha privada; el change de la interfaz en inglés los traducirá.

### D5. Página (`stream/static/`)
`card.js` consulta `/state` cada 400 ms y solo vuelve a dibujar cuando cambia `seq`. Si `visible` es falso, hace una animación de salida. Si llegan tarjetas nuevas, una de entrada (deslizar y fundido, 250 ms). La escala sale de `?scale` (limitada a 0,5-3) y se aplica con `transform: scale()` sobre un contenedor anclado arriba a la izquierda. `html` y `body` son transparentes. La tipografía es la del sistema (Segoe UI) y no se cargan recursos externos, conforme a la CSP.

### D6. Integración en la app
- `Config` añade `stream_enabled = False`, `stream_port = 17320`, `stream_card_mode = "normal"` y `hotkey_toggle_stream = "Ctrl+Alt+S"`, con validación de puerto 1024-65535 y modo en `MODES`.
- `App._apply_stream(config)` arranca, para o reinicia el servidor según la configuración. Se llama al arrancar y en `apply_config`. Si el puerto está ocupado, avisa.
- `_show_battle` construye el payload con las mismas vistas, niveles y movimientos que la ficha privada y lo publica con `visible = True`.
- `Action.HIDE` (fin del combate) llama a `set_visible(False)`. `hide_overlay` (clic o atajo de ocultar) no lo hace.
- `toggle_stream_card` alterna la visibilidad, sin cambiar nada si no hay tarjetas.
- La bandeja añade la casilla «Modo stream» (señal `stream_toggled`) y «Copiar URL para OBS» (`QGuiApplication.clipboard()`).

### D7. Empaquetado
`battlelens.spec` añade `stream/static/*` a `datas`, y `--self-test` comprueba que la página se puede leer desde el paquete.

## Risks / Trade-offs

- [Puerto ocupado por otra aplicación] → Aviso con el puerto y opción de cambiarlo en Ajustes.
- [El cortafuegos de Windows pregunta] → No debería, porque solo se escucha en `127.0.0.1`. Se comprobará en la validación manual.
- [Sondeo cada 400 ms] → Coste despreciable (un JSON de pocos KB en local) y más tolerante que una conexión persistente si OBS recarga la fuente.

## Migration Plan

Las claves nuevas tienen valores por defecto, así que las configuraciones existentes se cargan con el modo stream desactivado.

## Open Questions

Ninguna.
