# own-moves Specification

## Purpose
TBD - created by archiving change add-own-moves. Update Purpose after archive.
## Requirements
### Requirement: Lectura del menú de ataques
Si el perfil tiene la región del menú de ataques, el sistema SHALL leerla con el OCR (con las variantes propias del menú) y buscar en el texto de cada variante nombres de movimiento en en/es/fr/de/it: cada secuencia de 1 a 3 palabras consecutivas se compara con el catálogo de movimientos, y se aceptan las coincidencias de puntuación ≥ 80 que no se solapan, sin repetir movimiento. El resultado combina las variantes: los 4 movimientos encontrados en más variantes, en el orden en que aparecen. La lectura MUST darse por válida solo si encuentra al menos 2 movimientos. El texto restante (PP, tipos, otras palabras del menú) se ignora.

#### Scenario: Menú de Espada
- **WHEN** el OCR del menú lee "Ascuas PP 25/25 Placaje PP 35/35 Gruñido PP 40/40 Ataque Rápido PP 30/30"
- **THEN** los movimientos son Ascuas, Placaje, Gruñido y Ataque Rápido

#### Scenario: Lectura con errores
- **WHEN** el OCR lee "EMBER TACKIE GROWL QUICK ATTAGK"
- **THEN** los movimientos son Ascuas, Placaje, Gruñido y Ataque Rápido

#### Scenario: Rejilla de GBA
- **WHEN** una variante lee "TACKLE QUICK ATTACK" y otra "EMBER GROWL TACKLE QUICK ATTACK"
- **THEN** los movimientos son Placaje, Ataque Rápido, Ascuas y Gruñido

#### Scenario: Menú cerrado
- **WHEN** en la región se ve el escenario o un texto de combate con como mucho una palabra parecida a un movimiento
- **THEN** la lectura no es válida y no cambia nada

### Requirement: Vigilancia del menú de ataques
Con la detección automática activa, el sistema SHALL vigilar la región del menú de ataques con su propia huella, independiente de la del combate (cambiar el menú MUST NOT ocultar ni volver a reconocer la ficha). Cuando la huella del menú se mantiene estable durante 2 ciclos y es distinta de la última leída, se lee el menú. El reconocimiento manual también lee el menú si la región existe.

#### Scenario: Abrir el menú
- **WHEN** el usuario elige «Luchar» y el menú queda quieto
- **THEN** se lee el menú una vez, y no vuelve a leerse mientras no cambie

#### Scenario: El menú no oculta la ficha
- **WHEN** la región del menú cambia continuamente por las animaciones del combate
- **THEN** la ficha sigue visible mientras el nombre del rival no cambie

### Requirement: Memoria de movimientos
Cuando una lectura del menú es válida y se conoce tu Pokémon (región de tu Pokémon reconocida), el sistema SHALL guardar esos movimientos para el perfil activo y esa especie, sustituyendo los anteriores, en `moves.json` dentro del directorio de datos, y MUST volver a dibujar la ficha visible si han cambiado. Sin tu Pokémon reconocido, la lectura se descarta.

#### Scenario: Recordar entre combates
- **WHEN** se leyeron los movimientos de tu Scorbunny en un combate y en otro combate vuelve a salir Scorbunny
- **THEN** la ficha muestra esos movimientos sin abrir el menú

#### Scenario: Movimientos nuevos
- **WHEN** tu Scorbunny aprende Doble Patada y se lee el menú
- **THEN** los movimientos guardados de Scorbunny pasan a ser los nuevos y la ficha se actualiza

### Requirement: Apartado «Tus movimientos»
Si se conoce tu Pokémon, cada tarjeta SHALL incluir, en ambos modos, el apartado «Tus movimientos» con los guardados para esa especie o, si no los hay y se conoce su nivel, sus movimientos probables (spec `competitive-data`) con el título «Tus movimientos (probables)». Cada movimiento muestra su tipo, su nombre y, si no es de estado, su multiplicador contra ese rival con los efectos seguros de las habilidades del rival (con «*» si hay alguno posible); los de estado muestran «Estado». Sin movimientos guardados ni nivel, el apartado no aparece.

#### Scenario: Movimiento de otro tipo
- **WHEN** tu Scorbunny tiene guardados Ascuas, Placaje, Doble Patada y Ataque Rápido, y el rival es Rookidee (Volador)
- **THEN** la tarjeta muestra Ascuas ×1, Placaje ×1, Doble Patada ×½ y Ataque Rápido ×1

#### Scenario: Habilidad del rival
- **WHEN** tienes un movimiento de tipo Tierra y el rival es Flygon (solo Levitación)
- **THEN** ese movimiento aparece con ×0

#### Scenario: Probables
- **WHEN** no hay movimientos guardados de tu Pokémon y se ha leído su nivel
- **THEN** el apartado se titula «Tus movimientos (probables)» y muestra los que aprende hasta ese nivel

