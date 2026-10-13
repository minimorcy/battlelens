## MODIFIED Requirements

### Requirement: Ejecución del OCR
El sistema SHALL ejecutar el OCR nativo de Windows sobre cada variante con los idiomas del perfil, en orden y quedándose con el primer resultado no vacío de cada variante. Después MUST conservar la lectura cuya coincidencia (ver «Coincidencia aproximada multilingüe») tenga mayor puntuación, y SHALL dejar de probar variantes en cuanto una alcance 100 y alguna lectura contenga el nivel; si no hay nivel, se aplica la búsqueda adicional del nivel (spec `level-reading`).

#### Scenario: Mejor variante
- **WHEN** las variantes producen las lecturas "~~", "P1DGEY Nv. 5" y "PIDGEY Nv. 5"
- **THEN** el resultado es Pidgey con puntuación 100 y no se evalúan más variantes

#### Scenario: Idioma de OCR no instalado
- **WHEN** ninguno de los idiomas del perfil tiene paquete de OCR instalado en Windows
- **THEN** el sistema muestra un error que indica qué paquete de idioma instalar
