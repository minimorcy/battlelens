## ADDED Requirements

### Requirement: Estadísticas base según la generación
El dataset SHALL incluir, por Pokémon (especie y forma), las estadísticas base que tuvo en generaciones anteriores, con la última generación en que estuvieron vigentes, incluida la estadística **Especial** de la Gen 1. Al resolver la vista de un juego, el sistema MUST usar, para cada estadística, el valor vigente en la generación del juego. En la Gen 1 la vista MUST tener PS, Ataque, Defensa, Especial y Velocidad (sin At. Esp. ni Def. Esp.), y su total MUST sumar esas cinco.

#### Scenario: Pikachu en Blanco/Negro
- **WHEN** se resuelve la especie #25 (Pikachu) para el juego `black-white` (Gen 5)
- **THEN** su Defensa es 30 y su Def. Esp. 40

#### Scenario: Pikachu en la generación actual
- **WHEN** se resuelve la especie #25 sin juego
- **THEN** su Defensa es 40 y su Def. Esp. 50

#### Scenario: Pikachu en Rojo/Azul
- **WHEN** se resuelve la especie #25 para el juego `red-blue`
- **THEN** sus estadísticas son PS 35, Ataque 55, Defensa 30, Especial 50 y Velocidad 90 (total 260)
