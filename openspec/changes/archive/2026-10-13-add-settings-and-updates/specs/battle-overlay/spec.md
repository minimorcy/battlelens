## MODIFIED Requirements

### Requirement: Icono en la bandeja del sistema
El sistema SHALL mostrar un icono en la bandeja del sistema con un menú para: reconocer ahora, activar o desactivar la detección automática, seleccionar ventana objetivo, seleccionar perfil activo, cambiar el juego del perfil activo, gestionar las regiones del perfil activo (recalibrar el rival; calibrar o quitar el 2.º rival; calibrar o quitar tu Pokémon), calibrar un perfil nuevo, eliminar el perfil activo, abrir los ajustes, abrir la carpeta de datos, descargar la versión nueva (solo si hay una disponible) y salir.

#### Scenario: Salida limpia
- **WHEN** el usuario elige "Salir"
- **THEN** se liberan los atajos globales, se detiene la detección automática, se guarda la configuración y el proceso termina

#### Scenario: Estado de la detección visible
- **WHEN** el usuario abre el menú de la bandeja
- **THEN** «Detección automática» aparece marcada si está activada

#### Scenario: Regiones disponibles
- **WHEN** el perfil activo no tiene región del 2.º rival
- **THEN** el submenú «Regiones del perfil» ofrece «Calibrar 2.º rival…» y no ofrece «Quitar 2.º rival»
