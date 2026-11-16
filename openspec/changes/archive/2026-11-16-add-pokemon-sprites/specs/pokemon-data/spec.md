## ADDED Requirements

### Requirement: Número de sprite por especie y forma
El dataset SHALL guardar para cada especie y cada forma su número de Pokémon de PokéAPI (`sprite_id`), y la vista de la especie MUST exponer el de la forma mostrada. Las formas sin Pokémon propio usan el de la especie.

#### Scenario: Especie base
- **WHEN** se consulta la vista de Stufful
- **THEN** su `sprite_id` es 759

#### Scenario: Forma regional
- **WHEN** se consulta la vista de Zigzagoon en `sword-shield`
- **THEN** su `sprite_id` es 10174
