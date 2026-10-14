## ADDED Requirements

### Requirement: Presets por juego
El sistema SHALL incluir presets para los juegos con recuadros de nombre en posición fija: `red-blue`, `yellow`, `gold-silver`, `crystal`, `ruby-sapphire`, `emerald`, `firered-leafgreen`, `diamond-pearl`, `platinum`, `heartgold-soulsilver`, `black-white`, `black-2-white-2` y `sword-shield`. Cada preset MUST indicar la proporción de la imagen del juego (Game Boy 10:9, GBA 3:2, pantalla de DS 4:3, Switch 16:9), si es un juego de DS (el preset se refiere a la pantalla superior) y las regiones del rival y de tu Pokémon, y opcionalmente la del menú de ataques, en fracciones de esa imagen.

#### Scenario: Juego con preset
- **WHEN** se piden los presets de `emerald`
- **THEN** se obtiene un preset GBA (3:2) con las regiones del rival y de tu Pokémon

#### Scenario: Juego sin preset
- **WHEN** se piden los presets de `scarlet-violet`
- **THEN** no hay preset y el asistente propone calibrar a mano

### Requirement: Localización de la imagen del juego
Dada una captura del área cliente del emulador y la proporción del juego, el sistema SHALL localizar el rectángulo de la imagen del juego: descartar las bandas de color uniforme de los bordes y, si lo que queda es más alto o más ancho de lo que corresponde a la proporción, separar las franjas sobrantes (barra de menús, de estado) buscando el borde horizontal o vertical más marcado. En juegos de DS, si lo que queda corresponde a dos pantallas en vertical (aprox. 4:6) u horizontal (aprox. 8:3), MUST quedarse con la pantalla superior (la de arriba o la de la izquierda). Si no consigue un rectángulo de la proporción esperada (±6 %), MUST indicar que la localización no es fiable.

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

### Requirement: Asistente de preset
La bandeja SHALL ofrecer «Nuevo perfil con un preset…», que, con la ventana del emulador seleccionada, la captura y abre un asistente:
1. **Juego:** se propone por el título de la ventana entre los juegos con preset, y se puede cambiar.
2. **Confirmación:** se dibujan sobre la captura el rectángulo de la imagen del juego localizada y los recuadros del preset, con lo que lee BattleLens en cada uno, y se pregunta si los recuadros caen sobre los nombres (pidiendo hacerlo durante un combate).
3. **Acciones:** «Guardar perfil» (crea el perfil con las regiones del preset convertidas al área cliente, con el juego y el nombre propuestos, y lo activa), «Ajustar la imagen del juego» (el usuario dibuja el rectángulo de la imagen del juego y se vuelven a colocar los recuadros) y «Calibrar a mano» (abre la calibración actual).

Si la localización no es fiable, el asistente MUST pedir directamente que el usuario dibuje la imagen del juego.

#### Scenario: Preset aceptado
- **WHEN** el usuario abre el asistente con mGBA en un combate de Esmeralda y pulsa «Guardar perfil»
- **THEN** se crea y activa el perfil «Pokémon Esmeralda», con juego `emerald` y las regiones del rival y de tu Pokémon

#### Scenario: Ajustar la imagen del juego
- **WHEN** los recuadros no caen sobre los nombres y el usuario elige «Ajustar la imagen del juego» y dibuja su rectángulo
- **THEN** los recuadros se recolocan dentro de ese rectángulo

#### Scenario: Sin preset para el juego
- **WHEN** el juego detectado no tiene preset
- **THEN** el asistente lo indica y ofrece «Calibrar a mano»

### Requirement: Primer arranque
Si al arrancar no hay ningún perfil, el aviso de bienvenida SHALL proponer «Nuevo perfil con un preset…» en la bandeja como primer paso.

#### Scenario: Sin perfiles
- **WHEN** BattleLens arranca por primera vez con la ventana del emulador ya elegida
- **THEN** el aviso indica que abra «Nuevo perfil con un preset…» durante un combate

### Requirement: Validación de presets
El proyecto SHALL incluir `tools/validate_presets.py`, que, para cada imagen de una carpeta de capturas de referencia cuyo nombre empieza por el juego, localiza la imagen del juego, aplica el preset, lee cada región con el pipeline de BattleLens y muestra una tabla con lo leído, y opcionalmente guarda los recortes.

#### Scenario: Validar Esmeralda
- **WHEN** se ejecuta `uv run python tools/validate_presets.py capturas-presets`
- **THEN** se muestra, por imagen, el juego, la región, el texto leído y la especie reconocida
