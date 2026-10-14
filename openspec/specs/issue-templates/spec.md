# issue-templates Specification

## Purpose
Formularios de GitHub para informar de fallos (con datos de depuración) y proponer mejoras.
## Requirements
### Requirement: Plantillas de issues
El repositorio SHALL incluir formularios de GitHub para informar de un fallo y para proponer una mejora. El de fallos MUST estar en español y en inglés y MUST pedir: versión de BattleLens, emulador, juego e idioma, qué ocurrió, qué se esperaba, pasos para reproducirlo y el ZIP creado con «Informar de un problema…» (bandeja), indicando cómo crearlo; para fallos de reconocimiento, recomendar además activar `recognition.debug` antes de reproducirlo. Los campos de versión, emulador y juego MUST tener los identificadores `version`, `emulator` y `game` para poder rellenarlos desde la URL. Las issues en blanco MUST desactivarse.

#### Scenario: Informar de un fallo de reconocimiento
- **WHEN** un usuario abre una issue nueva en GitHub
- **THEN** elige entre «Fallo» y «Mejora», y el formulario de fallo le indica, en español y en inglés, cómo crear y adjuntar el ZIP del informe

