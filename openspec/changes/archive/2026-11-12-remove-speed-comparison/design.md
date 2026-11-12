## Context

`_matchup_section` añadía una línea «Velocidad: …» con `compare_speed` sobre los rangos de tu Pokémon y del rival.

## Decisions

- Quitar la línea en vez de matizarla («probablemente»): un veredicto dudoso en la sección más consultada estorba más de lo que ayuda, y los rangos ya están en las estadísticas.
- Se mantiene el parámetro `own_level` de `show_battle` (tiene unos 60 llamadores posicionales) aunque ya no se use; los parámetros internos muertos de `_card` y `_matchup_section` se quitan.

## Risks / Trade-offs

- Quien usaba la comparación tendrá que mirar la Velocidad en las estadísticas → aceptable.
