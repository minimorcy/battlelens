## MODIFIED Requirements

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
