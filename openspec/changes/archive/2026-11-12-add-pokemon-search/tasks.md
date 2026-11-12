## 1. Configuración y atajo

- [x] 1.1 `hotkey_search = "Ctrl+Alt+B"` en `Config`: plantilla TOML, carga (`hotkeys.search`) y validación
- [x] 1.2 Registrar `search` en `_parse_hotkeys`, `_on_hotkey` y la comparación de `apply_config`
- [x] 1.3 Campo «Buscar Pokémon» en `HOTKEY_FIELDS` de Ajustes y en `_collect`

## 2. Buscador

- [x] 2.1 `ui/search.py`: `SearchDialog` con `QLineEdit` y `QCompleter` (MatchContains, insensible a mayúsculas, siempre encima). Resuelve con un emparejador inyectado y avisa si no encuentra la especie
- [x] 2.2 `Controller.search_pokemon()`: abre el diálogo con `_modal_open` y muestra la ficha con `_show_battle((sid, None, None), juego del perfil, rect, searched=True)`
- [x] 2.3 `_show_battle` guarda `searched` y no publica en el stream; `_redraw_last_battle` y `cycle_form` lo conservan
- [x] 2.4 Opción «Buscar Pokémon…» en la bandeja con la pista del atajo
- [x] 2.5 Textos en `i18n` (catálogo inglés)
- [x] 2.6 Tipos en píldoras a la derecha de cada sugerencia (delegado de la lista)
- [x] 2.7 Una sugerencia por forma disponible en el juego (`Pokedex.search_entries`); elegirla abre la ficha con esa forma
- [x] 2.8 Un solo buscador a la vez: el atajo trae delante el abierto

## 3. Tests

- [x] 3.1 Config: valor por defecto, carga y guardado de `hotkeys.search`
- [x] 3.2 Diálogo: sugerencias, resolución sin tilde y aviso sin coincidencia
- [x] 3.3 Controller: la ficha buscada se muestra con el juego del perfil y no se publica en el stream

## 4. Documentación

- [x] 4.1 Guía de uso: actualizar `site/guide.html` en español e inglés (apartado «Buscar un Pokémon», atajos y bandeja), añadir la captura del buscador a `tools/make_guide_screenshots.py` y regenerar las capturas con `uv run python tools/make_guide_screenshots.py`
- [x] 4.2 README.md, README.es.md y CHANGELOG.md (los dos idiomas)
- [x] 4.3 `uv run pytest` en verde
