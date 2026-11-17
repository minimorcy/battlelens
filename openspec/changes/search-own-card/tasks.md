## 1. Campo de búsqueda reutilizable

- [x] 1.1 Extraer de `SearchDialog` un `SearchField(QWidget)` con campo, completer, aviso y resolución; señal `chosen(int, object)` y `set_entries(entries)`; `Esc` vacía el campo
- [x] 1.2 `SearchDialog` envuelve `SearchField` (guarda `choice` y acepta en `chosen`; `Esc` cierra)
- [x] 1.3 Adaptar `tests/test_search.py` y añadir un test de `SearchField` (elegir sugerencia, texto aproximado, sin coincidencia, `set_entries`)

## 2. Ficha buscada independiente

- [x] 2.1 `State.search_card_pos` opcional en `core/config.py`, con lectura tolerante como `overlay_pos`
- [x] 2.2 Crear `App.search_card` (segunda `Overlay`, sin temporizador, `collapsed` compartido) y conectar `moved`, `form_step` y `dismissed`
- [x] 2.3 Propagar a las dos fichas `language`, `mode`, `hidden`, `type_icons`, `sprites`, `sprite_arrived`, `keep_on_top` y `expand_all`
- [x] 2.4 `_last_search` + `_show_search()`; `search_pokemon` deja de usar `_show_battle`; quitar `_searched`, el parámetro `searched` y la pausa `_modal_open` del buscador
- [x] 2.5 Formas de la ficha buscada con sus flechas; `cycle_form` (atajo) solo para el rival; redibujar la búsqueda en `_redraw_last_battle`
- [x] 2.6 Posición por defecto de la ficha buscada en overlay que no solape a la del rival
- [x] 2.7 Tests en `tests/test_app.py`: buscar no toca la ficha del rival, la detección y el fin del combate no tocan la buscada, la búsqueda no va al stream, la detección no se pausa, flechas de forma independientes

## 3. Panel en tres columnas

- [x] 3.1 `PanelWindow` recibe `search_card` y un `SearchField`; añadir `_search_column` (campo + `_search_slot`) a la derecha y ancho fijo de ficha
- [x] 3.2 `dock`/`undock` reparentan y restauran también la ficha buscada (flags, cursor, exclusión de captura)
- [x] 3.3 Tamaño inicial `1440×760` y mínimo `760×400`
- [x] 3.4 En modo panel, el atajo y la bandeja traen el panel delante y enfocan el campo; tras buscar se vacía; las entradas se refrescan al cambiar de perfil o de idioma
- [x] 3.5 Tests en `tests/test_panel.py`: tres columnas, ficha buscada bajo el buscador, fin del combate conserva la buscada, `undock` devuelve las dos fichas a flotar

## 4. Guía de uso, README y CHANGELOG

- [x] 4.1 `site/guide.html` (ES y EN): apartado del buscador (ficha propia, detección sin pausa, cerrar con ✕, flechas de forma) y del modo panel (tres columnas, buscador fijo, atajo)
- [x] 4.2 Actualizar `tools/make_guide_screenshots.py` para que la captura del panel muestre las tres columnas con una ficha buscada, y regenerar con `uv run python tools/make_guide_screenshots.py`
- [x] 4.3 `README.md`, `README.es.md` y `CHANGELOG.md` (los dos idiomas)
- [ ] 4.4 `uv run pytest` completo (incluido `tests/test_site.py`) y prueba manual en los dos modos
