# game-catalog Specification

## Purpose
Catálogo de juegos principales (generación, forma regional, nombres) y detección del juego a partir del título de la ventana del emulador.
## Requirements
### Requirement: Catálogo de juegos
El sistema SHALL disponer de un catálogo de juegos principales derivado de los grupos de versiones de PokéAPI. Cada entrada MUST incluir: identificador del grupo de versiones, generación, nombres de cada versión en en/es/fr/de/it y la forma regional que predomina en ese juego (alola, galar, hisui, paldea o ninguna).

#### Scenario: Juego con forma regional
- **WHEN** se consulta el juego `sword-shield`
- **THEN** su generación es 8, su forma regional es `galar` y sus versiones se llaman «Espada» y «Escudo» en español

#### Scenario: Let's Go usa formas de Alola
- **WHEN** se consulta el juego `lets-go-pikachu-lets-go-eevee`
- **THEN** su forma regional es `alola`

### Requirement: Detección del juego por el título
El sistema SHALL detectar el juego a partir del título de una ventana, buscando como palabras completas los nombres de las versiones en cualquiera de los idiomas soportados (sin distinguir mayúsculas ni acentos) y algunos títulos internos de ROM habituales. Si coinciden varios nombres, MUST elegirse el más largo. Los nombres de 4 caracteres o menos («X», «Sol», «Rojo»…) MUST ir precedidos de «Pokémon» para contar. Si no hay coincidencia, el resultado es «desconocido».

#### Scenario: Emulador de Switch
- **WHEN** el título es "Eden Nightly | 4dc69c06f7-master | Pokémon Espada (64-bit) | 1.3.2"
- **THEN** se detecta `sword-shield`

#### Scenario: Nombre contenido en otro más largo
- **WHEN** el título es "mGBA - Pokemon Rojo Fuego"
- **THEN** se detecta `firered-leafgreen`, no `red-blue`

#### Scenario: Título interno de ROM
- **WHEN** el título es "mGBA - POKEMON EMER"
- **THEN** se detecta `emerald`

#### Scenario: Nombre corto sin «Pokémon»
- **WHEN** el título es "Bloc de notas - Lista X"
- **THEN** el resultado es «desconocido»

