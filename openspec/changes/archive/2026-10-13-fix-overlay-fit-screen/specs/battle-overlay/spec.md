## MODIFIED Requirements

### Requirement: Comportamiento de la ventana
El overlay SHALL estar siempre por encima del resto de ventanas, sin marco, MUST NOT robar el foco del teclado al emulador y MUST NOT aparecer en la barra de tareas. Se SHALL posicionar por defecto junto al borde derecho de la ventana objetivo, o dentro de la pantalla si no cabe, y MUST recordar la posición si el usuario lo arrastra. El overlay MUST caber en la pantalla: si su contenido es más alto que la altura disponible, se limita a esa altura y el contenido se desplaza con la rueda del ratón. Las tarjetas MUST reservar la altura que necesitan sus textos partidos en líneas, también con escalado de pantalla alto.

#### Scenario: Foco preservado
- **WHEN** el overlay aparece mientras el usuario juega
- **THEN** las pulsaciones de teclado siguen llegando al emulador

#### Scenario: Emulador a pantalla completa en el borde
- **WHEN** la ventana objetivo ocupa toda la pantalla
- **THEN** el overlay se coloca dentro de la pantalla, en la esquina superior derecha

#### Scenario: Pantalla pequeña
- **WHEN** la ficha competitiva (~860 px) se muestra en una pantalla con 720 px de alto disponibles
- **THEN** el overlay mide como máximo esa altura y su contenido se puede desplazar con la rueda

#### Scenario: Escalado alto en combates dobles
- **WHEN** Windows usa un escalado del 200 % y se muestra un combate doble con una evolución larga
- **THEN** ningún texto de las tarjetas queda recortado
