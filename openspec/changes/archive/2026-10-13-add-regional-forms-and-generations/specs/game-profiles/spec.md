## MODIFIED Requirements

### Requirement: Modelo de perfil
Un perfil SHALL contener: identificador, nombre visible, región del nombre del rival expresada como fracciones (x, y, ancho, alto) en el rango [0, 1] respecto al área cliente, idiomas de OCR preferidos, fecha de creación y, de forma opcional, el juego (identificador del grupo de versiones). Los perfiles guardados sin juego MUST seguir cargándose, con el juego sin especificar.

#### Scenario: Región relativa
- **WHEN** se calibra una región de 160×24 px en (480, 40) sobre un área cliente de 960×640
- **THEN** el perfil guarda la región (0.5, 0.0625, 0.1667, 0.0375) con al menos 4 decimales

#### Scenario: Perfil antiguo sin juego
- **WHEN** se carga un perfil guardado antes de existir el campo de juego
- **THEN** se carga correctamente con el juego sin especificar

### Requirement: Calibración interactiva
El sistema SHALL ofrecer un modo de calibración que muestre una captura de la ventana objetivo y permita dibujar con el ratón un rectángulo sobre ella, confirmarlo con Enter o cancelarlo con Esc. Al confirmar un perfil nuevo, el sistema MUST pedir el nombre del perfil y el juego, proponiendo ambos según el juego detectado en el título de la ventana.

#### Scenario: Calibración completada
- **WHEN** el usuario dibuja un rectángulo, pulsa Enter, y confirma nombre y juego
- **THEN** se crea el perfil con esa región y ese juego, y pasa a ser el perfil activo

#### Scenario: Juego propuesto
- **WHEN** se calibra un perfil nuevo con la ventana "… | Pokémon Espada (64-bit) | …"
- **THEN** el diálogo propone el nombre «Pokémon Espada» y el juego «Espada / Escudo»

#### Scenario: Calibración cancelada
- **WHEN** el usuario pulsa Esc durante la calibración
- **THEN** no se crea ni se modifica ningún perfil

#### Scenario: Rectángulo demasiado pequeño
- **WHEN** el usuario confirma un rectángulo de menos de 8 px de alto o de ancho
- **THEN** se rechaza con un mensaje y la calibración sigue abierta

#### Scenario: Calibración sin ventana objetivo
- **WHEN** el usuario inicia la calibración sin ventana objetivo seleccionada
- **THEN** se le indica que seleccione primero una ventana y no se abre la calibración

## ADDED Requirements

### Requirement: Activación automática del perfil por juego
WHEN se selecciona una ventana objetivo o se va a reconocer, el sistema SHALL detectar el juego por el título de la ventana y, si el perfil activo no es de ese juego y existe un perfil que sí lo es, MUST activarlo y avisarlo en la bandeja. Si no hay ningún perfil de ese juego, el perfil activo no cambia.

#### Scenario: Cambio de juego
- **WHEN** el perfil activo es de Esmeralda, existe uno de Espada y el usuario reconoce con la ventana "… Pokémon Espada …"
- **THEN** se activa el perfil de Espada antes de reconocer y se avisa en la bandeja

#### Scenario: Juego sin perfil propio
- **WHEN** el juego detectado no tiene perfil
- **THEN** se mantiene el perfil activo

### Requirement: Cambiar el juego de un perfil
El sistema SHALL permitir cambiar el juego del perfil activo desde el menú de la bandeja, incluida la opción «Sin especificar».

#### Scenario: Asignar juego a un perfil antiguo
- **WHEN** el usuario elige «Espada / Escudo» en el menú de juego del perfil activo
- **THEN** el perfil se guarda con ese juego y las siguientes fichas usan las formas de Galar
