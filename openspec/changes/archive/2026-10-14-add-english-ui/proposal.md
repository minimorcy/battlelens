## Why

Toda la interfaz (menús de la bandeja, avisos, diálogos, Ajustes, calibración y los títulos de la ficha) está en español. El README ya está en inglés y la ficha muestra los datos Pokémon en cinco idiomas, pero un streamer o jugador que no hable español no entiende los menús. Para repartir BattleLens a testers internacionales hace falta la interfaz en inglés.

## What Changes

- **Idioma de la interfaz** (`interface.language`): `auto` (por defecto), `es` o `en`. `auto` sigue al idioma de Windows: español si Windows está en español y, si no, inglés.
- **Todo el texto de la interfaz traducido:** bandeja, notificaciones, diálogos (calibración, perfiles, Ajustes, Acerca de, instalación del OCR, errores) y los textos de la ficha y de la ficha del stream (títulos de sección, captura y su dificultad, veredictos, velocidad, efectos de habilidades, perfil de estadísticas, etc.).
- **Idiomas independientes:** el idioma de la interfaz no cambia el de los datos Pokémon (`overlay.language`: nombres, tipos, movimientos y habilidades en es/en/fr/de/it). En Ajustes se llaman «Idioma de la interfaz» e «Idioma de los datos Pokémon».
- **Cambio en caliente:** la ficha y la del stream cambian de idioma al guardar Ajustes; los menús y diálogos, al reiniciar (se avisa).
- **Garantía de cobertura:** un test comprueba que todos los textos marcados para traducir tienen su versión en inglés.
- Los registros (`app.log`) y la autocomprobación siguen en español: no son interfaz.

## Capabilities

### New Capabilities
- `interface-language`: idioma de la interfaz, detección automática y cobertura de la traducción.

### Modified Capabilities
- `app-settings`: «Idioma de la interfaz» en Ajustes y renombrado de «Idioma de la ficha» a «Idioma de los datos Pokémon».

## Impact

- **Código:** nuevo `i18n/` (función `_()`, idioma actual y catálogos en inglés). Textos marcados con `_()` en `app.py`, `ui/*`, `stream/payload.py`, `stream/static/card.js` (los textos fijos pasan al estado), `core/competitive.py`, `core/abilities.py`, `core/card_text.py`, `core/matchup.py`, `core/pokedex.py` (dificultad de captura) y mensajes de error mostrados al usuario (`core/profiles.py`, `platform/*`).
- **Configuración:** nueva sección `[interface]`, con `auto` por defecto: los usuarios con Windows en español no notan ningún cambio.
- **Sin dependencias nuevas** (diccionarios en Python, sin gettext ni archivos `.mo`).
