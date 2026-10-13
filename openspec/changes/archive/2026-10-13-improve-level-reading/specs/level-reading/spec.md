## MODIFIED Requirements

### Requirement: Lectura del nivel
El sistema SHALL extraer el nivel (1-100) de las lecturas de OCR de cada región: primero, un número precedido de «Nv», «Lv», «N», «L» o «:L» (con o sin punto); si no lo hay, un número suelto al final del texto. Se usan todas las lecturas hechas sobre esa región, empezando por la de mejor coincidencia. Detrás de un prefijo de nivel, las letras que el OCR confunde con dígitos MUST interpretarse como el dígito correspondiente (O, o, Q y D → 0; I, l, | e i → 1; Z y z → 2; S y s → 5; G y b → 6; B → 8) siempre que el resultado tenga al menos un dígito real o vaya precedido de «Nv»/«Lv». Si no se encuentra, el nivel es desconocido.

#### Scenario: Formatos de nivel
- **WHEN** las lecturas son "Stufful Nv. 10", "PIDGEY Lv5", "RATTATA :L12" o "Stufiul 10"
- **THEN** los niveles son 10, 5, 12 y 10

#### Scenario: Dígitos confundidos
- **WHEN** las lecturas son "Machop Nv. 1G", "Machop Nv. I6", "Machop Nv. 2O" o "Machop Lv.lS"
- **THEN** los niveles son 16, 16, 20 y 15

#### Scenario: Sin nivel
- **WHEN** la región solo contiene el nombre ("PIDGEY")
- **THEN** el nivel es desconocido

#### Scenario: Palabras que no son niveles
- **WHEN** la lectura es "NOSEPASS" o "Lombre"
- **THEN** el nivel es desconocido

#### Scenario: Valor imposible
- **WHEN** la lectura es "Stufful Nv. 410"
- **THEN** el nivel es desconocido

## ADDED Requirements

### Requirement: Búsqueda adicional del nivel
Si el nombre de una región se ha reconocido con puntuación 100 pero ninguna lectura contiene el nivel, el sistema SHALL probar hasta 3 variantes más de las pendientes (primero las de grises) y parar en cuanto una lectura contenga el nivel. Si sigue sin nivel, SHALL pasar por el OCR la mitad derecha del recorte en escala de grises, ampliada a 48 y 64 px de alto, y extraer el nivel de esas lecturas. Estas lecturas MUST NOT cambiar la especie reconocida.

#### Scenario: El nivel aparece en otra variante
- **WHEN** el recorte original da "Machop" (100) sin nivel y la siguiente variante de grises da "Machop Nv. 16"
- **THEN** el resultado es Machop con nivel 16 y no se prueban más variantes

#### Scenario: Nivel solo en la mitad derecha
- **WHEN** ninguna variante del recorte completo contiene el nivel y la mitad derecha ampliada da "Nv. 16"
- **THEN** el nivel es 16

#### Scenario: Región sin nivel
- **WHEN** la región solo contiene el nombre
- **THEN** se hacen como mucho 5 lecturas adicionales y el nivel es desconocido
