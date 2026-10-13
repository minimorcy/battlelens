## ADDED Requirements

### Requirement: Cambiar de forma
El sistema SHALL ofrecer el atajo global «Cambiar de forma» (por defecto `Ctrl+Alt+F`, configurable). Con la ficha visible, el atajo avanza a la siguiente forma de la secuencia del primer rival que tenga más de una forma disponible en el juego del perfil, volviendo a la primera tras la última, y vuelve a dibujar la ficha con esa forma (tipos, estadísticas, habilidades, eficacias, comparativa y movimientos). La forma elegida MUST mantenerse mientras esa especie siga en el combate, aunque la detección automática vuelva a mostrar la ficha, y MUST olvidarse cuando la especie deje de estar entre los rivales mostrados. Si ningún rival tiene otras formas, el atajo no hace nada. La sección «Otras formas» MUST recordar el atajo.

#### Scenario: Rotom Lavado
- **WHEN** la ficha muestra a Rotom en `platinum` y el usuario pulsa `Ctrl+Alt+F` dos veces
- **THEN** la ficha muestra primero Rotom Calor y después Rotom Lavado (Eléctrico/Agua)

#### Scenario: La elección se mantiene en el combate
- **WHEN** el usuario ha elegido Mega Charizard X y la detección automática vuelve a reconocer a Charizard
- **THEN** la ficha sigue mostrando Mega Charizard X

#### Scenario: Nuevo rival
- **WHEN** después de elegir Rotom Lavado entra otro Pokémon y luego otro Rotom
- **THEN** el nuevo Rotom se muestra con la forma base

#### Scenario: Sin otras formas
- **WHEN** la ficha muestra a Pidgey y el usuario pulsa `Ctrl+Alt+F`
- **THEN** la ficha no cambia

#### Scenario: Movimientos de una mega
- **WHEN** la ficha competitiva muestra Mega Charizard X de nivel 50
- **THEN** los movimientos probables son los de Charizard
