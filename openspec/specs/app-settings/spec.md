# app-settings Specification

## Purpose
Ventana de ajustes para editar la configuración sin tocar archivos y aplicarla al momento.
## Requirements
### Requirement: Ventana de ajustes
El sistema SHALL ofrecer desde la bandeja una ventana «Ajustes» para editar todos los valores de `config.toml`: atajos (reconocer, calibrar, ocultar, cambiar de modo, cambiar de forma), modo e idioma de la ficha, umbral de reconocimiento, modo depuración, ocultación automática de la ficha, detección automática (activada, intervalo y ocultación al terminar el combate) y comprobación de actualizaciones.

#### Scenario: Abrir con los valores actuales
- **WHEN** el usuario abre «Ajustes…»
- **THEN** cada control muestra el valor vigente de la configuración

#### Scenario: Atajo de cambiar de forma
- **WHEN** el usuario abre «Ajustes…» con la configuración por defecto
- **THEN** el atajo «Cambiar de forma» muestra `Ctrl+Alt+F`

### Requirement: Validación
La ventana SHALL validar los valores antes de guardar con las mismas reglas que `config.toml` (atajos con modificador y tecla conocida; rangos numéricos) y MUST NOT guardar si alguno no es válido, indicando cuál.

#### Scenario: Atajo sin modificador
- **WHEN** el usuario escribe «F8» como atajo de reconocer y pulsa Guardar
- **THEN** se muestra el error junto a ese campo y no se guarda nada

### Requirement: Guardar y aplicar sin reiniciar
WHEN el usuario guarda, el sistema SHALL reescribir `config.toml` (conservando los comentarios explicativos de la plantilla) y MUST aplicar los cambios sin reiniciar: volver a registrar los atajos, idioma de la ficha, umbral, depuración, ocultación automática y parámetros de la detección.

#### Scenario: Cambio de idioma
- **WHEN** el usuario cambia el idioma a «en» y guarda
- **THEN** la siguiente ficha se muestra en inglés y `config.toml` contiene `language = "en"`

#### Scenario: Cambio de atajo
- **WHEN** el usuario cambia el atajo de reconocer a `Ctrl+Alt+R` y guarda
- **THEN** `Ctrl+Alt+R` reconoce y `Ctrl+Alt+P` deja de estar registrado

#### Scenario: Ida y vuelta
- **WHEN** se guarda una configuración y se vuelve a leer `config.toml`
- **THEN** se obtienen exactamente los mismos valores

