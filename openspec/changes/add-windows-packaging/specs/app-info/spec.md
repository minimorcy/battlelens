## ADDED Requirements

### Requirement: Ventana «Acerca de»
El menú de la bandeja SHALL incluir «Acerca de…», que muestra: nombre y versión de la aplicación, licencia, enlace al repositorio de GitHub, atribución de los datos a PokéAPI y el aviso de proyecto no oficial.

#### Scenario: Consultar la versión
- **WHEN** el usuario abre «Acerca de…» en la versión 0.2.0
- **THEN** ve «BattleLens 0.2.0» y un enlace clicable al repositorio

### Requirement: Aviso de proyecto no oficial
La ventana «Acerca de», el README y la descripción de cada Release SHALL indicar que se trata de un proyecto de fans no afiliado ni respaldado por Nintendo, The Pokémon Company, Creatures Inc. o GAME FREAK inc., y que «Pokémon» y los nombres de Pokémon son marcas registradas de sus titulares.

#### Scenario: Aviso visible
- **WHEN** un usuario abre «Acerca de…» o la página de una Release
- **THEN** encuentra el aviso de proyecto no oficial

### Requirement: Recursos visuales propios
La aplicación y el instalador MUST NOT usar logotipos, imágenes, sprites ni diseños oficiales de Pokémon, incluida la Poké Ball. El icono de la aplicación SHALL ser un diseño original.

#### Scenario: Icono de la bandeja
- **WHEN** la aplicación se ejecuta
- **THEN** el icono de la bandeja y el del ejecutable son el diseño original del proyecto

### Requirement: Licencia
El repositorio SHALL contener un archivo `LICENSE`, que MUST incluirse también en el ejecutable y en el instalador.

#### Scenario: Licencia en el paquete
- **WHEN** se instala la aplicación
- **THEN** el archivo `LICENSE.txt` está en la carpeta de instalación y el instalador lo muestra antes de instalar
