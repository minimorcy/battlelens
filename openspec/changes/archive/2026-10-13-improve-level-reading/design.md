## Context

`read_crop` recorre `preprocess_variants(crop)` (original, 3 de grises y 14 binarizadas) y para con la primera coincidencia de 100. `CropReading.level` llama a `extract_level` sobre todas las lecturas hechas. Con la captura real de Espada (`site/assets/gameplay.jpg`), el recorte original ya da «Machop@ Nv. 16» a 1600, 1920, 2560 y 3840 px de ancho, así que la fuente grande por sí sola no basta para fallar. Los fallos observados vienen de que la única lectura hecha (por la parada temprana) no traiga el nivel, o lo traiga con letras en lugar de dígitos.

## Goals / Non-Goals

**Goals:**
- Más probabilidad de leer el nivel sin empeorar el reconocimiento del nombre.
- Coste acotado cuando la región no incluye el nivel.

**Non-Goals:**
- Una región separada para el nivel (exige otra calibración).
- OCR de solo dígitos (Windows.Media.Ocr no admite restringir el juego de caracteres).

## Decisions

### D1. Confusiones solo tras un prefijo
`extract_level` añade un patrón que busca un prefijo (`nv`, `lv`, `niv`, `n`, `l`, `:l`) seguido de 1-3 caracteres del conjunto de dígitos y confusiones, los traduce y acepta el valor si está en 1-100. Para no leer niveles en nombres («Lombre», «NOSEPASS»), el patrón exige que el prefijo sea «Nv»/«Lv» (con o sin punto) o que el grupo contenga al menos un dígito real. El orden de prueba es: prefijo con dígitos (actual), prefijo con confusiones (nuevo) y número suelto al final (actual).

### D2. Parada temprana condicionada
`read_crop` sigue igual hasta alcanzar 100. A partir de ahí, si `extract_level(lecturas)` es `None`, prueba como mucho `LEVEL_EXTRA_VARIANTS = 3` variantes pendientes, empezando por las de grises que aún no se hayan probado, y para en cuanto aparece el nivel. Las lecturas extra se añaden a `readings`, pero no cambian `best`: la especie ya tiene 100.

### D3. Mitad derecha ampliada
Si después sigue sin nivel, `preprocess.level_variants(crop)` devuelve la mitad derecha del recorte en grises a `LEVEL_HEIGHTS = (48, 64)` px con margen blanco, y sus lecturas se añaden a `readings`. Se aplica solo si el nombre se reconoció con 100: si no se reconoce, el nivel no sirve.

### D4. Coste
En el peor caso (región sin nivel) son 3 + 2 = 5 lecturas más, de unos 10-20 ms cada una. La detección automática solo lee las regiones cuando cambia la huella, así que no se repite en cada tick.

## Risks / Trade-offs

- [Falsos niveles por las confusiones] → Solo tras un prefijo y con las restricciones de D1. Los tests incluyen nombres con «L»/«N» iniciales.
- [Sin muestras reales del fallo] → Se valida con tests sintéticos (OCR simulado) y con una comprobación manual en Espada.

## Migration Plan

Nada que migrar.

## Open Questions

Ninguna.
