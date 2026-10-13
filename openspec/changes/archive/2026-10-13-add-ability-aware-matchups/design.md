## Context

`core/competitive.py` tiene la tabla `ABILITY_TYPE_EFFECTS`, pero solo se usa para poner etiquetas en el modo Competitivo. `Pokedex.view` calcula `matchups` solo con los tipos, y `core/matchup.py` hace lo mismo. Las habilidades del dataset son las actuales y no llevan el número de hueco.

## Goals / Non-Goals

**Goals:**
- Que ninguna inmunidad por habilidad segura (Levitación de Flygon, Superguarda de Shedinja…) quede oculta en la ficha ni en el veredicto.
- Avisar de las posibles sin dar por hecho algo que no sabemos.
- Habilidades correctas por generación.

**Non-Goals:**
- Saber qué habilidad tiene realmente el rival (no se ve en pantalla).
- Habilidades que anulan otras (Rompemoldes…), objetos (Globo Helium) y climas.
- Cambios del efecto de una habilidad entre generaciones (la tabla describe el efecto actual).

## Decisions

### D1. `core/abilities.py`
La tabla `ABILITY_TYPE_EFFECTS`, `ABILITY_NOTES` y `ability_effects()` pasan de `competitive.py` a este módulo. `competitive.py` las reexporta para no romper importaciones. Se añade lo siguiente:
- `adjusted_factor(identifier, attacking, factor) -> float`: aplica una habilidad a un multiplicador. Las inmunidades y los factores de la tabla multiplican. Superguarda deja en 0 todo lo que no sea supereficaz. Filtro, Roca Sólida y Armadura Prisma multiplican por 0,75 los supereficaces.
- `AbilityEffect(type, base, factor, abilities, certain)`: lo que cambia en un tipo de ataque. `abilities` son las `Ability` que lo causan.
- `resolve(abilities, attacking, base) -> (factor_final, AbilityEffect | None)`: calcula el resultado de cada habilidad. Si todos coinciden y difieren de `base`, el efecto es seguro y `factor_final` es el nuevo valor. Si alguno difiere, es posible: `factor_final = base`, y el efecto lista las habilidades que lo cambian con su valor. Cuando hay varias habilidades posibles con valores distintos, se guarda un efecto por cada valor.

*Alternativa descartada:* tomar el peor caso (suponer siempre la habilidad más favorable al rival). Esconde debilidades reales de Pokémon como Bronzong, donde lo habitual es la otra habilidad.

### D2. Habilidades por generación en el dataset
`build_dataset.py` añade `slot` a cada habilidad y `past_abilities: [{until_generation, slot, ability | null}]` a especies y formas, a partir de `pokemon_abilities_past.csv`. `Species.abilities_in(gen)` y `Form.abilities_in(gen)` sustituyen cada hueco por la entrada con el menor `until_generation >= gen`, o quitan el hueco si la entrada es `null`. Es la misma regla que ya usa `types_in`. Después se siguen aplicando los filtros de generación (sin habilidades antes de la Gen 3, sin oculta antes de la Gen 5).

### D3. La vista lleva los efectos
`SpeciesView` añade `ability_effects: tuple[AbilityEffect, ...]`, con los efectos defensivos de sus habilidades para cada tipo de ataque existente en la generación. `matchups` se calcula con los factores seguros, pero un factor seguro que no está en los grupos (×1,5, ×1,25…) no mueve el tipo. Así la interfaz y `matchup()` no repiten el cálculo.

### D4. `matchup()` con habilidades
`Matchup` añade `offense_effects` y `defense_effects` (`dict[tipo, AbilityEffect]`). `offense` y `defense` siguen siendo pares `(tipo, multiplicador)`, ahora con el multiplicador seguro. Para obtenerlo se busca el tipo en `rival.ability_effects` (o en `own.ability_effects`) sobre el multiplicador de los tipos. El veredicto usa estos multiplicadores. Los efectos de las vistas se calculan con la tabla de su generación, que es la misma que usa la comparativa.

### D5. Interfaz
- En la sección de eficacias, debajo de los grupos, se añade una línea por habilidad con efectos: «Levitación: Tierra ×0» si es seguro, o «Si tiene Levitación: Tierra ×0» si es posible. Las habilidades con nota (Superguarda, Filtro…) muestran la nota en lugar de la lista de tipos (`objectName` `ability-effect-line`). Va en ambos modos.
- En «Contra tu X», la pastilla muestra el multiplicador seguro. Si el efecto es posible, añade «*» y debajo una línea en gris («Tierra: ×0 si tiene Levitación»). Si es seguro, se explica con «Tierra: ×0 por Levitación».
- En los movimientos probables, el multiplicador contra ti se toma de `own.ability_effects` cuando el efecto es seguro.

## Risks / Trade-offs

- [Más texto en la ficha Normal] → Solo aparece cuando la especie tiene una habilidad de la tabla, que son pocas.
- [La tabla describe el efecto actual] → Por ejemplo, Ignífugo no cambió. Si algún efecto cambia entre generaciones, se documenta como limitación.
- [Habilidades ocultas en Pokémon salvajes] → Cuentan como posibles. Es lo correcto, porque puede tenerlas.

## Migration Plan

Se regenera el dataset. El cargador acepta datasets antiguos sin `slot` ni `past_abilities`, para los tests y las instalaciones a medias.

## Open Questions

Ninguna.
