## ADDED Requirements

### Requirement: Plantillas de issues
El repositorio SHALL incluir formularios de GitHub para informar de un fallo y para proponer una mejora. El de fallos MUST pedir: versión de BattleLens, emulador, juego e idioma, qué ocurrió, qué se esperaba, pasos para reproducirlo y, si es un fallo de reconocimiento, los archivos de `%APPDATA%\BattleLens\debug` con la instrucción de activar `recognition.debug`. Las issues en blanco MUST desactivarse.

#### Scenario: Informar de un fallo de reconocimiento
- **WHEN** un usuario abre una issue nueva en GitHub
- **THEN** elige entre «Fallo» y «Mejora», y el formulario de fallo le indica cómo adjuntar los archivos de depuración
