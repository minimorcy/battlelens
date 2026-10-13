# game-profiles Specification

## Purpose
Perfiles de calibración por juego: dónde aparece el nombre del rival en la pantalla de cada juego, su persistencia y cuál está activo.
## Requirements
### Requirement: Modelo de perfil
Un perfil SHALL contener: identificador, nombre visible, región del nombre del rival, idiomas de OCR preferidos, fecha de creación y, de forma opcional, el juego (identificador del grupo de versiones), la región del nombre del 2.º rival (combates dobles) y la región del nombre de tu Pokémon. Todas las regiones se expresan como fracciones (x, y, ancho, alto) en el rango [0, 1] respecto al área cliente. Los perfiles guardados sin los campos opcionales MUST seguir cargándose, con esos campos sin especificar.

#### Scenario: Región relativa
- **WHEN** se calibra una región de 160×24 px en (480, 40) sobre un área cliente de 960×640
- **THEN** el perfil guarda la región (0.5, 0.0625, 0.1667, 0.0375) con al menos 4 decimales

#### Scenario: Perfil antiguo sin juego
- **WHEN** se carga un perfil guardado antes de existir el campo de juego
- **THEN** se carga correctamente con el juego sin especificar

#### Scenario: Perfil sin regiones opcionales
- **WHEN** se carga un perfil que solo tiene la región del rival
- **THEN** se carga correctamente sin región del 2.º rival ni de tu Pokémon

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

### Requirement: Persistencia de perfiles
El sistema SHALL guardar cada perfil como un archivo JSON en `%APPDATA%\BattleLens\profiles\` y MUST cargarlos todos al arrancar.

#### Scenario: Recarga tras reinicio
- **WHEN** se crea un perfil y se reinicia la aplicación
- **THEN** el perfil aparece disponible con la misma región

#### Scenario: Archivo corrupto
- **WHEN** un archivo de perfil no es JSON válido o no cumple el esquema
- **THEN** se ignora ese archivo, se registra un aviso en el log y el resto de perfiles se cargan

### Requirement: Perfil activo
El sistema SHALL mantener exactamente un perfil activo cuando exista al menos un perfil, MUST permitir cambiarlo desde la bandeja del sistema y MUST recordar el último perfil activo entre ejecuciones.

#### Scenario: Cambio de perfil
- **WHEN** el usuario selecciona otro perfil en el menú de la bandeja
- **THEN** los siguientes reconocimientos usan la región de ese perfil

#### Scenario: Sin perfiles
- **WHEN** no existe ningún perfil y el usuario lanza un reconocimiento
- **THEN** el sistema indica que hay que calibrar primero

### Requirement: Recalibrar y eliminar
El sistema SHALL permitir recalibrar la región del perfil activo y eliminar perfiles existentes.

#### Scenario: Recalibración
- **WHEN** el usuario recalibra el perfil activo y confirma un nuevo rectángulo
- **THEN** se sobrescribe la región manteniendo el identificador y el nombre del perfil

#### Scenario: Eliminación del perfil activo
- **WHEN** el usuario elimina el perfil activo y quedan otros perfiles
- **THEN** se borra su archivo y pasa a ser activo otro perfil existente

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

### Requirement: Regiones opcionales
El sistema SHALL permitir calibrar sobre una captura, para el perfil activo, la región del nombre del 2.º rival, la de tu Pokémon y la del menú de ataques (con el mismo diálogo y las mismas validaciones que la región del rival), y SHALL permitir quitarlas. La región del menú de ataques MUST NOT formar parte de la huella de detección del combate ni de las regiones de nombres.

#### Scenario: Calibrar tu Pokémon
- **WHEN** el usuario elige «Calibrar tu Pokémon…», dibuja el rectángulo y pulsa Enter
- **THEN** el perfil activo guarda esa región como la de tu Pokémon

#### Scenario: Quitar la región del 2.º rival
- **WHEN** el usuario elige «Quitar 2.º rival»
- **THEN** el perfil deja de tener esa región y los reconocimientos vuelven a leer solo un rival

#### Scenario: Calibrar el menú de ataques
- **WHEN** el usuario elige «Calibrar menú de ataques…» con el menú de «Luchar» abierto, dibuja el rectángulo sobre los 4 movimientos y pulsa Enter
- **THEN** el perfil activo guarda esa región como la del menú de ataques, y los perfiles guardados antes de este cambio se siguen cargando sin ella

