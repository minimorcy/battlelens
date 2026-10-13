## ADDED Requirements

### Requirement: Formas alternativas
El dataset SHALL incluir, además de las formas regionales, las formas alternativas de cada especie que cambian sus tipos, estadísticas base o habilidades: megaevoluciones, regresiones primigenias y otras formas (Rotom, Deoxys, Giratina, Tri-Genios, Necrozma, Urshifu…), con sus nombres, tipos, estadísticas, habilidades y el juego en que se introdujeron. MUST descartar las formas idénticas a la por defecto en tipos, estadísticas y habilidades (cosméticas y Gigamax), las de Pokémon dominante y las de compañero de Let's Go, y quedarse con una sola de las formas idénticas entre sí.

Una forma alternativa está **disponible** en un juego si se introdujo en ese juego o en uno anterior (las DLC cuentan como su juego base). Las megaevoluciones y las regresiones primigenias, además, solo en los juegos con Megaevolución: `x-y`, `omega-ruby-alpha-sapphire`, `sun-moon`, `ultra-sun-ultra-moon`, `lets-go-pikachu-lets-go-eevee`, `legends-za`, `mega-dimension` y `champions`. Sin juego, todas están disponibles.

#### Scenario: Rotom en Platino
- **WHEN** se consultan las formas de Rotom (#479) disponibles en `platinum`
- **THEN** son Calor, Lavado, Frío, Ventilador y Corte, cada una de tipo Eléctrico y su segundo tipo (Fuego, Agua, Hielo, Volador, Planta)

#### Scenario: Megas fuera de su época
- **WHEN** se consultan las formas de Charizard (#6) disponibles en `sword-shield`
- **THEN** no incluyen Mega Charizard X ni Mega Charizard Y

#### Scenario: Formas posteriores al juego
- **WHEN** se consultan las formas de Giratina (#487) disponibles en `diamond-pearl`
- **THEN** no incluyen la forma Origen (introducida en `platinum`)

#### Scenario: Formas cosméticas
- **WHEN** se consulta Unown (#201)
- **THEN** no tiene formas alternativas

### Requirement: Vista de una forma elegida
El sistema SHALL resolver la vista de una especie para una forma elegida (por su identificador, incluida la forma base de la especie) con sus nombres, tipos (los de la forma no cambian por generación), estadísticas, habilidades y eficacias, y MUST ofrecer la secuencia de formas para alternar en un juego: la forma que se muestra sin elegir (regional o base) seguida de las demás disponibles, en el orden del dataset. Una forma no disponible en el juego MUST NOT poder elegirse.

#### Scenario: Rotom Lavado
- **WHEN** se resuelve Rotom con la forma `rotom-wash` en `platinum`
- **THEN** la vista es de tipo Eléctrico/Agua, con Planta como única debilidad (×2) y Tierra en ×0 (Levitación)

#### Scenario: Secuencia en Espada
- **WHEN** se pide la secuencia de formas de Zigzagoon en `sword-shield`
- **THEN** es Zigzagoon de Galar y después Zigzagoon

## MODIFIED Requirements

### Requirement: Vista de la especie según el juego
El sistema SHALL resolver, para una especie y un juego opcional, la vista que se muestra: la forma regional del juego si la especie la tiene (si no, la forma por defecto); los tipos vigentes en la generación del juego; las habilidades solo a partir de la Gen 3 y la habilidad oculta solo a partir de la Gen 5; y la lista de las otras formas de la especie disponibles en el juego (regionales y alternativas) con sus tipos. Sin juego, se usa la forma por defecto y la generación actual.

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

#### Scenario: Megas en otras formas
- **WHEN** se resuelve Charizard para el juego `x-y`
- **THEN** en «otras formas» aparecen Mega Charizard X (Fuego/Dragón) y Mega Charizard Y (Fuego/Volador)
