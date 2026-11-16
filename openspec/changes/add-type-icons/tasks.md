## 1. Descarga y caché

- [x] 1.1 `core/remote_images.py`: `fetch_png` (tiempo de espera, tamaño máximo, firma PNG, escritura atómica) con tests usando una función de descarga falsa
- [x] 1.2 `TypeIcons`: `complete()`, `ensure()` en segundo plano con aviso por señal Qt, fallos recordados en la sesión y `pixmap()` con caché por tamaño; tests de caché completa, fallo y respuesta no válida
- [ ] 1.3 Actualizar D2 de `openspec/changes/add-pokemon-sprites/design.md` para que reutilice `fetch_png`

## 2. Opción

- [x] 2.1 `overlay.type_icons = false` en `core/config.py` (plantilla de `config.toml` y lectura)
- [x] 2.2 Casilla en Ajustes › Ficha con su texto en `i18n` (es/en); al guardar, lanzar `ensure()` o volver a las etiquetas y redibujar la ficha
- [x] 2.3 `app.py`: crear `TypeIcons` en la carpeta de datos, lanzar `ensure()` al arrancar si la opción está activa y redibujar la última ficha cuando llegan

## 3. Ficha

- [x] 3.1 `_pill()` con icono, tooltip y nombre accesible cuando están disponibles (22 px, 28 px en la cabecera)
- [x] 3.2 Revisar con capturas las fichas Normal, Competitiva, doble y con formas, y resolver la pregunta abierta de la cabecera
- [x] 3.3 Tests: con iconos, cada sección muestra pixmaps con el nombre accesible correcto; sin iconos completos, todo sigue con etiquetas

## 4. Tabla de tipos y stream

- [x] 4.1 Cabeceras de `TypeChartWindow` con iconos y tooltip
- [x] 4.2 `payload.py` con `icon` por tipo, ruta `/type-icon/<id>.png` validada en `server.py` y `<img alt>` en `card.js`
- [x] 4.3 Tests del servidor: icono en caché (200), id no válido o ausente (404), sin rutas fuera de `type-icons/`

## 5. Guía de uso y documentación

- [x] 5.1 Guía de uso: opción nueva en Ajustes › Ficha y mención en la ficha y en la tabla de tipos (`site/guide.html`, es/en); captura nueva de la ficha con iconos añadida a `tools/make_guide_screenshots.py` (con iconos de prueba generados en el script, sin descargar) y capturas regeneradas con `uv run python tools/make_guide_screenshots.py`; `uv run pytest tests/test_site.py`
- [x] 5.2 README.md y README.es.md: opción nueva y aviso del origen y la propiedad de los iconos
- [x] 5.3 CHANGELOG.md en los dos idiomas
