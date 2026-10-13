## ADDED Requirements

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
