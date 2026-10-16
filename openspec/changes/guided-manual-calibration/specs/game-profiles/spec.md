## MODIFIED Requirements

### Requirement: Calibración interactiva
El sistema SHALL ofrecer un modo de calibración que muestre una captura de la ventana objetivo y permita dibujar con el ratón un rectángulo sobre ella, confirmarlo con Enter o cancelarlo con Esc. Al calibrar un perfil nuevo, el sistema MUST pedir primero la región del nombre del rival y después, como pasos opcionales que se saltan con Esc o «Saltar», la del nombre de tu Pokémon y la del menú de ataques. El diálogo SHALL ofrecer «Volver a capturar» para cambiar la imagen por una captura nueva del emulador, también al recalibrar una región. Al confirmar un perfil nuevo, el sistema MUST pedir el nombre del perfil y el juego, proponiendo ambos según el juego detectado en el título de la ventana. Como alternativa a dibujar las regiones, el sistema SHALL ofrecer crear el perfil con un preset del juego (spec `game-presets`).

#### Scenario: Calibración completada
- **WHEN** el usuario dibuja un rectángulo, pulsa Enter, salta los pasos opcionales y confirma nombre y juego
- **THEN** se crea el perfil con esa región y ese juego, y pasa a ser el perfil activo

#### Scenario: Las tres regiones
- **WHEN** el usuario dibuja el rival, su Pokémon y, tras abrir el menú de Luchar y pulsar «Volver a capturar», el menú de ataques
- **THEN** el perfil se crea con las tres regiones

#### Scenario: Juego propuesto
- **WHEN** se calibra un perfil nuevo con la ventana "… | Pokémon Espada (64-bit) | …"
- **THEN** el diálogo propone el nombre «Pokémon Espada» y el juego «Espada / Escudo»

#### Scenario: Calibración cancelada
- **WHEN** el usuario pulsa Esc al dibujar la región del rival
- **THEN** no se crea ni se modifica ningún perfil

#### Scenario: Rectángulo demasiado pequeño
- **WHEN** el usuario confirma un rectángulo de menos de 8 px de alto o de ancho
- **THEN** se rechaza con un mensaje y la calibración sigue abierta

#### Scenario: Calibración sin ventana objetivo
- **WHEN** el usuario inicia la calibración sin ventana objetivo seleccionada
- **THEN** se le indica que seleccione primero una ventana y no se abre la calibración

#### Scenario: Con un preset
- **WHEN** el usuario elige «Nuevo perfil con un preset…» en lugar de calibrar
- **THEN** se abre el asistente de preset (spec `game-presets`)
