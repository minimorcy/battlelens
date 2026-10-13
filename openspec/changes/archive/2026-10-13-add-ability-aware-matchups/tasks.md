## 1. Datos

- [x] 1.1 `tools/build_dataset.py`: `slot` en cada habilidad y `past_abilities` desde `pokemon_abilities_past.csv` (D2), con test en `test_build_dataset.py`
- [x] 1.2 Regenerar `pokedex.json`

## 2. Dominio

- [x] 2.1 `core/abilities.py`: tabla movida desde `competitive.py`, `adjusted_factor`, `AbilityEffect` y `resolve` (D1)
- [x] 2.2 `core/pokedex.py`: `abilities_in(gen)` en especie y forma, `ability_effects` en la vista y grupos ajustados (D2-D3)
- [x] 2.3 `core/matchup.py`: multiplicadores seguros y efectos posibles por tipo (D4)
- [x] 2.4 Tests: Gengar en Platino y actual, Flygon, Bronzong, Shedinja, comparativa Garchomp-Flygon y Garchomp-Bronzong, y veredicto Dugtrio-Gengar

## 3. Interfaz

- [x] 3.1 `ui/overlay.py`: líneas de efecto de habilidad en las eficacias, «*» y explicación en «Contra tu X», y movimientos contra ti con las habilidades seguras (D5)
- [x] 3.2 Tests de UI: línea «Levitación: Tierra ×0» en Normal, aviso de efecto posible y movimiento ×0 contra Flygon

## 4. Cierre

- [x] 4.1 README (en y es: limitaciones), CHANGELOG, todos los tests y `openspec validate --strict`
