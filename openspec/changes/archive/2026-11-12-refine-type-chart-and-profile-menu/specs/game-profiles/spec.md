## ADDED Requirements

### Requirement: Modificar o crear un perfil desde la bandeja
La bandeja SHALL ofrecer «Modificar o crear perfil…», con la pista del atajo de calibrar, que hace lo mismo que ese atajo. Con un perfil activo, pregunta qué región recalibrar o si crear un perfil nuevo. Sin perfiles, empieza la calibración de uno nuevo.

#### Scenario: Desde la bandeja con un perfil activo
- **WHEN** el perfil «Espada» está activo y el usuario elige «Modificar o crear perfil…» en la bandeja
- **THEN** se abre el diálogo para elegir qué recalibrar en «Espada» o crear un perfil nuevo

#### Scenario: Pista del atajo
- **WHEN** el atajo de calibrar es `Ctrl+Alt+C`
- **THEN** la opción de la bandeja muestra `Ctrl+Alt+C`
