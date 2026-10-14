# interface-language Specification

## Purpose
TBD - created by archiving change add-english-ui. Update Purpose after archive.
## Requirements
### Requirement: Idioma de la interfaz
El sistema SHALL mostrar la interfaz en el idioma de `interface.language`: `es` (español), `en` (inglés) o `auto` (por defecto). Con `auto`, MUST usar español si el idioma de la interfaz de Windows es español y, en cualquier otro caso, inglés. La interfaz incluye los menús de la bandeja, las notificaciones, los diálogos (calibración, perfiles, Ajustes, Acerca de, instalación del OCR y errores) y los textos de la ficha y de la ficha del stream que no son datos Pokémon (títulos de sección, captura y su dificultad, veredictos, velocidad, notas de habilidades, perfil de estadísticas, etiquetas de estadísticas y categorías de movimientos).

#### Scenario: Windows en inglés
- **WHEN** `interface.language = "auto"` y Windows está en `en-US`
- **THEN** la bandeja muestra «Recognize now» y la ficha «Weaknesses»

#### Scenario: Windows en español
- **WHEN** `interface.language = "auto"` y Windows está en `es-ES`
- **THEN** la bandeja muestra «Reconocer ahora» y la ficha «Debilidades»

#### Scenario: Otro idioma de Windows
- **WHEN** `interface.language = "auto"` y Windows está en `fr-FR`
- **THEN** la interfaz está en inglés

#### Scenario: Elegido a mano
- **WHEN** `interface.language = "en"` con Windows en español
- **THEN** la interfaz está en inglés

### Requirement: Idiomas de la interfaz y de los datos independientes
El idioma de la interfaz MUST NOT cambiar el de los datos Pokémon (`overlay.language`), que sigue decidiendo los nombres de especies, tipos, movimientos, habilidades y objetos.

#### Scenario: Interfaz en inglés con datos en español
- **WHEN** `interface.language = "en"` y `overlay.language = "es"` y se muestra Machop contra tu Scorbunny
- **THEN** la ficha muestra «Against your Scorbunny», «Weaknesses» y los tipos «Volador», «Psíquico» y «Hada»

### Requirement: Cambio de idioma
Al guardar Ajustes con otro idioma de la interfaz, el sistema SHALL volver a dibujar la ficha visible y la del stream en el idioma nuevo, y SHALL avisar de que los menús y diálogos cambiarán al reiniciar BattleLens.

#### Scenario: Cambiar a inglés
- **WHEN** el usuario elige «English» como idioma de la interfaz y guarda con la ficha visible
- **THEN** la ficha pasa a «Weaknesses» y la bandeja avisa de que los menús cambian al reiniciar

### Requirement: Cobertura de la traducción
Todo texto de la interfaz MUST pasar por la función de traducción, y cada texto marcado MUST tener su traducción al inglés; un test automático SHALL fallar si falta alguna. Los registros de la aplicación y el informe de autocomprobación quedan fuera de la interfaz.

#### Scenario: Texto sin traducir
- **WHEN** se añade al código un texto marcado para traducir sin su versión en inglés
- **THEN** el test de cobertura falla indicando el texto

