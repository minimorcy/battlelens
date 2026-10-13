## MODIFIED Requirements

### Requirement: Modelo de perfil
Un perfil SHALL contener: identificador, nombre visible, región del nombre del rival, idiomas de OCR preferidos, fecha de creación y, de forma opcional, el juego (identificador del grupo de versiones), la región del nombre del 2.º rival (combates dobles) y la región del nombre de tu Pokémon. Todas las regiones se expresan como fracciones (x, y, ancho, alto) en el rango [0, 1] respecto al área cliente. Los perfiles guardados sin los campos opcionales MUST seguir cargándose, con esos campos sin especificar.

#### Scenario: Región relativa
- **WHEN** se calibra una región de 160×24 px en (480, 40) sobre un área cliente de 960×640
- **THEN** el perfil guarda la región (0.5, 0.0625, 0.1667, 0.0375) con al menos 4 decimales

#### Scenario: Perfil antiguo sin juego
- **WHEN** se carga un perfil guardado antes de existir el campo de juego
- **THEN** se carga correctamente con el juego sin especificar

#### Scenario: Perfil sin regiones opcionales
- **WHEN** se carga un perfil que solo tiene la región del rival
- **THEN** se carga correctamente sin región del 2.º rival ni de tu Pokémon

## ADDED Requirements

### Requirement: Regiones opcionales
El sistema SHALL permitir calibrar sobre una captura, para el perfil activo, la región del nombre del 2.º rival y la de tu Pokémon (con el mismo diálogo y las mismas validaciones que la región del rival), y SHALL permitir quitarlas.

#### Scenario: Calibrar tu Pokémon
- **WHEN** el usuario elige «Calibrar tu Pokémon…», dibuja el rectángulo y pulsa Enter
- **THEN** el perfil activo guarda esa región como la de tu Pokémon

#### Scenario: Quitar la región del 2.º rival
- **WHEN** el usuario elige «Quitar 2.º rival»
- **THEN** el perfil deja de tener esa región y los reconocimientos vuelven a leer solo un rival
