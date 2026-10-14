## 1. Datos y localización

- [x] 1.1 `vision/viewport.py`: `find_viewport` con bandas, ajuste a la proporción y DS (D2); tests sintéticos de los escenarios
- [x] 1.2 `core/presets.py`: presets medidos con las capturas de referencia, `preset_for` y `to_profile_regions` (D1); tests
- [x] 1.3 `tools/validate_presets.py` (D5) y pasada sobre `capturas-presets/` para ajustar las regiones

## 2. Asistente

- [x] 2.1 `ui/preset_wizard.py`: selector de juego, dibujo de recuadros, lecturas, ajustar la imagen del juego y calibrar a mano (D3); textos en `i18n`
- [x] 2.2 `app.py` y `ui/tray.py`: «Nuevo perfil con un preset…», creación del perfil y aviso de primer arranque (D4)
- [x] 2.3 Tests de UI y de controlador: preset aceptado, ajuste del viewport, juego sin preset y aviso sin perfiles

## 3. Cierre

- [x] 3.1 README (en y es: uso), CHANGELOG, `docs/manual-validation.md` (un emulador por plataforma), todos los tests y `openspec validate --strict`
