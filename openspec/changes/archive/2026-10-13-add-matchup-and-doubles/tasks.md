## 1. Dominio

- [x] 1.1 `core/profiles.py`: `rival2_region` y `own_region` opcionales, `regions()` y `with_regions()`, con compatibilidad JSON
- [x] 1.2 `core/matchup.py`: `matchup()` y veredicto (D5)
- [x] 1.3 `core/detection.py`: clave de combate genérica (D4)
- [x] 1.4 Tests: perfiles con y sin regiones opcionales, escenarios de `type-matchup` y clave de combate (cambia tu Pokémon, sin rival = no reconocido)

## 2. Reconocimiento

- [x] 2.1 `pipeline.py`: lectura de todas las regiones desde una captura, huella combinada y `rival2`/`own` en el resultado (D2-D3)
- [x] 2.2 Tests del pipeline con OCR simulado: tres regiones, apodo no reconocido y perfil de una sola región sin cambios

## 3. Interfaz

- [x] 3.1 `ui/overlay.py`: `show_battle` con varias tarjetas y apartado «Contra tu X» (D6)
- [x] 3.2 `ui/tray.py`: submenú «Regiones del perfil» con las opciones según el perfil activo (D7)
- [x] 3.3 `app.py`: calibrar y quitar regiones; reconocimiento manual y automático con varias regiones; mostrar la batalla
- [x] 3.4 Tests de UI y de controlador: doble con dos tarjetas, comparativa visible, submenú de regiones y detección automática con cambio de tu Pokémon

## 4. Cierre

- [x] 4.1 README, CHANGELOG y `docs/manual-validation.md` (doble y comparativa en un juego real); todos los tests y `openspec validate --all --strict`
