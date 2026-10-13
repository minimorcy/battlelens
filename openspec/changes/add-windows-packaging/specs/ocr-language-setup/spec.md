## ADDED Requirements

### Requirement: Detección del OCR que falta
Al arrancar, el sistema SHALL comprobar si hay algún paquete de OCR de Windows compatible con los idiomas soportados (es, en, fr, de, it). Si no lo hay, MUST mostrar un aviso y MUST añadir al menú de la bandeja la opción «Instalar OCR de Windows…».

#### Scenario: Sin paquete de OCR
- **WHEN** la aplicación arranca en un equipo sin paquetes de OCR compatibles
- **THEN** se muestra un aviso que explica el problema y el menú de la bandeja incluye «Instalar OCR de Windows…»

#### Scenario: Con paquete de OCR
- **WHEN** la aplicación arranca en un equipo con el OCR en español o en inglés instalado
- **THEN** no se muestra el aviso ni la opción de instalación

### Requirement: Elección del idioma a instalar
El sistema SHALL proponer el paquete de OCR que corresponda al idioma de la interfaz de Windows, si es uno de los soportados. Si no lo es, MUST proponer inglés (en-US).

#### Scenario: Windows en español
- **WHEN** el idioma de la interfaz de Windows es es-ES
- **THEN** se propone instalar `Language.OCR~~~es-ES~0.0.1.0`

#### Scenario: Windows en un idioma no soportado
- **WHEN** el idioma de la interfaz de Windows es pl-PL
- **THEN** se propone instalar `Language.OCR~~~en-US~0.0.1.0`

### Requirement: Instalación guiada con elevación
WHEN el usuario confirma la instalación, el sistema SHALL ejecutar `Add-WindowsCapability` en PowerShell con elevación de permisos (UAC), esperar a que termine sin bloquear la interfaz, volver a comprobar el OCR e informar del resultado. Si el OCR sigue sin estar disponible tras una instalación correcta, MUST pedir reiniciar la aplicación.

#### Scenario: Instalación correcta
- **WHEN** el usuario acepta el UAC y la instalación termina bien
- **THEN** se informa del éxito y el reconocimiento funciona (tras reiniciar la app si hace falta)

#### Scenario: UAC cancelado
- **WHEN** el usuario cancela el aviso de UAC
- **THEN** no se instala nada, se informa de que se canceló y la opción del menú sigue disponible

#### Scenario: Fallo de instalación
- **WHEN** la instalación falla, por ejemplo por falta de conexión
- **THEN** se muestra un error con las instrucciones para instalarlo manualmente desde la Configuración de Windows
