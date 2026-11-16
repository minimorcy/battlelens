## Context

`core/updates.py` ya hace peticiones HTTPS con `urllib` (con tiempo de espera y `User-Agent: BattleLens/<versión>`). Los datos del usuario viven en `storage.app_data_dir()`. El dataset (`data/pokedex.json`, generado por `tools/build_dataset.py` desde los CSV de PokéAPI) guarda el identificador de cada forma (`zigzagoon-galar`), pero no su número de Pokémon, que es el nombre de archivo de los sprites (`sprites/pokemon/<número>.png`, 96×96 con margen transparente). El servidor del modo stream solo sirve una lista fija de rutas.

## Goals / Non-Goals

**Goals:**
- Reconocer al Pokémon de un vistazo sin redistribuir imágenes con copyright.
- Que la descarga nunca retrase ni bloquee la ficha ni el reconocimiento.
- Funcionar sin conexión, simplemente sin imagen.

**Non-Goals:**
- Sprites animados, shiny o de una generación concreta (se usa el sprite por defecto).
- Descargar todos los sprites de golpe.
- Ilustraciones oficiales de alta resolución.

## Decisions

### D1. Número de Pokémon en el dataset
`build_dataset.py` añade `sprite_id` a cada especie (su número de Pokémon por defecto) y a cada forma (`pokemon.id` de PokéAPI; p. ej. 10174). `SpeciesView` lo expone y el cambio de forma (`Ctrl+Alt+F`) cambia también la imagen. Las formas cosméticas sin Pokémon propio usan el de la especie.

### D2. `core/sprites.py`
- La descarga validada y la escritura atómica reutilizan `fetch_png` de `core/remote_images.py` (creado en `add-type-icons`); aquí solo se añade el recorte y la caché por `sprite_id`.
- `SpriteCache(dir, fetch)`: `path(sprite_id) -> Path | None` devuelve el PNG ya recortado si existe; `request(sprite_id, callback)` lo descarga en un hilo (`QThreadPool` o `ThreadPoolExecutor` de 2 hilos) y llama a `callback` en el hilo de la interfaz (señal Qt).
- URL fija: `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{id}.png`; `sprite_id` MUST ser un entero; tiempo de espera de 5 s; tamaño máximo de 256 KB; se comprueba que sea un PNG válido.
- Recorte: se elimina el margen transparente (caja de los píxeles con alfa > 0) antes de guardar, para que la imagen quede centrada en el recuadro y no abajo a la izquierda como en el original. Con `QImage` (sin dependencias nuevas).
- Escritura atómica en `sprites/<id>.png`. Los fallos se recuerdan solo durante la sesión (no se reintenta en cada reconocimiento) y se registran en el log de depuración.

### D3. Cabecera
Recuadro de 60×60 px a la izquierda de los tipos, debajo del nombre (probado con capturas: a la izquierda del nombre, en la ficha Normal de 300 px los nombres largos con flechas de forma, como «Zigzagoon de Galar», y la línea de captura se cortaban), con un fondo radial teñido del primer tipo. El sprite recortado se escala para caber en 48×48 sin superar ×2, con escalado por vecino más próximo (`Qt.TransformationMode.FastTransformation`) para que el pixel art no se vea borroso. Sin imagen (desactivada, sin conexión o fallo), el recuadro no se reserva y la cabecera queda como en `improve-card-visuals`. Cuando llega una imagen con la ficha visible, se coloca en su recuadro sin redibujar la ficha ni moverla. Para que la altura no salte, el recuadro se reserva en cuanto se pide la descarga.

### D4. Ajustes
`overlay.sprites = false` por defecto (decidido el 2026-11-16, como `overlay.type_icons`: sin peticiones a GitHub que el usuario no haya pedido). En Ajustes: casilla «Mostrar la imagen del Pokémon (se descarga de PokéAPI la primera vez)». Al desactivarla no se hacen peticiones y la caché no se borra.

### D5. Stream
Ruta nueva `/sprite/<id>.png`: `id` se valida con una expresión regular `^\d{1,5}$` y solo se sirve un archivo que ya exista en la caché (404 en otro caso). El servidor nunca descarga y no se construyen rutas a partir de la petición más allá del entero validado. El payload incluye `sprite` (`/sprite/<id>.png` o `null`). La política CSP `default-src 'self'` ya permite la imagen.

### D6. Legal
El README (es/en) indica que las imágenes no se distribuyen con la app, que se descargan del repositorio de sprites de PokéAPI y que son propiedad de Nintendo/Creatures/GAME FREAK.

## Risks / Trade-offs

- [GitHub limita o cambia la URL del repositorio de sprites] → fallo silencioso sin imagen; la URL está en una constante.
- [Privacidad: GitHub ve la IP y qué Pokémon se consultan] → opción para desactivarlo, explicada en Ajustes y en el README.
- [La imagen llega tarde y desplaza la cabecera] → el recuadro se reserva al pedir la descarga (D3).
- [Retirada del repositorio de sprites] → la app sigue funcionando sin imágenes.

## Resolved Questions

- Imágenes desactivadas por defecto (`overlay.sprites = false`), igual que los iconos de tipo.
