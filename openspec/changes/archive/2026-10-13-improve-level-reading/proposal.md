## Why

En juegos 3D (Espada/Escudo) el nivel del rival a veces no se lee, y sin nivel el modo Competitivo pierde los movimientos probables y los rangos de estadísticas. Hay dos causas en el código:
1. **Parada temprana:** en cuanto una variante reconoce el nombre con puntuación 100, se dejan de probar variantes. Con la fuente grande de los juegos 3D suele ser el recorte original, y si esa lectura no trae el nivel (el OCR omite o corta «Nv. 16» al otro extremo del recuadro), no se intenta nada más.
2. **Confusiones del OCR:** con fuentes estilizadas, los dígitos se leen como letras («Nv. 1G», «Nv. I6», «Nv. 2O»), y `extract_level` las descarta.

## What Changes

- **Seguir buscando el nivel:** si la mejor lectura llega a 100 pero ninguna lectura contiene el nivel, se prueban hasta 3 variantes más (las de grises, las mejores para texto suavizado) y se para en cuanto aparece.
- **Lectura ampliada del nivel:** si aun así no hay nivel, se pasa por el OCR la mitad derecha del recorte (donde va el nivel en todos los juegos), ampliada a dos alturas.
- **Dígitos confundidos:** detrás de un prefijo de nivel («Nv», «Lv»…), las letras que el OCR confunde con dígitos se interpretan como el dígito: O/o/Q/D → 0, I/l/|/i → 1, Z/z → 2, S/s → 5, G/b → 6, B → 8.
- Se documenta en `docs/manual-validation.md` una comprobación con Espada a pantalla completa.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `level-reading`: confusiones de dígitos tras el prefijo y lectura ampliada de la mitad derecha.
- `name-recognition`: la parada al llegar a 100 espera al nivel durante unas pocas variantes más.

## Impact

- **Código:** `core/normalize.py` (`extract_level`), `pipeline.py` (`read_crop`) y `vision/preprocess.py` (variantes del nivel).
- **Rendimiento:** solo cuando el nombre se reconoce y no se ve el nivel, hasta 5 lecturas de OCR más (unos 50-100 ms). Sigue por debajo de 500 ms.
