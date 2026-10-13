## ADDED Requirements

### Requirement: Catálogo completo de movimientos
`learnsets.json` SHALL incluir los datos de todos los movimientos de PokéAPI (nombres en en/es/fr/de/it, tipo, categoría, potencia, precisión, PP y prioridad), no solo los que se aprenden por subida de nivel, y el sistema MUST permitir buscar un movimiento por su identificador.

#### Scenario: Movimiento de MT
- **WHEN** se busca el movimiento `double-kick` en el catálogo
- **THEN** se obtiene «Doble Patada», de tipo Lucha, físico y con potencia 30
