## Context

El pipeline lee una sola región y la ficha muestra una sola especie. El detector automático compara especies (`int`). Las regiones adicionales son opcionales y no deben cambiar nada para los perfiles existentes.

## Goals / Non-Goals

**Goals:**
- Comparativa de tipos útil de un vistazo («¿le pego fuerte? ¿me pega fuerte?»).
- Combates dobles con dos tarjetas.
- Compatibilidad total con los perfiles de una sola región.

**Non-Goals:**
- Movimientos concretos de tu Pokémon (exigiría leer el menú de ataques). La comparativa usa sus tipos, es decir, ataques con STAB.
- Habilidades que cambian la eficacia (Levitación, Absorbe Agua…), objetos y el teratipo.
- Tu 2.º Pokémon en dobles (se puede añadir con el mismo mecanismo).

## Decisions

### D1. Regiones con nombre en el perfil
`Profile` añade `rival2_region: Region | None` y `own_region: Region | None` (claves JSON opcionales). Un método `regions()` devuelve un diccionario ordenado `{"rival": …, "rival2": …, "own": …}` con solo las regiones configuradas, y ese orden fija el de la huella y el de la lectura.
*Alternativa descartada:* una lista genérica de regiones con roles. Es más flexible, pero innecesaria con tres roles fijos y complica la interfaz.

### D2. `BattleReading` en el pipeline
`RecognitionPipeline.run` captura una vez, recorta cada región y llama a `read_crop` sobre cada recorte. Devuelve `RecognitionResult` con `match`/`species` (rival, por compatibilidad), `rival2` y `own` (`MatchResult | None`) y una huella combinada. `read_regions(crops)` se reutiliza en el modo automático.

### D3. Huella combinada
Se concatenan horizontalmente las huellas de 32×12 de cada región configurada. Como el perfil fija qué regiones hay, la forma es constante y `fingerprint_distance` sirve sin cambios. Un cambio solo en la región de tu Pokémon también dispara el reconocimiento.

### D4. Clave de combate genérica en el detector
`BattleDetector` deja de tratar «especie» como un entero y usa una clave hashable: la tupla `(rival, rival2, own)` de especies o `None`. `on_result(key)` muestra la ficha si la clave tiene algún rival y es distinta de la mostrada. Una clave sin ningún rival equivale a «no reconocido».

### D5. `core/matchup.py`
`matchup(own: SpeciesView, rival: SpeciesView, chart) -> Matchup(offense=[(tipo, mult)], defense=[(tipo, mult)], verdict)`. Usa la tabla de la generación del juego (`Pokedex.type_chart`). El veredicto compara `max(offense)` con `max(defense)`.

### D6. Overlay con varias tarjetas
`show_battle(rivals: list[SpeciesView], own: SpeciesView | None, rect)` coloca las tarjetas en un `QHBoxLayout`, de modo que la anchura pasa de 320 a 640 px en dobles. Cada tarjeta añade al final el apartado «Contra tu X» si hay `own`. `show_species` sigue existiendo para una sola especie.

### D7. Calibración de regiones opcionales
Se reutiliza `CalibrationDialog` con otro título y otra ayuda («Dibuja el nombre del 2.º rival» / «Dibuja el nombre de tu Pokémon»). El submenú «Regiones del perfil» agrupa recalibrar el rival, calibrar o quitar el 2.º rival y calibrar o quitar tu Pokémon. «Recalibrar perfil activo» pasa a ese submenú como «Recalibrar rival».

## Risks / Trade-offs

- [Tu Pokémon con apodo] → La región no se reconoce y la ficha se muestra sin comparativa. Está documentado. La alternativa de leer el sprite queda fuera de alcance.
- [Más OCR por reconocimiento] → Hasta 3 lecturas de 15-80 ms. Sigue por debajo de 500 ms.
- [La comparativa ignora habilidades y movimientos concretos] → Se presenta como orientación por tipos y está documentado.

## Migration Plan

No hay: los campos nuevos son opcionales.

## Open Questions

Ninguna.
