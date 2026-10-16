## ADDED Requirements

### Requirement: Regiones ancladas a la imagen del juego
Un perfil SHALL poder guardar dónde estaba la imagen del juego en el área cliente cuando se midieron sus regiones (`game_area`). Si lo tiene y su juego tiene una proporción conocida, antes de recortar el sistema MUST localizar la imagen del juego en la captura actual y llevar cada región a la misma posición relativa dentro de ella. La localización MUST hacerse una sola vez por tamaño de captura; si no es fiable, las regiones se usan sin mover y se reintenta con la siguiente captura. Los perfiles creados con un preset, los creados a mano para un juego de proporción conocida y las regiones recalibradas MUST guardar sus medidas respecto a `game_area`. Los perfiles sin `game_area` MUST seguir funcionando como antes.

#### Scenario: De ventana maximizada a pantalla completa
- **WHEN** un perfil de Espada se crea con un preset en la ventana maximizada (con barra de menús y de estado) y luego el emulador se pone a pantalla completa
- **THEN** las regiones caen sobre los mismos recuadros del juego

#### Scenario: Pantalla en negro
- **WHEN** la captura es una pantalla negra entre escenas
- **THEN** las regiones no se mueven y no se recuerda ninguna posición para ese tamaño

#### Scenario: Perfil anterior
- **WHEN** el perfil no tiene `game_area`
- **THEN** las regiones se usan tal cual, como fracciones del área cliente

#### Scenario: Recalibrar con otra ventana
- **WHEN** el usuario recalibra una región con el emulador a pantalla completa en un perfil medido en ventana
- **THEN** la región se guarda en su sitio respecto a la imagen del juego original
