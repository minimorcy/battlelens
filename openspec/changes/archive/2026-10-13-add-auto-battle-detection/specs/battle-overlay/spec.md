## MODIFIED Requirements

### Requirement: Icono en la bandeja del sistema
El sistema SHALL mostrar un icono en la bandeja del sistema con un menú para: reconocer ahora, activar o desactivar la detección automática, seleccionar ventana objetivo, seleccionar perfil activo, cambiar el juego del perfil activo, calibrar, recalibrar o eliminar el perfil activo, abrir la carpeta de datos y salir.

#### Scenario: Salida limpia
- **WHEN** el usuario elige "Salir"
- **THEN** se liberan los atajos globales, se detiene la detección automática, se guarda la configuración y el proceso termina

#### Scenario: Estado de la detección visible
- **WHEN** el usuario abre el menú de la bandeja
- **THEN** «Detección automática» aparece marcada si está activada
