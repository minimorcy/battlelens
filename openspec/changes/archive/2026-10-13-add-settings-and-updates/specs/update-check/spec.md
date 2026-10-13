## ADDED Requirements

### Requirement: Comprobación de versión nueva
IF `updates.check` es `true` (por defecto), THEN al arrancar, y como máximo una vez cada 24 horas, el sistema SHALL consultar en segundo plano la última Release publicada de `minimorcy/battlelens` en la API de GitHub y compararla con la versión instalada. La petición MUST NOT incluir datos del usuario y MUST tener un tiempo de espera de 5 s.

#### Scenario: Hay una versión nueva
- **WHEN** la versión instalada es 0.2.0 y la última Release es v0.3.0
- **THEN** se avisa en la bandeja «BattleLens 0.3.0 disponible» y aparece en el menú «Descargar BattleLens 0.3.0…», que abre la página de la Release en el navegador

#### Scenario: Versión al día
- **WHEN** la última Release es igual o anterior a la versión instalada
- **THEN** no se muestra ningún aviso ni opción

#### Scenario: Sin conexión o sin Releases
- **WHEN** la consulta falla, agota el tiempo de espera o el repositorio aún no tiene Releases
- **THEN** no se muestra nada al usuario y se anota en el log

#### Scenario: Comprobación reciente
- **WHEN** la última comprobación se hizo hace menos de 24 horas
- **THEN** no se vuelve a consultar al arrancar

### Requirement: Comparación de versiones
El sistema SHALL comparar versiones con formato `X.Y.Z` (con o sin «v» delante) numéricamente por componentes; una etiqueta con formato no válido se considera no más nueva.

#### Scenario: Comparación numérica
- **WHEN** se comparan 0.10.0 y 0.9.3
- **THEN** 0.10.0 es más nueva
