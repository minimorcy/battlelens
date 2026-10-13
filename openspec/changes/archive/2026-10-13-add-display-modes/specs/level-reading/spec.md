## ADDED Requirements

### Requirement: Lectura del nivel
El sistema SHALL extraer el nivel (1-100) de las lecturas de OCR de cada región: primero, un número precedido de «Nv», «Lv», «N», «L» o «:L» (con o sin punto); si no lo hay, un número suelto al final del texto. Se usan todas las lecturas hechas sobre esa región, empezando por la de mejor coincidencia. Si no se encuentra, el nivel es desconocido.

#### Scenario: Formatos de nivel
- **WHEN** las lecturas son "Stufful Nv. 10", "PIDGEY Lv5", "RATTATA :L12" o "Stufiul 10"
- **THEN** los niveles son 10, 5, 12 y 10

#### Scenario: Sin nivel
- **WHEN** la región solo contiene el nombre ("PIDGEY")
- **THEN** el nivel es desconocido

#### Scenario: Valor imposible
- **WHEN** la lectura es "Stufful Nv. 410"
- **THEN** el nivel es desconocido
