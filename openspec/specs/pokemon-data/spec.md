# pokemon-data Specification

## Purpose
Dataset local de especies generado desde PokéAPI y cálculos derivados (eficacia de tipos), disponible sin conexión.
## Requirements
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

### Requirement: Carga del dataset sin conexión
La aplicación SHALL cargar el dataset desde el archivo `pokedex.json` incluido en el paquete y MUST NOT hacer peticiones de red para obtener datos de Pokémon. La única petición de red permitida en tiempo de ejecución es la comprobación de actualizaciones (spec `update-check`), que se puede desactivar.

#### Scenario: Sin conexión
- **WHEN** la aplicación arranca sin conexión a Internet
- **THEN** el reconocimiento y el overlay funcionan con normalidad

#### Scenario: Dataset ausente
- **WHEN** no existe `pokedex.json`
- **THEN** la aplicación muestra un error que indica cómo generarlo y termina

#### Scenario: Comprobación de actualizaciones desactivada
- **WHEN** `updates.check = false` y la aplicación se usa durante una sesión completa
- **THEN** no se realiza ninguna petición de red

### Requirement: Consulta de especie
El sistema SHALL devolver la ficha completa de una especie a partir de su número de Pokédex.

#### Scenario: Consulta válida
- **WHEN** se consulta la especie #6
- **THEN** se obtiene Charizard, tipos Fuego/Volador, estadísticas base 78/84/78/109/85/100 (total 534) y habilidades Mar Llamas y Poder Solar (oculta)

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

### Requirement: Carga diferida de movimientos
El sistema SHALL cargar `learnsets.json` solo la primera vez que se necesite (al mostrar una ficha en modo competitivo) y MUST NOT retrasar el arranque por ello. Si falta el archivo, el modo competitivo omite los movimientos e indica el motivo.

#### Scenario: Arranque en modo normal
- **WHEN** la aplicación arranca en modo normal
- **THEN** `learnsets.json` no se carga

### Requirement: Habilidades según la generación
El dataset SHALL incluir, por Pokémon (especie y forma), las habilidades que tuvo en generaciones anteriores, por hueco (1, 2 u oculta), con la última generación en que estuvieron vigentes; un hueco puede estar vacío. Al resolver la vista de un juego, el sistema MUST usar, para cada hueco, la habilidad vigente en la generación del juego.

#### Scenario: Gengar en Platino
- **WHEN** se resuelve la especie #94 (Gengar) para el juego `platinum` (Gen 4)
- **THEN** su única habilidad es Levitación

#### Scenario: Gengar en la generación actual
- **WHEN** se resuelve la especie #94 sin juego
- **THEN** su habilidad es Cuerpo Maldito

### Requirement: Eficacia defensiva con habilidades
Al resolver la vista de un juego, el sistema SHALL ajustar los grupos de eficacia defensiva con los efectos **seguros** de sus habilidades: un efecto es seguro si todas las habilidades posibles de la vista dan el mismo multiplicador para ese tipo de ataque y este difiere del de los tipos. Si solo algunas habilidades cambian el multiplicador, el efecto es **posible** y MUST NOT cambiar los grupos. La vista MUST incluir la lista de efectos seguros y posibles con la habilidad que los causa. Los efectos que no dan un multiplicador de los grupos (por ejemplo, ×0,75 a los supereficaces) se indican sin mover el tipo.

#### Scenario: Flygon
- **WHEN** se resuelve Flygon (Tierra/Dragón, solo Levitación) sin juego
- **THEN** Tierra aparece en ×0, y la vista indica el efecto seguro «Levitación: Tierra ×0»

#### Scenario: Bronzong en Platino
- **WHEN** se resuelve Bronzong (Acero/Psíquico; Levitación o Ignífugo) para el juego `platinum`
- **THEN** Tierra sigue en ×2 y Fuego en ×2, y la vista indica los efectos posibles «Levitación: Tierra ×0» e «Ignífugo: Fuego ×1»

#### Scenario: Shedinja
- **WHEN** se resuelve Shedinja (Bicho/Fantasma, solo Superguarda) sin juego
- **THEN** solo Fuego, Volador, Roca, Fantasma y Siniestro le afectan (×2), y el resto de tipos aparece en ×0

