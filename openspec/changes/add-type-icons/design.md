## Context

Todos los tipos de la ficha pasan por `_pill()` en `ui/overlay.py` (sólida en la cabecera, suave en el resto). La tabla de tipos (`ui/type_chart.py`) y la ficha del stream (`stream/static/card.js`) pintan los suyos aparte. El dataset ya guarda el número de PokéAPI de cada tipo (`types[<id>].id`, 1 = Normal … 18 = Hada). `core/updates.py` ya hace HTTPS con `urllib`, tiempo de espera y `User-Agent: BattleLens/<versión>`. El cambio `add-pokemon-sprites`, aún sin implementar, necesita la misma descarga validada a una caché.

En el repositorio de PokéAPI, los iconos de la 3.ª a la 7.ª generación son solo el nombre del tipo en inglés pixelado. Desde la 8.ª hay además una versión `small` de 60×60 con el símbolo sin texto.

## Goals / Non-Goals

**Goals:**
- Reconocer los tipos de un vistazo en cualquier idioma de la ficha.
- No redistribuir imágenes con copyright ni bloquear nunca la ficha.
- Funcionar sin conexión, con las etiquetas de siempre.

**Non-Goals:**
- Iconos distintos por generación o juego (decidido con el usuario: símbolo moderno en todos).
- Tipo Astral, Tera o «???».
- Iconos en la ventana de Ajustes, en el buscador o en el asistente de presets.

## Decisions

### D1. Un solo juego de símbolos
Se usa `generation-viii/sword-shield/small/<id>.png` para todos los juegos. Alternativas: los iconos de cada generación (texto en inglés en 3.ª-7.ª, tamaños de 32×14 a 200×44) o solo donde hay símbolo (sin efecto en GBA, DS y 3DS). El símbolo se entiende en cualquier idioma y todos tienen el mismo tamaño. El Hada existe en este juego, así que cubre todas las generaciones. Los tipos que no existían en un juego antiguo no aparecen en su ficha, así que no hace falta filtrar.

### D2. `core/remote_images.py`, compartido con los sprites
- `fetch_png(url, dest, max_bytes)`: descarga con tiempo de espera de 5 s y el `User-Agent` de `updates.py`, comprueba la firma PNG y que `QImage` la carga, y escribe en `dest.tmp` y luego `os.replace`. Lanza excepción en cualquier fallo.
- `TypeIcons(dir)`: `complete()` dice si están los 18. `ensure(callback)` descarga en un `ThreadPoolExecutor` de 2 hilos los que falten y avisa en el hilo de la interfaz (señal Qt) cuando termina. Los fallos se apuntan en el log de depuración y no se reintentan en la sesión. `pixmap(type_id, size)` devuelve el icono escalado con suavizado (no es pixel art) y lo guarda en memoria por tamaño.
- `add-pokemon-sprites` reutilizará `fetch_png` en lugar de escribir su propia descarga. Hay que actualizar su `design.md` (D2) para que lo diga.

### D3. Todo o nada
Los iconos se usan solo si están los 18 (spec `type-icons`). Mezclar iconos y etiquetas en una misma ficha mientras llegan sería más confuso que esperar unos segundos la primera vez.

### D4. Dibujo en la ficha
`_pill()` recibe la fuente de iconos del `Overlay`. Si están disponibles, devuelve un `QLabel` con el pixmap (22 px en el resto de secciones y 28 px en la cabecera), `setAccessibleName` y `setToolTip` con el nombre del tipo. Así las 15 llamadas actuales no cambian. Se mantiene el ancho fijo donde lo hay (columna de tipo de los movimientos), con el icono centrado. Al llegar los iconos, o al cambiar la opción, se redibuja la última ficha, como ya se hace al cambiar de idioma.

### D5. Tabla de tipos y stream
- `TypeChartWindow` recibe los pixmaps y los usa en las cabeceras, con el nombre en el tooltip.
- `payload.py` añade `icon: "/type-icon/<id>.png"` a cada tipo cuando están disponibles. `server.py` añade la ruta validada con `^\d{1,2}$`, que solo lee de `type-icons/`, y `card.js` pinta `<img alt="<nombre>">` en lugar de la pastilla. La CSP `default-src 'self'` ya lo permite.

### D6. Legal
El README (es/en) indica que los iconos no se distribuyen con la app, que se descargan del repositorio de PokéAPI y que son propiedad de Nintendo/Creatures/GAME FREAK. Comparte el aviso con los sprites.

## Risks / Trade-offs

- [El icono solo no dice el nombre a quien no conoce los símbolos] → la opción está desactivada por defecto, y el nombre sale en el tooltip y en la descripción accesible.
- [GitHub cambia la ruta o limita las peticiones] → fallo silencioso con etiquetas. La URL está en una constante.
- [Privacidad: GitHub ve la IP] → solo 18 peticiones, una vez, y únicamente si el usuario activa la opción. Se explica en Ajustes y en el README.
- [Iconos de 22 px al lado de multiplicadores de texto] → se revisa con capturas de las fichas Normal, Competitiva y doble antes de cerrar.

## Open Questions

- ¿La cabecera lleva solo el icono o icono y nombre? Se decide con la primera captura.
