## MODIFIED Requirements

### Requirement: Mostrar la ficha en modo automático
WHEN un reconocimiento automático identifica al menos a un rival y la combinación de especies reconocidas (rival, 2.º rival y tu Pokémon) es distinta de la que muestra la ficha, el sistema SHALL mostrar la ficha con esa combinación. Con la opción «Solo en la pantalla de combate» activa (por defecto), un rival MUST contar como identificado solo si también se ha leído su nivel. Si la combinación es la misma, no hace nada (tampoco vuelve a mostrar una ficha que el usuario haya ocultado). Si no identifica a ningún rival, MUST NOT mostrar el aviso de «No reconocido».

#### Scenario: Nuevo rival
- **WHEN** la ficha muestra a Pidgey y la detección automática reconoce a Rattata
- **THEN** la ficha pasa a mostrar a Rattata

#### Scenario: Ficha ocultada por el usuario
- **WHEN** el usuario oculta la ficha de Stufful y la detección vuelve a reconocer a Stufful
- **THEN** la ficha no vuelve a aparecer

#### Scenario: Sin reconocer
- **WHEN** un reconocimiento automático no identifica ninguna especie
- **THEN** no se muestra ningún aviso

#### Scenario: Cambia tu Pokémon
- **WHEN** la ficha muestra a Venusaur contra tu Charizard y sacas a Blastoise
- **THEN** la ficha se actualiza con la comparativa contra Blastoise

#### Scenario: Pokédex
- **WHEN** la región del 2.º rival muestra «Cleffa» sin nivel (Pokédex) y la opción está activa
- **THEN** no se muestra la ficha

#### Scenario: Región sin nivel
- **WHEN** la opción está desactivada y la región del rival muestra «Pikachu» sin nivel
- **THEN** se muestra la ficha de Pikachu
