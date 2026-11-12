## MODIFIED Requirements

### Requirement: Resaltar los tipos de la ficha
Si hay una ficha visible (de combate o del buscador), la tabla SHALL resaltar las columnas (defensor) de los tipos de los rivales de esa ficha. Si la ficha muestra también tu Pokémon, la tabla SHALL resaltar con otro color las filas (atacante) de sus tipos. Las casillas donde se cruzan, tus ataques de tu tipo contra los tipos del rival, SHALL quedar marcadas. Mientras haya algo resaltado, una leyenda en la cabecera SHALL indicar el color del rival y el de tu Pokémon. En combates dobles SHALL resaltarse juntas las columnas de los tipos de los dos rivales. El resaltado SHALL actualizarse cuando se muestra otra ficha o cambia la forma, y SHALL desaparecer cuando la ficha se oculta.

#### Scenario: Rival en combate
- **WHEN** la ficha muestra a Rapidash de Galar y la tabla está abierta
- **THEN** las columnas Psíquico y Hada aparecen resaltadas

#### Scenario: Con tu Pokémon
- **WHEN** la ficha muestra a Rapidash de Galar contra tu Scorbunny (Fuego)
- **THEN** la fila Fuego aparece resaltada con el color de tu Pokémon, y las casillas Fuego→Psíquico y Fuego→Hada quedan marcadas

#### Scenario: Combate doble
- **WHEN** la ficha muestra a un rival Agua y a otro Roca
- **THEN** las columnas Agua y Roca aparecen resaltadas a la vez

#### Scenario: Ficha oculta
- **WHEN** el usuario oculta la ficha con la tabla abierta
- **THEN** ninguna fila ni columna queda resaltada
