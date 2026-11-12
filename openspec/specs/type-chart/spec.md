# type-chart Specification

## Purpose
Tabla de tipos flotante y reescalable de la generación del juego, con atajo global y los tipos de la ficha resaltados.
## Requirements
### Requirement: Mostrar y ocultar la tabla de tipos
El sistema SHALL ofrecer el atajo global «Tabla de tipos» (por defecto `Ctrl+Alt+T`, configurable en `hotkeys.type_chart` y en *Ajustes → Atajos*, con las mismas reglas que el resto de atajos) y la opción «Tabla de tipos» en la bandeja, con la pista del atajo. Ambos SHALL alternar una ventana flotante con la tabla. La ventana SHALL estar siempre delante sin quitar el foco al emulador, SHALL poder arrastrarse, SHALL cerrarse con su botón ✕ y MUST quedar excluida de la captura de pantalla para que el OCR no la lea. La primera vez SHALL aparecer junto al emulador (o en la pantalla principal si no hay ventana seleccionada) y después donde el usuario la dejó.

#### Scenario: Abrir y cerrar con el atajo
- **WHEN** el usuario pulsa `Ctrl+Alt+T` dos veces
- **THEN** la tabla aparece con la primera pulsación y se oculta con la segunda

#### Scenario: El OCR no la ve
- **WHEN** la tabla está abierta encima del nombre del rival
- **THEN** la captura del emulador no incluye la tabla

### Requirement: Tabla reescalable
La tabla SHALL poder reescalarse entera, manteniendo su proporción, arrastrando el tirador de su esquina inferior derecha o con `Ctrl` + rueda del ratón, entre el 60 % y el 200 % de su tamaño. La posición y la escala SHALL guardarse en `state.json` y recuperarse al volver a abrir la app; si la posición guardada queda fuera de las pantallas, la tabla MUST aparecer dentro de la pantalla. Un `state.json` con valores no válidos MUST ignorarse sin impedir el arranque.

#### Scenario: Agrandar con el tirador
- **WHEN** el usuario arrastra el tirador hacia la derecha
- **THEN** la tabla crece entera (celdas, textos y píldoras) sin cambiar su proporción

#### Scenario: Recordar el tamaño
- **WHEN** el usuario deja la tabla al 130 % y reinicia la app
- **THEN** al abrir la tabla aparece al 130 % y donde la dejó

#### Scenario: Límites
- **WHEN** el usuario sigue girando la rueda con `Ctrl` pulsado
- **THEN** la escala se detiene en el 200 % (o en el 60 % al reducir)

### Requirement: Tabla según la generación del juego
La tabla SHALL mostrar el atacante en filas y el defensor en columnas, solo con los tipos que existen en la generación del juego del perfil activo (sin perfil, la generación actual), y con los multiplicadores de esa generación. Las celdas ×2, ×½ y ×0 SHALL distinguirse por color y texto; las ×1 SHALL quedar vacías. El título SHALL indicar la generación. La tabla SHALL calcularse al mostrarse, así que un cambio de perfil se ve al volver a abrirla.

#### Scenario: Tercera generación
- **WHEN** el perfil activo es de Pokémon Rojo Fuego (Gen 3) y abre la tabla
- **THEN** aparecen 17 tipos, sin Hada, y Fantasma hace ×½ contra Acero

#### Scenario: Pokémon Rojo/Azul
- **WHEN** el perfil activo es de un juego de la Gen 1
- **THEN** aparecen 15 tipos y Fantasma hace ×0 contra Psíquico

#### Scenario: Sin perfil
- **WHEN** no hay perfil activo
- **THEN** la tabla tiene los 18 tipos de la generación actual

### Requirement: Resaltar los tipos de la ficha
Si hay una ficha visible (de combate o del buscador), la tabla SHALL resaltar las columnas de los tipos de los Pokémon de esa ficha (los rivales, no el Pokémon propio). El resaltado SHALL actualizarse cuando se muestra otra ficha o cambia la forma, y SHALL desaparecer cuando la ficha se oculta.

#### Scenario: Rival en combate
- **WHEN** la ficha muestra a Rapidash de Galar y la tabla está abierta
- **THEN** las columnas Psíquico y Hada aparecen resaltadas

#### Scenario: Ficha oculta
- **WHEN** el usuario oculta la ficha con la tabla abierta
- **THEN** ninguna columna queda resaltada

