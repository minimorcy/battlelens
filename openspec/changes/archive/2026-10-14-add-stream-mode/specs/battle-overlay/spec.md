## ADDED Requirements

### Requirement: Opciones del modo stream en la bandeja
La bandeja SHALL incluir «Modo stream» (casilla que activa o desactiva el modo) y «Copiar URL para OBS» (activa solo con el servidor en marcha), y el atajo global «Mostrar/ocultar ficha del stream» (por defecto `Ctrl+Alt+S`, configurable en `hotkeys.toggle_stream`).

#### Scenario: Copiar la URL
- **WHEN** el modo stream está activo en el puerto 17320 y el usuario elige «Copiar URL para OBS»
- **THEN** el portapapeles contiene `http://localhost:17320/` y la bandeja lo confirma

#### Scenario: Sin servidor
- **WHEN** el modo stream está desactivado
- **THEN** «Copiar URL para OBS» aparece deshabilitada
