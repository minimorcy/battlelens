## ADDED Requirements

### Requirement: Descarga y caché de sprites
Con `overlay.sprites` activado, el sistema SHALL descargar bajo demanda el sprite de cada Pokémon mostrado desde el repositorio público de sprites de PokéAPI, la primera vez que aparece, y guardarlo en la carpeta `sprites` de los datos del usuario. La descarga MUST hacerse en segundo plano, sin retrasar la ficha ni el reconocimiento. El sprite MUST guardarse recortado a su contorno visible (sin el margen transparente). Las imágenes MUST NOT incluirse en el repositorio ni en el instalador.

#### Scenario: Primera vez
- **WHEN** se reconoce a Stufful por primera vez con conexión
- **THEN** la ficha aparece en el acto y, al terminar la descarga, `sprites/759.png` existe y la cabecera muestra la imagen

#### Scenario: Ya en caché
- **WHEN** se reconoce a Stufful y `sprites/759.png` ya existe
- **THEN** la cabecera muestra la imagen sin hacer ninguna petición

#### Scenario: Sin conexión
- **WHEN** se reconoce a un Pokémon sin imagen en caché y la descarga falla
- **THEN** la ficha se muestra sin imagen y no se reintenta la descarga de ese Pokémon durante la sesión

#### Scenario: Recorte
- **WHEN** se guarda un sprite de 96×96 cuyo contenido ocupa la zona inferior izquierda
- **THEN** el archivo guardado contiene solo la caja de los píxeles visibles

#### Scenario: Respuesta no válida
- **WHEN** la descarga devuelve algo que no es un PNG o pesa más de 256 KB
- **THEN** no se guarda nada y la ficha se muestra sin imagen
