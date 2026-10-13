# pokemon-data Specification

## Purpose
Dataset local de especies generado desde PokéAPI y cálculos derivados (eficacia de tipos), disponible sin conexión.
## Requirements
### Requirement: Generación del dataset
El proyecto SHALL incluir un script (`tools/build_dataset.py`) que descargue los CSV públicos de PokéAPI y genere un único archivo `pokedex.json` con, por especie: número de Pokédex nacional, nombres en en/es/fr/de/it, tipos de la forma por defecto, estadísticas base (PS, Ataque, Defensa, At. Esp., Def. Esp., Velocidad) y habilidades (normales y oculta) con su nombre en español e inglés. Además MUST incluir la tabla de eficacia de tipos y los nombres de los tipos en español.

#### Scenario: Generación completa
- **WHEN** se ejecuta el script con conexión a Internet
- **THEN** se genera `pokedex.json` con todas las especies publicadas en PokéAPI y la tabla completa de 18×18 tipos

#### Scenario: Descarga fallida
- **WHEN** falla la descarga de algún CSV
- **THEN** el script termina con código de salida distinto de 0 y no sobrescribe un `pokedex.json` existente

### Requirement: Carga del dataset sin conexión
La aplicación SHALL cargar el dataset desde el archivo `pokedex.json` incluido en el paquete y MUST NOT hacer peticiones de red en tiempo de ejecución.

#### Scenario: Sin conexión
- **WHEN** la aplicación arranca sin conexión a Internet
- **THEN** el reconocimiento y el overlay funcionan con normalidad

#### Scenario: Dataset ausente
- **WHEN** no existe `pokedex.json`
- **THEN** la aplicación muestra un error que indica cómo generarlo y termina

### Requirement: Consulta de especie
El sistema SHALL devolver la ficha completa de una especie a partir de su número de Pokédex.

#### Scenario: Consulta válida
- **WHEN** se consulta la especie #6
- **THEN** se obtiene Charizard, tipos Fuego/Volador, estadísticas base 78/84/78/109/85/100 (total 534) y habilidades Mar Llamas y Poder Solar (oculta)

### Requirement: Eficacia de tipos defensiva
El sistema SHALL calcular, para la combinación de tipos de una especie, el multiplicador de daño recibido de cada uno de los 18 tipos de ataque (producto de los multiplicadores individuales) y MUST agruparlos en ×4, ×2, ×½, ×¼ y ×0.

#### Scenario: Doble debilidad
- **WHEN** se calcula la eficacia para Charizard (Fuego/Volador)
- **THEN** Roca aparece en ×4; Agua y Eléctrico en ×2; Fuego, Lucha, Acero y Hada en ×½; Planta y Bicho en ×¼; Tierra en ×0

#### Scenario: Inmunidad
- **WHEN** se calcula la eficacia para Gengar (Fantasma/Veneno)
- **THEN** Normal y Lucha aparecen en ×0

