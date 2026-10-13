## MODIFIED Requirements

### Requirement: Generación del dataset
El proyecto SHALL incluir un script (`tools/build_dataset.py`) que descargue los CSV públicos de PokéAPI y genere un único archivo `pokedex.json` con, por especie: número de Pokédex nacional, generación de introducción, nombres en en/es/fr/de/it, tipos de la forma por defecto, estadísticas base (PS, Ataque, Defensa, At. Esp., Def. Esp., Velocidad), habilidades (normales y oculta) con sus nombres, los tipos que tuvo en generaciones anteriores y sus formas regionales (Alola, Galar, Hisui, Paldea) con sus propios nombres, tipos, estadísticas y habilidades. Además MUST incluir la tabla de eficacia de tipos actual, las diferencias de eficacia de generaciones anteriores, la generación en que apareció cada tipo, los nombres de los tipos y el catálogo de juegos.

#### Scenario: Generación completa
- **WHEN** se ejecuta el script con conexión a Internet
- **THEN** se genera `pokedex.json` con todas las especies publicadas en PokéAPI, la tabla completa de 18×18 tipos, las formas regionales y el catálogo de juegos

#### Scenario: Formas regionales incluidas
- **WHEN** se consulta en el dataset la especie #263 (Zigzagoon)
- **THEN** tiene una forma `galar` llamada «Zigzagoon de Galar» en español, de tipos Siniestro/Normal

#### Scenario: Descarga fallida
- **WHEN** falla la descarga de algún CSV
- **THEN** el script termina con código de salida distinto de 0 y no sobrescribe un `pokedex.json` existente

### Requirement: Eficacia de tipos defensiva
El sistema SHALL calcular, para una combinación de tipos y una generación (por defecto, la actual), el multiplicador de daño recibido de cada tipo de ataque existente en esa generación (producto de los multiplicadores individuales según la tabla de esa generación) y MUST agruparlos en ×4, ×2, ×½, ×¼ y ×0.

#### Scenario: Doble debilidad
- **WHEN** se calcula la eficacia para Charizard (Fuego/Volador) en la generación actual
- **THEN** Roca aparece en ×4; Agua y Eléctrico en ×2; Fuego, Lucha, Acero y Hada en ×½; Planta y Bicho en ×¼; Tierra en ×0

#### Scenario: Inmunidad
- **WHEN** se calcula la eficacia para Gengar (Fantasma/Veneno)
- **THEN** Normal y Lucha aparecen en ×0

#### Scenario: Tabla de la Gen 1
- **WHEN** se calcula la eficacia en la generación 1
- **THEN** solo intervienen los 15 tipos de esa generación (sin Siniestro, Acero ni Hada) y Fantasma no afecta a Psíquico (×0)

#### Scenario: Acero antes de la Gen 6
- **WHEN** se calcula la eficacia para un Pokémon de tipo Acero en la generación 5
- **THEN** Fantasma y Siniestro le hacen ×½

## ADDED Requirements

### Requirement: Vista de la especie según el juego
El sistema SHALL resolver, para una especie y un juego opcional, la vista que se muestra: la forma regional del juego si la especie la tiene (si no, la forma por defecto); los tipos vigentes en la generación del juego; las habilidades solo a partir de la Gen 3 y la habilidad oculta solo a partir de la Gen 5; y la lista de las otras formas regionales de la especie con sus tipos. Sin juego, se usa la forma por defecto y la generación actual.

#### Scenario: Zigzagoon en Espada
- **WHEN** se resuelve la especie #263 para el juego `sword-shield`
- **THEN** la vista es «Zigzagoon de Galar», de tipos Siniestro/Normal, con Lucha en ×4, Psíquico y Fantasma en ×0, y la forma original (Normal) en «otras formas»

#### Scenario: Clefairy antes de la Gen 6
- **WHEN** se resuelve la especie #35 para el juego `black-white` (Gen 5)
- **THEN** su tipo es Normal

#### Scenario: Clefairy en la generación actual
- **WHEN** se resuelve la especie #35 sin juego
- **THEN** su tipo es Hada

#### Scenario: Habilidades en la Gen 1
- **WHEN** se resuelve cualquier especie para el juego `red-blue`
- **THEN** la vista no incluye habilidades

#### Scenario: Juego sin formas regionales
- **WHEN** se resuelve la especie #263 para el juego `emerald`
- **THEN** la vista es la forma original (Normal) y en «otras formas» aparece la de Galar
