## 1. Datos

- [x] 1.1 `tools/build_dataset.py`: todos los movimientos en `learnsets.json`; `core/learnsets.py`: `move(identifier)` y `all_moves()` (D2); tests
- [x] 1.2 Regenerar `learnsets.json`

## 2. Dominio

- [x] 2.1 `core/profiles.py`: `moves_region` fuera de `regions()`, con compatibilidad JSON (D1)
- [x] 2.2 `core/normalize.py` (`clean_text`) y `core/moves.py`: `MoveMatcher`, `MoveMemory` (D2, D4)
- [x] 2.3 `core/detection.py`: `RegionWatcher` (D3)
- [x] 2.4 `vision/preprocess.py` (`moves_variants`) y `pipeline.py` (`read_moves` y `RecognitionResult.moves`) (D2-D3)
- [x] 2.5 Tests: menú de Espada, lectura con errores, menú cerrado, memoria (guardar, cambiar y persistir), vigilante (estable una vez, sin repetir) y perfil con región de menú (huella sin cambios)

## 3. App e interfaz

- [x] 3.1 `ui/tray.py` y `app.py`: calibrar y quitar el menú de ataques; vigilante del menú, lectura en segundo plano, memoria y redibujo (D1, D3-D4)
- [x] 3.2 `ui/overlay.py`: apartado «Tus movimientos» (guardados o probables) con multiplicadores contra cada rival (D5)
- [x] 3.3 Tests de UI y de controlador: Scorbunny contra Rookidee, Tierra contra Flygon, probables, la lectura del menú actualiza la ficha y submenú con la nueva región

## 4. Cierre

- [x] 4.1 README (en y es: uso y limitaciones), CHANGELOG, `docs/manual-validation.md`, todos los tests y `openspec validate --strict`
