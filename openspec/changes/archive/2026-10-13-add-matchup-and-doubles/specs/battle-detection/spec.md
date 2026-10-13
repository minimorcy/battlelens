## MODIFIED Requirements

### Requirement: Disparo del reconocimiento
El sistema SHALL lanzar un reconocimiento sobre los recortes capturados cuando la huella lleva al menos 2 ciclos consecutivos estable (diferencia media absoluta ≤ 8 sobre 255 respecto al ciclo anterior) y además difiere de la huella del último intento de reconocimiento. La huella combina las de todas las regiones configuradas en el perfil (rival, 2.º rival y tu Pokémon). Mientras alguna región cambia, no se reconoce.

#### Scenario: Entrada en combate
- **WHEN** aparece el recuadro con el nombre del rival y se mantiene estable 2 ciclos
- **THEN** se reconoce una sola vez

#### Scenario: Escena en movimiento
- **WHEN** la región cambia en todos los ciclos (por ejemplo, al caminar)
- **THEN** no se lanza ningún reconocimiento

#### Scenario: Región sin cambios
- **WHEN** la región sigue igual que en el último intento
- **THEN** no se vuelve a reconocer

#### Scenario: Cambias de Pokémon
- **WHEN** solo cambia la región de tu Pokémon y se estabiliza
- **THEN** se vuelve a reconocer para actualizar la comparativa

### Requirement: Mostrar la ficha en modo automático
WHEN un reconocimiento automático identifica al menos a un rival y la combinación de especies reconocidas (rival, 2.º rival y tu Pokémon) es distinta de la que muestra la ficha, el sistema SHALL mostrar la ficha con esa combinación. Si la combinación es la misma, no hace nada (tampoco vuelve a mostrar una ficha que el usuario haya ocultado). Si no identifica a ningún rival, MUST NOT mostrar el aviso de «No reconocido».

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
