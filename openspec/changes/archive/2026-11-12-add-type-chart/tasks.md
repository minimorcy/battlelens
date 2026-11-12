## 1. Configuración y atajo

- [x] 1.1 `hotkey_type_chart = "Ctrl+Alt+T"` en `Config`: plantilla TOML, carga (`hotkeys.type_chart`) y validación
- [x] 1.2 Registrar `type_chart` en `_parse_hotkeys`, `_on_hotkey` y la comparación de `apply_config`
- [x] 1.3 Campo «Tabla de tipos» en `HOTKEY_FIELDS` de Ajustes y en `collect`

## 2. Tabla

- [x] 2.1 `ui/type_chart.py`: `TypeChartWindow` pintada con `QPainter` (D1, D2), con resaltado (D3), arrastre, ✕ y exclusión de captura (D4)
- [x] 2.2 `Controller.toggle_type_chart()`: tabla de la generación del perfil activo, posición inicial junto al emulador (D5)
- [x] 2.3 Resaltado desde `_show_battle` y limpieza con la señal `Overlay.became_hidden` (cualquier forma de ocultar la ficha); `keep_on_top` en la vigilancia
- [x] 2.4 Opción «Tabla de tipos» en la bandeja con la pista del atajo
- [x] 2.5 Textos en `i18n` (catálogo inglés)
- [x] 2.6 Reescalado con tirador y `Ctrl` + rueda (D7); posición y escala en `state.json`, validadas y ajustadas a la pantalla (D5)

## 3. Tests

- [x] 3.1 Config: valor por defecto y carga de `hotkeys.type_chart`
- [x] 3.2 Tabla: tipos y celdas en Gen 1, Gen 3 y Gen 9; abreviaturas únicas en es/en
- [x] 3.3 Controller: alternar con el atajo, generación del perfil, resaltado con ficha visible y sin resaltado al ocultarla
- [x] 3.4 Reescalado (límites y `Ctrl` + rueda) y persistencia en `state.json`

## 4. Documentación

- [x] 4.1 Guía de uso: apartado «Tabla de tipos» en `site/guide.html` (es y en), fila de atajo y opción de bandeja; captura nueva en `tools/make_guide_screenshots.py` y regenerar con `uv run python tools/make_guide_screenshots.py`
- [x] 4.2 README.md, README.es.md y CHANGELOG.md (los dos idiomas); sección en la portada (`site/index.html`) con la captura de la tabla
- [x] 4.3 `uv run pytest` en verde
