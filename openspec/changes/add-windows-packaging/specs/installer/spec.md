## ADDED Requirements

### Requirement: Instalador sin permisos de administrador
El proyecto SHALL generar con Inno Setup un instalador `BattleLens-Setup-<versión>.exe` que instale la aplicación solo para el usuario actual en `%LOCALAPPDATA%\Programs\BattleLens`, sin pedir permisos de administrador. El instalador MUST estar disponible en español e inglés y MUST mostrar la licencia.

#### Scenario: Instalación estándar
- **WHEN** un usuario sin permisos de administrador ejecuta el instalador y acepta los valores por defecto
- **THEN** la aplicación queda instalada, aparece en el menú Inicio y en «Aplicaciones instaladas» de Windows, y no se muestra ningún aviso de UAC

### Requirement: Opciones de instalación
El instalador SHALL ofrecer las opciones: crear un acceso directo en el escritorio (desactivada por defecto), iniciar con Windows (desactivada por defecto) y ejecutar la aplicación al terminar (activada por defecto).

#### Scenario: Inicio con Windows
- **WHEN** el usuario marca «Iniciar con Windows» y después inicia sesión de nuevo
- **THEN** la aplicación arranca automáticamente en la bandeja del sistema

### Requirement: Actualización sobre una versión anterior
WHEN se instala una versión nueva sobre una existente, el instalador SHALL reemplazar los archivos del programa conservando la configuración, los perfiles y el estado del usuario. Si la aplicación está en ejecución, MUST pedir que se cierre antes de continuar.

#### Scenario: Actualización conservando perfiles
- **WHEN** el usuario con perfiles calibrados instala la versión 0.3.0 sobre la 0.2.0
- **THEN** tras la actualización sus perfiles y su configuración siguen disponibles

#### Scenario: Aplicación abierta
- **WHEN** la aplicación está en ejecución y el usuario lanza el instalador
- **THEN** el instalador detecta que está abierta y pide cerrarla antes de copiar archivos

### Requirement: Desinstalación
El desinstalador SHALL eliminar los archivos del programa, los accesos directos y la entrada de inicio con Windows, y MUST preguntar si se borran también los datos del usuario (`%APPDATA%\BattleLens`). La respuesta por defecto es conservarlos.

#### Scenario: Desinstalación conservando datos
- **WHEN** el usuario desinstala y responde «No» a borrar sus datos
- **THEN** se elimina el programa y se mantiene `%APPDATA%\BattleLens`

#### Scenario: Desinstalación completa
- **WHEN** el usuario desinstala y responde «Sí»
- **THEN** no queda ningún archivo de la aplicación en el equipo

### Requirement: Versión portable
El proyecto SHALL generar `BattleLens-<versión>-portable.zip` con la carpeta del programa, ejecutable sin instalar.

#### Scenario: Uso portable
- **WHEN** el usuario descomprime el ZIP en cualquier carpeta y ejecuta `BattleLens.exe`
- **THEN** la aplicación funciona igual que la instalada
