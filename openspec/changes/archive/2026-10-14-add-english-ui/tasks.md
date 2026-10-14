## 1. Base

- [x] 1.1 `i18n/`: `_`, `N_`, `set_language`, `get_language`, `resolve_language` y unión de catálogos (D1-D3)
- [x] 1.2 `tests/test_i18n.py`: cobertura con `ast`, marcadores y entradas sin usar (D4); `resolve_language`
- [x] 1.3 `core/config.py`: `[interface] language` con validación (D6)

## 2. Textos

- [x] 2.1 App y errores: `app.py`, `platform/*` (mensajes que ve el usuario), `core/profiles.py`, `core/config.py` (errores de validación) → `i18n/en_app.py`
- [x] 2.2 Menús y diálogos: `ui/tray.py`, `ui/settings.py`, `ui/calibrator.py`, `ui/about.py` → `i18n/en_menus.py`
- [x] 2.3 Ficha: `ui/overlay.py`, `ui/theme.py`, `stream/payload.py`, `stream/static/card.js` (D5), `core/competitive.py`, `core/abilities.py`, `core/card_text.py`, `core/matchup.py` y la dificultad de captura → `i18n/en_card.py`

## 3. Integración

- [x] 3.1 `app.py` (`main` y `apply_config`) y `ui/settings.py`: idioma de la interfaz, cambio en caliente y aviso (D6)
- [x] 3.2 Tests: escenarios de la spec (auto con en/es/fr, a mano, datos en español con interfaz en inglés, cambio en caliente) y comprobación de que no quedan palabras españolas en la bandeja, en Ajustes ni en la ficha en inglés

## 4. Cierre

- [x] 4.1 README (en y es: quitar «la interfaz está en español» y documentar `interface.language`), CHANGELOG, todos los tests y `openspec validate --strict`
