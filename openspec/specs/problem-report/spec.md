# problem-report Specification

## Purpose
TBD - created by archiving change add-problem-report. Update Purpose after archive.
## Requirements
### Requirement: Crear un informe
La bandeja SHALL ofrecer «Informar de un problema…», que abre un diálogo con un campo de descripción opcional, la casilla «Incluir una captura del emulador» (marcada si hay ventana del emulador seleccionada; desactivada si no) y la casilla «Abrir el formulario de GitHub al terminar» (marcada). Al pulsar «Crear informe», el sistema SHALL crear en segundo plano un ZIP en `%APPDATA%\BattleLens\informes\` con el nombre `battlelens-informe-AAAAMMDD-HHMMSS.zip` y, al terminar, abrir el Explorador con el ZIP seleccionado.

#### Scenario: Informe con captura
- **WHEN** el tester tiene seleccionada la ventana del emulador, escribe «No reconoce a Pidgey» y pulsa «Crear informe»
- **THEN** se crea el ZIP en `informes\` y se abre el Explorador con él seleccionado

#### Scenario: Sin ventana del emulador
- **WHEN** no hay ventana del emulador seleccionada
- **THEN** la casilla de la captura aparece desmarcada y desactivada, y el informe se crea sin captura

### Requirement: Contenido del informe
El ZIP SHALL contener:
- `informe.json`, con la versión, la fecha, la versión de Windows, los idiomas de OCR instalados, los idiomas de la interfaz y de los datos, el modo de la ficha, el emulador (ejecutable y título de la ventana), el juego y las regiones del perfil activo, la detección automática y el modo stream activados o no, y la descripción;
- `config.toml`, `profiles/*.json` y los registros `app.log*`;
- si se pidió captura y fue posible, `captura/emulador.png` con el área cliente del emulador, `captura/<rol>.png` con el recorte de cada región del perfil activo (rival, 2.º rival, tu Pokémon, menú de ataques) y `captura/lecturas.json` con lo que lee el OCR en cada región (texto, especie reconocida, puntuación y nivel);
- `debug/` con los 20 archivos más recientes de la carpeta de depuración, si existe.

Si la captura falla, el informe MUST crearse igualmente y `informe.json` MUST indicar el motivo.

#### Scenario: Recortes de las regiones
- **WHEN** el perfil activo tiene las regiones del rival y de tu Pokémon y se pide captura
- **THEN** el ZIP contiene `captura/emulador.png`, `captura/rival.png`, `captura/own.png` y `captura/lecturas.json` con la lectura de ambas

#### Scenario: Ventana minimizada
- **WHEN** la ventana del emulador está minimizada al crear el informe
- **THEN** el ZIP se crea sin captura y `informe.json` indica que no se pudo capturar y por qué

### Requirement: Privacidad del informe
El sistema MUST NOT enviar el informe a ningún sitio: solo se guarda en local. En todos los archivos de texto del ZIP (registros, configuración, perfiles, `informe.json`, JSON de depuración) MUST sustituir la ruta de la carpeta del usuario por `%USERPROFILE%` y el nombre de usuario de Windows por `<usuario>`. La captura MUST ser solo del área cliente de la ventana del emulador.

#### Scenario: Ruta con el nombre de usuario
- **WHEN** `app.log` contiene `C:\Users\ash\AppData\Roaming\BattleLens\debug`
- **THEN** en el ZIP aparece como `%USERPROFILE%\AppData\Roaming\BattleLens\debug`

### Requirement: Formulario de GitHub prerrellenado
Si está marcada la casilla, al terminar el sistema SHALL abrir en el navegador el formulario de fallo del repositorio con los campos «Versión», «Emulador» y «Juego» rellenados a partir de la versión instalada, el ejecutable del emulador y el juego del perfil activo.

#### Scenario: Abrir el formulario
- **WHEN** se crea un informe con la versión 0.3.0, el emulador `mGBA.exe` y el juego Esmeralda
- **THEN** se abre `…/issues/new?template=bug_report.yml` con `version=0.3.0`, `emulator=mGBA.exe` y `game=Esmeralda`

