## MODIFIED Requirements

### Requirement: Ventana de ajustes
El sistema SHALL ofrecer desde la bandeja una ventana «Ajustes» para editar todos los valores de `config.toml`: atajos (reconocer, calibrar, ocultar, cambiar de modo, cambiar de forma, mostrar u ocultar la ficha del stream), modo e idioma de la ficha, umbral de reconocimiento, modo depuración, ocultación automática de la ficha, detección automática (activada, intervalo y ocultación al terminar el combate), modo stream (activado, puerto entre 1024 y 65535 y modo de su ficha) y comprobación de actualizaciones.

#### Scenario: Abrir con los valores actuales
- **WHEN** el usuario abre «Ajustes…»
- **THEN** cada control muestra el valor vigente de la configuración

#### Scenario: Atajo de cambiar de forma
- **WHEN** el usuario abre «Ajustes…» con la configuración por defecto
- **THEN** el atajo «Cambiar de forma» muestra `Ctrl+Alt+F`

#### Scenario: Modo stream
- **WHEN** el usuario activa el modo stream en Ajustes, cambia el puerto a 18000 y guarda
- **THEN** el servidor se reinicia en el puerto 18000 sin reiniciar la aplicación
