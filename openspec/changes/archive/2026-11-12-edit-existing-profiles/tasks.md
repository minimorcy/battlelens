## 1. Atajo de calibrar

- [x] 1.1 `ask_calibration_target` en `ui/calibrator.py`: botones por región (✓ si ya está calibrada) y «Crear un perfil nuevo…» (opcional)
- [x] 1.2 `Controller.calibrate()` como acción del atajo: sin perfil → `calibrate_new`; con perfil → diálogo y `calibrate_region` o `calibrate_new` (D1)

## 2. Renombrar

- [x] 2.1 Campo Nombre en la tarjeta Perfil activo con `rename_requested` (D2)
- [x] 2.2 `Controller.rename_profile`: guarda con el mismo id, ignora vacío/igual y refresca lista, bandeja y Ajustes

## 3. Aplicar un preset

- [x] 3.1 Extraer `_preset_regions` de la creación con preset
- [x] 3.2 Botón «Aplicar un preset…» y `Controller.apply_preset_to_active` (D3), incluido «Calibrar a mano…» → diálogo de D1 sin perfil nuevo
- [x] 3.3 Textos en `i18n`

## 4. Tests

- [x] 4.1 Atajo: sin perfiles crea; con perfil recalibra la región elegida; «nuevo» crea
- [x] 4.2 Renombrar: mismo id y regiones; vacío no cambia nada
- [x] 4.3 Reaplicar preset: mismo id y nombre, regiones y juego del preset, 2.º rival conservado; sin perfil nuevo

## 5. Documentación

- [x] 5.1 Guía de uso: actualizar `site/guide.html` en español e inglés («Calibrar a mano» y Ajustes › Perfiles), añadir la captura del diálogo de recalibrar a `tools/make_guide_screenshots.py` y regenerar con `uv run python tools/make_guide_screenshots.py`
- [x] 5.2 README.md, README.es.md, CHANGELOG.md (los dos idiomas) y novedades de la portada
- [x] 5.3 `uv run pytest` en verde
