## ADDED Requirements

### Requirement: Integración continua
El repositorio SHALL tener un flujo de GitHub Actions que, en cada push a `main` y en cada pull request, ejecute en `windows-latest` todos los tests y `openspec validate --all --strict`.

#### Scenario: Pull request con un test roto
- **WHEN** se abre un pull request que rompe un test
- **THEN** el flujo de CI falla y el pull request muestra el estado en rojo

### Requirement: Tests dependientes del entorno
Los tests que requieren el OCR de Windows SHALL omitirse (skip), indicando el motivo, cuando el equipo no tiene ningún paquete de OCR compatible, en lugar de fallar.

#### Scenario: Runner sin OCR en español ni inglés
- **WHEN** los tests se ejecutan en un equipo sin paquetes de OCR compatibles
- **THEN** los tests de OCR aparecen como omitidos con el motivo y el resto se ejecuta con normalidad

### Requirement: Publicación de versiones
WHEN se publica una etiqueta con formato `vX.Y.Z`, el sistema de CI SHALL: comprobar que coincide con la versión de `pyproject.toml`, ejecutar los tests, compilar el ejecutable, pasar su autocomprobación, generar el instalador y el ZIP portable, calcular sus SHA-256 y crear una *Release* de GitHub con esos archivos y con las notas de la sección correspondiente de `CHANGELOG.md`.

#### Scenario: Publicación correcta
- **WHEN** se publica la etiqueta `v0.2.0` y `pyproject.toml` indica 0.2.0
- **THEN** aparece en GitHub la Release «v0.2.0» con `BattleLens-Setup-0.2.0.exe`, `BattleLens-0.2.0-portable.zip` y `SHA256SUMS.txt`

#### Scenario: Versión no coincidente
- **WHEN** se publica la etiqueta `v0.2.1` y `pyproject.toml` indica 0.2.0
- **THEN** el flujo falla antes de compilar y no se crea ninguna Release

#### Scenario: Autocomprobación fallida
- **WHEN** el ejecutable compilado no supera `--self-test`
- **THEN** el flujo falla y no se crea ninguna Release

### Requirement: Artefactos de compilación en CI
El flujo de CI SHALL guardar el instalador y el ZIP de cada compilación de `main` como artefactos descargables durante 14 días, para poder probarlos antes de publicar una versión.

#### Scenario: Probar una compilación de main
- **WHEN** se fusiona un cambio en `main`
- **THEN** la ejecución del flujo ofrece el instalador y el ZIP como artefactos descargables
