## MODIFIED Requirements

### Requirement: Generación del dataset
El proyecto SHALL incluir un script (`tools/build_dataset.py`) que descargue los CSV públicos de PokéAPI y genere un único archivo `pokedex.json` con, por especie: número de Pokédex nacional, generación de introducción, nombres en en/es/fr/de/it, tipos de la forma por defecto, estadísticas base (PS, Ataque, Defensa, At. Esp., Def. Esp., Velocidad), habilidades (normales y oculta) con sus nombres, los tipos que tuvo en generaciones anteriores y sus formas regionales (Alola, Galar, Hisui, Paldea) con sus propios nombres, tipos, estadísticas y habilidades. También incluye, por especie, el ratio de captura, la especie de la que evoluciona, la cadena evolutiva y la condición de su evolución (nivel, objeto, intercambio, amistad, momento del día). Además MUST incluir la descripción más reciente de cada habilidad en en/es/fr/de/it, los nombres de los objetos que intervienen en evoluciones y la tabla de eficacia de tipos actual, las diferencias de eficacia de generaciones anteriores, la generación en que apareció cada tipo, los nombres de los tipos y el catálogo de juegos.

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

## ADDED Requirements

### Requirement: Cadena evolutiva según el juego
El sistema SHALL calcular, para una especie y un juego opcional, su cadena evolutiva completa (desde la especie base hasta las últimas evoluciones, incluidas las ramas) agrupada en etapas, con la condición de cada evolución en el idioma de la interfaz. MUST omitir las especies introducidas en una generación posterior a la del juego. Las condiciones se expresan como: «Nv. N», el nombre del objeto, «Intercambio» (con el objeto equipado si lo hay), «Amistad» (con «de día» o «de noche» si aplica) o «Especial» para el resto.

#### Scenario: Cadena lineal
- **WHEN** se calcula la cadena de Charmeleon (#5)
- **THEN** es Charmander → Charmeleon (Nv. 16) → Charizard (Nv. 36)

#### Scenario: Ramas
- **WHEN** se calcula la cadena de Eevee (#133) sin juego
- **THEN** la segunda etapa incluye Vaporeon (Piedra Agua), Jolteon (Piedra Trueno) y Flareon (Piedra Fuego), entre otras

#### Scenario: Evoluciones posteriores al juego
- **WHEN** se calcula la cadena de Pikachu (#25) para el juego `red-blue`
- **THEN** es Pikachu → Raichu (Piedra Trueno), sin Pichu (Gen 2)

#### Scenario: Sin evolución
- **WHEN** se calcula la cadena de Tauros (#128)
- **THEN** la cadena tiene una sola etapa y la ficha no muestra el apartado de evolución

### Requirement: Dificultad de captura
El sistema SHALL clasificar el ratio de captura (1-255) en: «Fácil» (≥ 190), «Media» (≥ 75), «Difícil» (≥ 25) y «Muy difícil» (< 25).

#### Scenario: Clasificación
- **WHEN** se clasifican los ratios 255, 140, 45 y 3
- **THEN** son «Fácil», «Media», «Difícil» y «Muy difícil» respectivamente
