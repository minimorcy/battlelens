# competitive-data Specification

## Purpose
Datos del modo Competitivo: movimientos probables, estadísticas a su nivel, velocidad, efectos de habilidades y entrenamiento.
## Requirements
### Requirement: Movimientos probables
Conocidos la especie (o forma), el juego y el nivel del rival, el sistema SHALL calcular sus movimientos probables: los 4 últimos movimientos distintos que aprende por subida de nivel hasta ese nivel, en el juego del perfil. Sin juego, o si la especie no está en ese juego, se usa el juego más reciente (de la generación del juego, si lo hay) que tenga datos. Cada movimiento indica nombre, tipo, categoría (física, especial o de estado), potencia y, si se conoce tu Pokémon, su multiplicador contra él, aplicando los efectos seguros de las habilidades de tu Pokémon.

#### Scenario: Movimientos de un salvaje
- **WHEN** el rival es Stufful de nivel 10 en `sword-shield`
- **THEN** los movimientos probables son los 4 últimos que aprende hasta el nivel 10 en Espada/Escudo, en orden de aprendizaje

#### Scenario: Supereficaz contra ti
- **WHEN** un movimiento probable es de tipo Lucha y tu Pokémon es de tipo Normal
- **THEN** ese movimiento aparece marcado con ×2

#### Scenario: Tu habilidad lo anula
- **WHEN** un movimiento probable es de tipo Tierra y tu Pokémon es Flygon (solo Levitación)
- **THEN** ese movimiento aparece marcado con ×0

#### Scenario: Nivel desconocido
- **WHEN** no se ha podido leer el nivel del rival
- **THEN** en lugar de los movimientos se indica que hay que incluir el nivel en la región calibrada

### Requirement: Estadísticas reales a su nivel
Conocido el nivel, el sistema SHALL calcular para cada estadística el rango real con la fórmula de la Gen 3 en adelante: mínimo con IV 0, EV 0 y naturaleza desfavorable; máximo con IV 31, EV 252 y naturaleza favorable (los PS no dependen de la naturaleza; Shedinja siempre tiene 1 PS).

#### Scenario: Rango a nivel 50
- **WHEN** se calcula Garchomp (PS 108, Velocidad 102) a nivel 50
- **THEN** los PS van de 168 a 215 y la Velocidad de 96 a 169

#### Scenario: Shedinja
- **WHEN** se calculan los PS de Shedinja a cualquier nivel
- **THEN** el rango es 1-1

### Requirement: ¿Quién es más rápido?
Si se conocen el nivel del rival y el de tu Pokémon, el sistema SHALL comparar sus rangos de Velocidad: «Eres más rápido» si tu mínimo supera su máximo, «Es más rápido» si su mínimo supera tu máximo y «Depende de IVs/EVs» en otro caso. Sin alguno de los niveles, MUST NOT mostrar la comparación.

#### Scenario: Más rápido seguro
- **WHEN** tu Pokémon es Jolteon de nivel 50 y el rival Snorlax de nivel 50
- **THEN** se indica «Eres más rápido»

#### Scenario: Depende
- **WHEN** ambos son Pikachu de nivel 50
- **THEN** se indica «Depende de IVs/EVs»

### Requirement: Habilidades que cambian la eficacia
El sistema SHALL anotar en cada habilidad del rival los cambios de eficacia que provoca si la tiene, según una tabla de habilidades conocidas (entre otras: Levitación → Tierra ×0; Absorbe Fuego → Fuego ×0; Absorbe Agua, Colector y Piel Seca → Agua ×0; Absorbe Elec, Pararrayos y Electromotor → Eléctrico ×0; Herbívoro → Planta ×0; Ignífugo → Fuego ×½; Sebo → Fuego ×½ y Hielo ×½; Peluche → Fuego ×2; Superguarda → solo le afectan los ataques supereficaces; Filtro, Roca Sólida y Armadura Prisma → los supereficaces le hacen ×0,75).

#### Scenario: Levitación
- **WHEN** el rival es Bronzong (Levitación, Ignífugo)
- **THEN** junto a Levitación aparece «Tierra ×0» y junto a Ignífugo «Fuego ×½»

### Requirement: Datos de entrenamiento
El sistema SHALL mostrar los EVs que da al ser derrotado, su peso con la potencia de Patada Baja y Hierba Lazo contra él (20 si pesa menos de 10 kg; 40, 60, 80 y 100 hasta 25, 50, 100 y 200 kg; 120 a partir de 200 kg) y un perfil según sus estadísticas base: atacante físico o especial (si su mayor estadística ofensiva supera a la otra en 20 o más), defensivo (si PS + Defensa + Def. Esp. supera a Ataque + At. Esp. + Velocidad en 40 o más) y rápido (Velocidad ≥ 100).

#### Scenario: Snorlax
- **WHEN** se muestran los datos de entrenamiento de Snorlax
- **THEN** da 2 EVs de PS, pesa 460 kg (Patada Baja: 120) y su perfil es «Atacante físico, defensivo»

