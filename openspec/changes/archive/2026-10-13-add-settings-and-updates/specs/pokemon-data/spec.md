## MODIFIED Requirements

### Requirement: Carga del dataset sin conexión
La aplicación SHALL cargar el dataset desde el archivo `pokedex.json` incluido en el paquete y MUST NOT hacer peticiones de red para obtener datos de Pokémon. La única petición de red permitida en tiempo de ejecución es la comprobación de actualizaciones (spec `update-check`), que se puede desactivar.

#### Scenario: Sin conexión
- **WHEN** la aplicación arranca sin conexión a Internet
- **THEN** el reconocimiento y el overlay funcionan con normalidad

#### Scenario: Dataset ausente
- **WHEN** no existe `pokedex.json`
- **THEN** la aplicación muestra un error que indica cómo generarlo y termina

#### Scenario: Comprobación de actualizaciones desactivada
- **WHEN** `updates.check = false` y la aplicación se usa durante una sesión completa
- **THEN** no se realiza ninguna petición de red
