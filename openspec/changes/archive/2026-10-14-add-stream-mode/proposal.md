## Why

BattleLens está pensado para jugar, pero queremos que lo prueben streamers, y la ficha no sale en el directo: la ventana se excluye de la captura de pantalla a propósito, para que BattleLens no se lea a sí mismo cuando copia la pantalla del emulador. Un streamer necesita que su público vea la ficha sin que cambie nada para quien juega sin emitir.

## What Changes

- **Modo stream opcional** (desactivado por defecto), que se activa desde la bandeja o desde Ajustes. Con él desactivado, BattleLens funciona exactamente igual que ahora.
- **Fuente de navegador para OBS:** con el modo stream activo, BattleLens sirve en `http://localhost:<puerto>/` (por defecto 17320, solo en el propio PC) una página con la ficha sobre fondo transparente, que se añade a la escena de OBS como «Fuente de navegador». Se actualiza sola con cada rival, entra con una animación, se oculta al terminar el combate y admite `?scale=` para ajustar el tamaño.
- **Contenido de la ficha del stream:** la misma información que la privada (tipos, captura, «Contra tu X», tus movimientos, debilidades, efectos de habilidades, evolución y, en modo Competitivo, nivel, resistencias y estadísticas), en su propio modo de ficha (Normal por defecto), independiente del de la ficha privada.
- **Las dos fichas a la vez:** la privada sigue funcionando y no aparece en la captura. Cerrarla con un clic no oculta la del stream.
- **Nuevo atajo `Ctrl+Alt+S`** («Mostrar/ocultar ficha del stream»), para quitarla de la escena en un momento sin tocar OBS.
- **Bandeja:** «Modo stream» (activar o desactivar) y «Copiar URL para OBS».
- **Ajustes:** sección «Modo stream» con el interruptor, el puerto y el modo de su ficha.

## Capabilities

### New Capabilities
- `stream-mode`: modo stream, servidor local de la fuente para OBS, contenido y visibilidad de la ficha del stream.

### Modified Capabilities
- `app-settings`: sección «Modo stream» y atajo nuevo.
- `battle-overlay`: atajo para mostrar u ocultar la ficha del stream y opciones de la bandeja.

## Impact

- **Código:** nuevo paquete `stream/` (`payload.py`, `server.py`, `static/` con `index.html`, `card.css` y `card.js`). Además, nuevo `core/card_text.py` con los textos compartidos de la ficha, que salen de `ui/overlay.py`, y cambios en `core/config.py`, `app.py`, `ui/tray.py`, `ui/settings.py` y `packaging/battlelens.spec`.
- **Red:** un servidor HTTP solo en `127.0.0.1`, solo con el modo stream activo, con lectura únicamente (GET) y comprobación de la cabecera `Host`. La comprobación de actualizaciones sigue siendo la única conexión saliente.
- **Dependencias:** ninguna nueva (`http.server` de la biblioteca estándar).
- **Configuración:** nueva sección `[stream]` y atajo `hotkeys.toggle_stream`, con valores por defecto.
