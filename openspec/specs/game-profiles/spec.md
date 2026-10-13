# game-profiles Specification

## Purpose
Perfiles de calibración por juego: dónde aparece el nombre del rival en la pantalla de cada juego, su persistencia y cuál está activo.
## Requirements
### Requirement: Modelo de perfil
Un perfil SHALL contener: identificador, nombre visible, región del nombre del rival expresada como fracciones (x, y, ancho, alto) en el rango [0, 1] respecto al área cliente, idiomas de OCR preferidos y fecha de creación.

#### Scenario: Región relativa
- **WHEN** se calibra una región de 160×24 px en (480, 40) sobre un área cliente de 960×640
- **THEN** el perfil guarda la región (0.5, 0.0625, 0.1667, 0.0375) con al menos 4 decimales

### Requirement: Calibración interactiva
El sistema SHALL ofrecer un modo de calibración que muestre una captura de la ventana objetivo y permita dibujar con el ratón un rectángulo sobre ella, confirmarlo con Enter o cancelarlo con Esc.

#### Scenario: Calibración completada
- **WHEN** el usuario dibuja un rectángulo, pulsa Enter e introduce un nombre de perfil
- **THEN** se crea el perfil con esa región y pasa a ser el perfil activo

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

