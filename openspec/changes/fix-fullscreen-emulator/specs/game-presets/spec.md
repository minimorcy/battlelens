## MODIFIED Requirements

### Requirement: Localización de la imagen del juego
Dada una captura del área cliente del emulador y la proporción del juego, el sistema SHALL localizar el rectángulo de la imagen del juego: descartar las bandas de color uniforme de los bordes y, si lo que queda es más alto o más ancho de lo que corresponde a la proporción, separar las franjas sobrantes (barra de menús, de estado) buscando el borde horizontal o vertical más marcado. En juegos de DS, si lo que queda corresponde a dos pantallas en vertical (aprox. 4:6) u horizontal (aprox. 8:3), MUST quedarse con la pantalla superior (la de arriba o la de la izquierda). Si no consigue un rectángulo de la proporción esperada (±6 %), MUST indicar que la localización no es fiable. Una captura lisa (pantalla negra, fundido) MUST marcarse como no fiable.

#### Scenario: Bandas negras
- **WHEN** la captura es una imagen GBA escalada ×4 centrada en un área de 1280×720 con bandas negras
- **THEN** la imagen del juego es el rectángulo de 960×640 centrado

#### Scenario: Barra de menús
- **WHEN** la captura es una imagen GBA de 720×480 con una barra de menús de 24 px encima
- **THEN** la imagen del juego empieza en la fila 24 y mide 720×480

#### Scenario: DS en vertical
- **WHEN** la captura son las dos pantallas de DS apiladas (512×768) y el preset es de DS
- **THEN** la imagen del juego es la mitad superior (512×384)

#### Scenario: Proporción imposible
- **WHEN** la captura es una imagen de 16:9 y el preset es de GBA
- **THEN** la localización se marca como no fiable

#### Scenario: Pantalla lisa
- **WHEN** la captura es una pantalla completamente negra de 16:9 y el preset es de Espada
- **THEN** la localización se marca como no fiable
