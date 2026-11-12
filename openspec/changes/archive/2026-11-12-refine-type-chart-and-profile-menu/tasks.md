## 1. Bandeja

- [x] 1.1 Acción «Modificar o crear perfil…» con pista del atajo de calibrar y señal `calibrate_requested` → `Controller.calibrate` (D4)

## 2. Tabla de tipos

- [x] 2.1 `set_highlight(defending, attacking)`: filas propias en amarillo, cruces con borde y leyenda (D1–D3)
- [x] 2.2 `_show_battle` pasa los tipos de tu Pokémon; `became_hidden` limpia filas y columnas
- [x] 2.3 Textos en `i18n`

## 3. Tests

- [x] 3.1 Bandeja: la acción emite la señal y muestra la pista
- [x] 3.2 Tabla: filas propias, columnas del rival (también en dobles) y limpieza al ocultar la ficha

## 4. Documentación

- [x] 4.1 Guía de uso: bandeja (opción nueva) y tabla de tipos (filas y columnas resaltadas) en `site/guide.html` (es y en); regenerar capturas con `uv run python tools/make_guide_screenshots.py` (tabla con tu Pokémon resaltado)
- [x] 4.2 CHANGELOG.md (los dos idiomas), README y portada
- [x] 4.3 `uv run pytest` en verde
