## 1. Datos

- [x] 1.1 `tools/build_dataset.py`: `past_stats` desde `pokemon_stats_past.csv`, con `special` (D1) y test
- [x] 1.2 Regenerar `pokedex.json`

## 2. Dominio

- [x] 2.1 `core/pokedex.py`: `stats_in(gen)` en especie y forma, la vista con las estadísticas de su generación y `stat_keys` (D2-D3)
- [x] 2.2 `core/competitive.py`: `stat_formula`, fórmulas Gen 1-2, Let's Go y Leyendas: Arceus, `view_ranges` y `stat_profile` con Especial (D4-D5)
- [x] 2.3 Tests: Pikachu en `black-white`, actual y `red-blue`; rangos Gen 1, Let's Go (rival y tuyo) y Arceus; Garchomp y Shedinja sin cambios

## 3. Interfaz

- [x] 3.1 `ui/overlay.py` y `ui/theme.py`: filas según `stat_keys`, etiqueta «Especial» y rangos con `view_ranges` (rival y tu velocidad)
- [x] 3.2 Test de UI: ficha competitiva de Pikachu en `red-blue` con fila «Especial» y sin At. Esp.

## 4. Cierre

- [x] 4.1 README (en y es: quitar las limitaciones resueltas), CHANGELOG, `docs/manual-validation.md`, todos los tests y `openspec validate --strict`
