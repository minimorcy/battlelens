## Why

La comparativa «Contra tu X» y las debilidades de la ficha solo miran los tipos. Si el rival es Flygon, la ficha da Tierra ×1 aunque con Levitación sea ×0, y el veredicto puede recomendar un ataque que no le hace nada. Las habilidades ya están en el dataset y el modo Competitivo ya conoce su efecto («Levitación → Tierra ×0»), pero ese efecto no se aplica a ningún cálculo.

Además, las habilidades del dataset son las actuales: Gengar aparece con Cuerpo Maldito incluso en Platino, donde tenía Levitación.

## What Changes

- **Habilidades de cada generación:** el dataset incluye las habilidades que cada Pokémon tuvo en generaciones anteriores (`pokemon_abilities_past` de PokéAPI), y la vista del juego usa las de su generación.
- **Efecto seguro y efecto posible:** si **todas** las habilidades posibles del Pokémon en ese juego cambian la eficacia de un tipo de la misma forma, el cambio es **seguro** y se aplica al cálculo. Por ejemplo, Flygon solo tiene Levitación, así que Tierra le hace ×0. Si solo **alguna** lo cambia, el cambio es **posible**: no altera el cálculo, pero se avisa. Por ejemplo, Bronzong puede tener Levitación.
- **Debilidades, resistencias e inmunidades** (modos Normal y Competitivo): los cambios seguros mueven el tipo a su grupo nuevo, y debajo se explica por qué («Levitación: Tierra ×0»). Los posibles se avisan con «Si tiene Levitación: Tierra ×0».
- **«Contra tu X»:** tus ataques contra el rival tienen en cuenta las habilidades del rival, y sus ataques contra ti las de tu Pokémon. El valor seguro se usa en el multiplicador y en el veredicto. Si el cambio es solo posible, el tipo se marca con «*» y se explica debajo.
- **Movimientos probables contra ti** (modo Competitivo): aplican las habilidades seguras de tu Pokémon.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `pokemon-data`: habilidades de generaciones anteriores en el dataset y en la vista del juego; eficacia defensiva con las habilidades seguras.
- `type-matchup`: la comparativa y el veredicto tienen en cuenta las habilidades seguras y avisan de las posibles.
- `competitive-data`: el multiplicador de los movimientos probables contra ti aplica las habilidades seguras de tu Pokémon.

## Impact

- **Código:** nuevo `core/abilities.py` (tabla de efectos, que sale de `core/competitive.py`, y su resolución), `core/pokedex.py`, `core/matchup.py`, `ui/overlay.py` y `tools/build_dataset.py`.
- **Datos:** se regenera `pokedex.json`, con el campo `slot` en cada habilidad y `past_abilities`. El tamaño crece unos pocos KB.
- **Compatibilidad:** sin cambios de configuración ni de perfiles.
