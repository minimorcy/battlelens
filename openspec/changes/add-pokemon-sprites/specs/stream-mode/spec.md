## ADDED Requirements

### Requirement: Imagen en la ficha del stream
El estado (`/state`) SHALL incluir para cada tarjeta la ruta de su sprite (`/sprite/<número>.png`) cuando esté en caché, o `null`. El servidor SHALL servir `/sprite/<número>.png` solo si el número es un entero de hasta 5 cifras y el archivo ya existe en la caché; en cualquier otro caso responde 404. El servidor MUST NOT descargar imágenes.

#### Scenario: Imagen en caché
- **WHEN** el stream muestra a Stufful y `sprites/759.png` existe
- **THEN** `/state` incluye `"/sprite/759.png"` y esa ruta devuelve el PNG

#### Scenario: Ruta no válida
- **WHEN** se pide `/sprite/..%2Fconfig.png` o `/sprite/123.png` sin estar en caché
- **THEN** el servidor responde 404
