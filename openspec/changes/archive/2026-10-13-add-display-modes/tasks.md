## 1. Datos

- [x] 1.1 `tools/build_dataset.py`: peso, altura y EVs por especie y forma; `learnsets.json` deduplicado con los datos de los movimientos (D3)
- [x] 1.2 Tests del script con CSV mínimos (EVs, peso, deduplicación de listas, datos de movimiento)

## 2. Dominio

- [x] 2.1 `core/normalize.py`: `extract_level()` (D2); `pipeline.py`: niveles por región en el resultado
- [x] 2.2 `core/learnsets.py`: carga diferida, elección del juego (D3) y `probable_moves()` (D4)
- [x] 2.3 `core/competitive.py`: rangos de estadísticas (D5), velocidad, efectos de habilidades (D6), Patada Baja/Hierba Lazo, perfil y EVs
- [x] 2.4 Tests: todos los escenarios de `level-reading` y `competitive-data`

## 3. Configuración e interfaz

- [x] 3.1 `core/config.py`: `overlay.mode` y `hotkeys.toggle_mode` en la plantilla y la validación
- [x] 3.2 `ui/overlay.py`: secciones según el modo (D1) y nuevas secciones competitivas
- [x] 3.3 `ui/tray.py` (submenú «Modo de la ficha»), `ui/settings.py` (modo y atajo), `app.py` (niveles, cambio de modo, nuevo dibujo de la última batalla y atajo)
- [x] 3.4 Tests de UI y de controlador: escenarios de `display-modes` (ficha compacta, ficha competitiva, cambio con la ficha abierta) y Ajustes

## 4. Cierre

- [x] 4.1 README (modos y limitaciones), CHANGELOG y `docs/manual-validation.md`; recompilar, ejecutar todos los tests y `openspec validate --all --strict`
