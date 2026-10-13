## 1. Datos

- [x] 1.1 `tools/build_dataset.py`: formas alternativas y megas con `kind` e `introduced`, filtros y deduplicación (D1), y `order` en los juegos; tests
- [x] 1.2 Regenerar `pokedex.json`

## 2. Dominio

- [x] 2.1 `core/pokedex.py`: `kind`/`introduced` en `Form`, `order` en `Game`, `form_available`, `view(..., form=)`, `form_id`/`base_pokemon` y `form_cycle` (D2-D3)
- [x] 2.2 Tests: Rotom en Platino, megas en Espada y X/Y, Giratina en Diamante, Unown, Rotom Lavado y secuencia de Zigzagoon

## 3. App e interfaz

- [x] 3.1 `core/config.py` y `ui/settings.py`: atajo `cycle_form` (D6)
- [x] 3.2 `app.py`: atajo, `_form_choice` y su limpieza al cambiar de rivales (D4)
- [x] 3.3 `ui/overlay.py`: pista del atajo y movimientos de la forma base (D5)
- [x] 3.4 Tests: alternar Rotom, la elección se mantiene con la misma clave y se olvida con otra, sin formas no cambia, ajustes con el atajo y movimientos de Mega Charizard X

## 4. Cierre

- [x] 4.1 README (en y es: uso, configuración y limitaciones), CHANGELOG, `docs/manual-validation.md`, todos los tests y `openspec validate --strict`
