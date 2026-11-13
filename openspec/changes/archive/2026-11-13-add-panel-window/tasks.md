## 1. Configuración y estado

- [x] 1.1 `Config.overlay_display` (`[overlay] display`, `overlay`|`panel`), plantilla TOML y validación
- [x] 1.2 `AppState.panel_geometry` (`[x, y, w, h]` o `None`)

## 2. Ficha y tabla dentro del panel

- [x] 2.1 `Overlay`: si no es ventana, `_present`/`_fit_to_screen`/`_relayout`/arrastre/`keep_on_top` se comportan como en D2
- [x] 2.2 `TypeChartWindow`: si no es ventana, sin ✕, tirador, arrastre ni Ctrl+rueda; `present` = `show`
- [x] 2.3 `ui/panel.py`: `PanelWindow` (columna ficha + «Esperando combate…», tabla escalada, `dock`/`undock`, geometría)

## 3. Integración

- [x] 3.1 `app.py`: `_set_display`, `_load_type_chart`, panel al arrancar y al cambiar Ajustes, guardar geometría
- [x] 3.2 Ajustes › Ficha: «Mostrar la ficha en»
- [x] 3.3 Bandeja: «Mostrar el panel» (solo en modo Panel)
- [x] 3.4 Textos en el catálogo inglés de `i18n/`
- [x] 3.5 Tests: config, estado vacío, cambio en caliente, tabla escalada

## 4. Guía de uso y documentación

- [x] 4.1 Guía de uso: apartado «Modo panel (dos pantallas)», opción en Ajustes › Ficha y menú de la bandeja en `site/guide.html` (es y en); captura nueva del panel en `tools/make_guide_screenshots.py` y regenerar con `uv run python tools/make_guide_screenshots.py`
- [x] 4.2 README.md, README.es.md y CHANGELOG.md (es y en)
