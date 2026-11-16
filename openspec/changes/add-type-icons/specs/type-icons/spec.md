## ADDED Requirements

### Requirement: Descarga de los iconos de tipo
Con la opción de iconos activada, el sistema SHALL descargar en segundo plano los iconos de los 18 tipos que falten en la caché, desde `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/types/generation-viii/sword-shield/small/<id>.png`, donde `<id>` es el número de tipo de PokéAPI guardado en el dataset. Cada descarga MUST tener un tiempo de espera de 5 s y un tamaño máximo de 64 KB, y MUST ser un PNG válido antes de guardarse, con escritura atómica en `type-icons/<id>.png` dentro de la carpeta de datos del usuario. La descarga MUST NOT bloquear la interfaz ni el reconocimiento.

#### Scenario: Primera activación
- **WHEN** el usuario activa los iconos y la caché está vacía
- **THEN** el sistema descarga los 18 iconos sin congelar la ficha ni la detección

#### Scenario: Respuesta no válida
- **WHEN** una descarga devuelve algo que no es un PNG o supera el tamaño máximo
- **THEN** el archivo no se guarda y ese icono cuenta como no disponible

#### Scenario: Caché completa
- **WHEN** los 18 iconos ya están en la caché
- **THEN** el sistema no hace ninguna petición

### Requirement: Iconos solo con el juego completo
El sistema SHALL dibujar los tipos como icono solo cuando la opción está activada y los 18 iconos están en la caché. En cualquier otro caso (sin conexión, descarga en curso o fallida) SHALL usar las etiquetas de texto. Los fallos se recuerdan durante la sesión y no se reintentan en cada ficha.

#### Scenario: Sin conexión
- **WHEN** la opción está activada pero no se pudo descargar algún icono
- **THEN** la ficha muestra todos los tipos como etiquetas y el resto no cambia

#### Scenario: Llegan los iconos
- **WHEN** termina de descargarse el último icono con una ficha visible
- **THEN** la ficha se vuelve a dibujar con iconos

### Requirement: Nombre del tipo accesible
Cada icono SHALL llevar el nombre del tipo en el idioma de la ficha como texto alternativo (descripción accesible y, donde la ventana admite el ratón, tooltip).

#### Scenario: Nombre del icono
- **WHEN** la ficha en español muestra el icono del tipo Fuego
- **THEN** su descripción accesible es «Fuego»
