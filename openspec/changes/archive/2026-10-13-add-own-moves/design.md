## Context

Las regiones de nombres (`Profile.regions()`: rival, rival2 y own) forman la huella combinada que usa `BattleDetector` para decidir cuándo reconocer y cuándo ocultar. El menú de ataques solo está visible mientras eliges un movimiento. El resto del tiempo esa zona muestra el escenario, animaciones o textos del combate, así que incluirla en esa huella provocaría ocultaciones falsas. `learnsets.json` solo trae los movimientos que se aprenden por nivel. Windows OCR devuelve las líneas unidas con espacios.

## Goals / Non-Goals

**Goals:**
- Saber qué movimientos lleva tu Pokémon sin escribirlos, y cuánto hace cada uno al rival.
- No empeorar la detección del combate.

**Non-Goals:**
- Tipos y potencias de los movimientos en generaciones anteriores (Mordisco era Normal en la Gen 1).
- Movimientos con tipo variable (Poder Oculto, Meteorobola, teracristalización).
- Cálculo de daño, precisión y PP restantes.

## Decisions

### D1. Región `moves_region` aparte
`Profile` añade `moves_region: Region | None`. `with_role_region("moves", …)` la cambia, y `regions()` **no** la incluye: las regiones de nombres, la huella y la lectura de nombres no cambian. El submenú «Regiones del perfil» añade «Calibrar / Recalibrar / Quitar menú de ataques». El diálogo pide «el menú de ataques (los 4 movimientos)».

### D2. Catálogo y coincidencia (`core/moves.py`)
`build_learnsets` guarda todos los movimientos de `moves.csv` que tienen tipo. `Learnsets.move(identifier) -> Move | None` (con `level = 0`) y `Learnsets.all_moves()`.

`MoveMatcher(moves)` indexa el nombre normalizado de cada movimiento en los 5 idiomas, sin acentos ni espacios y en mayúsculas (`clean_text`, que se extrae de `normalize._clean`). `match(text) -> list[Move]` hace lo siguiente:
1. Separa el texto en palabras.
2. Para cada ventana de 1-3 palabras con 4 o más caracteres normalizados, busca la mejor coincidencia (`rapidfuzz.process.extractOne`, `fuzz.ratio`).
3. Ordena los candidatos por puntuación (y, a igualdad, por la ventana más larga) y escoge vorazmente los que no se solapan ni repiten movimiento, con puntuación ≥ `MOVE_THRESHOLD = 80` (un error en palabras de 5-6 letras), hasta 4.
4. Devuelve el resultado en el orden en que aparece en el texto.

`read_moves(crop, ocr, matcher, languages)` prueba las variantes del menú (`preprocess.moves_variants`): el original; ampliadas ×2 en gris y binarizadas; en gris a 48, 64 y 96 px de alto; binarizada a 64 px, y cada mitad en gris a 48 px. Las mitades hacen falta porque, con la rejilla 2×2 pixelada de GBA, el OCR de Windows a veces omite la columna izquierda. Combina los movimientos de todas las variantes: se queda con los 4 que aparecen en más variantes y los ordena por orden de aparición. Para antes de tiempo si ya tiene 4 vistos al menos dos veces. La lectura es válida con 2 o más (`MIN_MOVES = 2`).

### D3. Vigilante propio (`RegionWatcher`)
Es lógica pura en `core/detection.py`. `on_frame(fp) -> bool` devuelve `True` cuando la huella lleva `STABLE_TICKS` ciclos estable y difiere de la última leída (`> CHANGE_THRESHOLD`), y `attempted(fp)` la marca como leída. `App._capture_crop` recorta también el menú y calcula su huella. `_on_watch_frame` consulta al vigilante y, si toca, lanza la lectura en el pool con su propio indicador `_moves_busy`, sin bloquear la del rival. Al reconocer a mano, `RecognitionPipeline.run` lee el menú si el perfil lo tiene y el pipeline tiene `move_matcher`, y lo devuelve en `RecognitionResult.moves`.

### D4. Memoria (`MoveMemory`)
`moves.json` guarda `{perfil: {especie: [identificadores]}}`, se escribe con `write_json_atomic` y los errores de lectura se ignoran (se empieza vacío). `store(profile_id, species_id, moves) -> bool` indica si cambió algo. La especie es la de tu Pokémon en `_last_battle`. Si no la hay, la lectura se descarta.

### D5. Overlay
`show_battle(..., own_moves: list[Move] | None, own_moves_probable: bool)`. La app calcula la lista con `MoveMemory`, o con `Learnsets.probable_moves(own.pokemon, own_level, …)` si no hay memoria y se conoce el nivel. Cada tarjeta añade «Tus movimientos» después de «Contra tu X», con una fila por movimiento: pastilla de tipo, nombre (`own-move`) y, para los no de estado, `effective_multiplier(chart, move.type, rival)` (`own-move-vs-rival`) en verde si es > 1, en rojo si es < 1 y con «*» si hay efectos posibles. Los de estado muestran «Estado». Se cargan los learnsets (diferidos) solo si hay que mostrar el apartado.

## Risks / Trade-offs

- [Falsos positivos al leer textos del combate] → Mínimo 2 movimientos, umbral 80, ventanas de ≥ 4 caracteres y lectura solo con la imagen estable.
- [El menú no se lee y se queda la memoria vieja] → Se sustituye en cuanto se lee el menú de nuevo. Los probables solo se usan sin memoria.
- [Coste de cargar los learnsets (~1 MB) en modo Normal] → Solo si se conoce tu Pokémon. Es una carga única en segundo plano dentro del primer dibujo.

## Migration Plan

Los perfiles sin `moves_region` se cargan igual. `moves.json` se crea al guardar la primera lectura. Se regenera `learnsets.json`.

## Open Questions

Ninguna.
