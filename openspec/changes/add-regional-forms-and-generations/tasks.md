## 1. Dataset

- [x] 1.1 Ampliar `tools/build_dataset.py`: catálogo de juegos (D2 y D4), formas regionales con nombres, tipos, estadísticas y habilidades, `past_types`, `type_generation`, `type_efficacy_past` y `format: 2`
- [x] 1.2 Regenerar `pokedex.json` y comprobar a mano Zigzagoon de Galar, las tres razas de Tauros de Paldea, Clefairy (Normal hasta la Gen 5) y Magnemite (solo Eléctrico en la Gen 1)
- [x] 1.3 Tests del script con CSV mínimos (forma regional, tipo anterior, eficacia anterior y juego)

## 2. Dominio

- [x] 2.1 `core/pokedex.py`: modelos `Form`, `Game` y `SpeciesView`; `type_chart(generation)` cacheada; `defensive_matchups(types, generation)`; `view(species_id, game)` según D1-D3
- [x] 2.2 `core/games.py`: `detect_game(title, catalog)` con palabras completas, prefijo «Pokémon» para nombres cortos, preferencia por el más largo, alias de ROM y reducción de las DLC a su juego base
- [x] 2.3 Tests: todos los escenarios de `pokemon-data` y `game-catalog` (Zigzagoon en Espada y en Esmeralda, Clefairy en la Gen 5 y la actual, tabla de la Gen 1, Acero en la Gen 5, sin habilidades en la Gen 1, detecciones y falsos positivos)

## 3. Perfiles

- [x] 3.1 `core/profiles.py`: campo opcional `game`, compatible con los JSON antiguos; `with_game()`; `ProfileStore.find_by_game()`
- [x] 3.2 Tests: carga de un perfil antiguo, ida y vuelta con juego, búsqueda por juego y preferencia por el activo

## 4. Interfaz e integración

- [x] 4.1 `ui/overlay.py`: pintar `SpeciesView` (nombre con la forma, «Otras formas», habilidades opcionales)
- [x] 4.2 `ui/calibrator.py`: `ProfileDialog` con nombre y juego propuestos según el título
- [x] 4.3 `ui/tray.py`: submenú «Juego del perfil» con «Sin especificar» y los juegos por generación
- [x] 4.4 `app.py`: activación automática por juego al seleccionar ventana y antes de reconocer; vista según el juego del perfil activo; guardar el juego desde la bandeja
- [x] 4.5 Tests de UI y de controlador: ficha de forma regional, diálogo con propuesta, activación automática y cambio de juego desde la bandeja

## 5. Cierre

- [x] 5.1 README (limitaciones actualizadas) y CHANGELOG; ejecutar todos los tests y `openspec validate --all --strict`
- [ ] 5.2 (Usuario) Validación con un juego de GBA y otro de NDS, heredada de la tarea 9.2 del MVP: calibrar y reconocer unos 10 rivales con depuración activada
