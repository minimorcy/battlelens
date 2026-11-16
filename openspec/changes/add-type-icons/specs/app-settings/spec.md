## ADDED Requirements

### Requirement: Opción de iconos de tipo
Ajustes › Ficha SHALL incluir la opción «Tipos como iconos (se descargan de PokéAPI la primera vez)», guardada en `overlay.type_icons` (desactivada por defecto). Al activarla se lanza la descarga de los iconos que falten. Al desactivarla, la ficha vuelve a las etiquetas, el sistema MUST NOT hacer peticiones de iconos y la caché no se borra.

#### Scenario: Valor por defecto
- **WHEN** el usuario abre «Ajustes…» con la configuración por defecto
- **THEN** la opción de iconos aparece desactivada

#### Scenario: Desactivar
- **WHEN** el usuario desactiva la opción y guarda con una ficha visible
- **THEN** la ficha se vuelve a dibujar con etiquetas
