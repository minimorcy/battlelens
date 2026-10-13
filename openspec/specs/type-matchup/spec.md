# type-matchup Specification

## Purpose
Comparativa de tipos entre tu Pokémon y el rival (multiplicadores en ambos sentidos y veredicto).
## Requirements
### Requirement: Comparativa de tipos
Dados tu Pokémon y un rival (sus vistas para el juego del perfil), el sistema SHALL calcular con la tabla de tipos de la generación del juego: para cada tipo de tu Pokémon, el multiplicador de daño contra el rival («Tus ataques»); y para cada tipo del rival, el multiplicador de daño contra tu Pokémon («Sus ataques»).

#### Scenario: Charizard contra Venusaur
- **WHEN** tu Pokémon es Charizard (Fuego/Volador) y el rival Venusaur (Planta/Veneno)
- **THEN** «Tus ataques» es Fuego ×2 y Volador ×2, y «Sus ataques» es Planta ×¼ y Veneno ×1

### Requirement: Veredicto
El sistema SHALL resumir la comparativa comparando tu mejor multiplicador con el mejor del rival: **Ventaja** si el tuyo es mayor, **Desventaja** si es menor y **Neutral** si son iguales.

#### Scenario: Ventaja
- **WHEN** tu Pokémon es Charizard y el rival Venusaur
- **THEN** el veredicto es Ventaja (×2 frente a ×1)

#### Scenario: Desventaja
- **WHEN** tu Pokémon es Charizard y el rival Golem (Roca/Tierra)
- **THEN** el veredicto es Desventaja (tu mejor es ×½, porque Roca resiste Fuego y Volador; el suyo es ×4)

#### Scenario: Neutral
- **WHEN** tu Pokémon es Rattata (Normal) y el rival Pidgey (Normal/Volador)
- **THEN** el veredicto es Neutral (×1 frente a ×1)

