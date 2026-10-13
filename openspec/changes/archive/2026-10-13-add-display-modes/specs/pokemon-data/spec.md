## MODIFIED Requirements

### Requirement: Generación del dataset
El proyecto SHALL incluir un script (`tools/build_dataset.py`) que descargue los CSV públicos de PokéAPI y genere un único archivo `pokedex.json` con, por especie: número de Pokédex nacional, generación de introducción, nombres en en/es/fr/de/it, tipos de la forma por defecto, estadísticas base (PS, Ataque, Defensa, At. Esp., Def. Esp., Velocidad), habilidades (normales y oculta) con sus nombres, los tipos que tuvo en generaciones anteriores y sus formas regionales (Alola, Galar, Hisui, Paldea) con sus propios nombres, tipos, estadísticas y habilidades. También incluye, por especie y forma, el peso, la altura, los EVs que da al ser derrotado y, por especie, el ratio de captura, la especie de la que evoluciona, la cadena evolutiva y la condición de su evolución (nivel, objeto, intercambio, amistad, momento del día). El script MUST generar además `learnsets.json` con los movimientos que aprende cada especie y forma por subida de nivel en cada juego (deduplicando las listas idénticas) y los datos de cada movimiento (nombres, tipo, categoría, potencia, precisión, PP y prioridad). Además MUST incluir la descripción más reciente de cada habilidad en en/es/fr/de/it, los nombres de los objetos que intervienen en evoluciones y la tabla de eficacia de tipos actual, las diferencias de eficacia de generaciones anteriores, la generación en que apareció cada tipo, los nombres de los tipos y el catálogo de juegos.

#### Scenario: Generación completa
- **WHEN** se ejecuta el script con conexión a Internet
- **THEN** se genera `pokedex.json` con todas las especies publicadas en PokéAPI, la tabla completa de 18×18 tipos, las formas regionales y el catálogo de juegos

#### Scenario: Formas regionales incluidas
- **WHEN** se consulta en el dataset la especie #263 (Zigzagoon)
- **THEN** tiene una forma `galar` llamada «Zigzagoon de Galar» en español, de tipos Siniestro/Normal

#### Scenario: Descarga fallida
- **WHEN** falla la descarga de algún CSV
- **THEN** el script termina con código de salida distinto de 0 y no sobrescribe un `pokedex.json` existente

#### Scenario: Datos de captura y evolución
- **WHEN** se consulta en el dataset la especie #760 (Bewear)
- **THEN** su ratio de captura es 70, evoluciona de #759 (Stufful) por subida de nivel con nivel mínimo 27

#### Scenario: Datos competitivos
- **WHEN** se consulta Stufful (#759) en los datos generados
- **THEN** pesa 6,8 kg, da 1 EV de Ataque y aprende Placaje a nivel 1 en `sword-shield`

## ADDED Requirements

### Requirement: Carga diferida de movimientos
El sistema SHALL cargar `learnsets.json` solo la primera vez que se necesite (al mostrar una ficha en modo competitivo) y MUST NOT retrasar el arranque por ello. Si falta el archivo, el modo competitivo omite los movimientos e indica el motivo.

#### Scenario: Arranque en modo normal
- **WHEN** la aplicación arranca en modo normal
- **THEN** `learnsets.json` no se carga
