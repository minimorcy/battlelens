## ADDED Requirements

### Requirement: Iconos de tipo en la ficha del stream
Cuando los iconos de tipo están disponibles, el payload de la ficha del stream SHALL incluir para cada tipo la ruta `/type-icon/<id>.png`, y la ficha HTML SHALL mostrar el icono en lugar de la etiqueta. El servidor SHALL servir esa ruta solo si `<id>` cumple `^\d{1,2}$` y el archivo ya existe en la caché (404 en otro caso). MUST NOT descargar nada ni construir rutas a partir de la petición más allá de ese entero.

#### Scenario: Icono en caché
- **WHEN** OBS pide `/type-icon/10.png` y el icono está en la caché
- **THEN** el servidor devuelve el PNG

#### Scenario: Ruta no válida
- **WHEN** se pide `/type-icon/../config.toml` o un número que no está en la caché
- **THEN** el servidor responde 404
