## MODIFIED Requirements

### Requirement: Regiones opcionales
El sistema SHALL permitir calibrar sobre una captura, para el perfil activo, la región del nombre del 2.º rival, la de tu Pokémon y la del menú de ataques (con el mismo diálogo y las mismas validaciones que la región del rival), y SHALL permitir quitarlas. La región del menú de ataques MUST NOT formar parte de la huella de detección del combate ni de las regiones de nombres.

#### Scenario: Calibrar tu Pokémon
- **WHEN** el usuario elige «Calibrar tu Pokémon…», dibuja el rectángulo y pulsa Enter
- **THEN** el perfil activo guarda esa región como la de tu Pokémon

#### Scenario: Quitar la región del 2.º rival
- **WHEN** el usuario elige «Quitar 2.º rival»
- **THEN** el perfil deja de tener esa región y los reconocimientos vuelven a leer solo un rival

#### Scenario: Calibrar el menú de ataques
- **WHEN** el usuario elige «Calibrar menú de ataques…» con el menú de «Luchar» abierto, dibuja el rectángulo sobre los 4 movimientos y pulsa Enter
- **THEN** el perfil activo guarda esa región como la del menú de ataques, y los perfiles guardados antes de este cambio se siguen cargando sin ella
