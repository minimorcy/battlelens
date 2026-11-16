## ADDED Requirements

### Requirement: Opción de imágenes del Pokémon
Ajustes SHALL incluir la casilla «Mostrar la imagen del Pokémon (se descarga de PokéAPI la primera vez)», guardada en `overlay.sprites` (desactivada por defecto, como los iconos de tipo). Al desactivarla, la ficha deja de mostrar imágenes y el sistema MUST NOT hacer peticiones de sprites; la caché no se borra.

#### Scenario: Valor por defecto
- **WHEN** el usuario abre «Ajustes…» con la configuración por defecto
- **THEN** la casilla de la imagen del Pokémon aparece desmarcada

#### Scenario: Desactivar
- **WHEN** el usuario desmarca la casilla y guarda con una ficha visible
- **THEN** la ficha se vuelve a dibujar sin imagen
