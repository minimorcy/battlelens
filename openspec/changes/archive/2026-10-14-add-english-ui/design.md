## Context

Los textos de la interfaz están escritos directamente en español en `app.py`, `ui/*`, `stream/*` y algunos módulos de `core` (veredictos, dificultad de captura, notas de habilidades, perfil de estadísticas) y `platform` (errores que se muestran en la bandeja). La ficha ya separa el idioma de los datos Pokémon (`overlay.language`). `platform/ocr_setup.ui_language_tag()` ya obtiene el idioma de la interfaz de Windows.

## Goals / Non-Goals

**Goals:**
- Interfaz completa en inglés, sin perder la española, con cobertura comprobada por un test.
- El código sigue escrito en español (el idioma del proyecto), con los textos legibles en su sitio.

**Non-Goals:**
- Más idiomas de interfaz (el mecanismo lo permite y se añadirían como catálogos nuevos).
- Traducir los registros, la autocomprobación, los comentarios ni los artefactos de OpenSpec.
- Cambiar los menús ya abiertos sin reiniciar.

## Decisions

### D1. Texto español como clave (`i18n/`)
`_("Reconocer ahora")` devuelve el texto tal cual en español o su traducción del catálogo inglés. Con argumentos, `_("Perfil «{name}» activado.", name=...)` formatea después de traducir, así que las f-strings se convierten a este formato. `N_("…")` solo marca un texto (devuelve el mismo) para constantes de módulo, como `STAT_LABELS`, los veredictos o `ABILITY_NOTES`, que se traducen al mostrarse con `_(constante)`.
*Alternativa descartada:* claves abstractas (`tray.recognize`). Obligan a abrir otro archivo para leer qué dice cada mensaje, y añaden una tabla para el español.
*Alternativa descartada:* gettext con `.po`/`.mo`. Exige un paso de compilación y empaquetar más archivos para dos idiomas.

### D2. Catálogos por zona
`i18n/en_app.py` (app y errores de `core`/`platform`), `i18n/en_menus.py` (bandeja, Ajustes, calibración, Acerca de) e `i18n/en_card.py` (ficha, ficha del stream y textos de `core` que aparecen en ella). Cada uno define `EN: dict[str, str]`, y `i18n` los une. Así se reparte el trabajo y se revisa cada zona por separado.

### D3. Idioma actual
`i18n.set_language("es" | "en")` y `get_language()` guardan un valor de módulo, que se fija en `main()` antes de crear ninguna ventana. `resolve_language(setting, windows_tag)` aplica la regla de `auto`: español si `windows_tag` empieza por `es` y, si no, inglés.

### D4. Cobertura
`tests/test_i18n.py` recorre con `ast` todos los `.py` de `src/battlelens` y recoge los literales de `_()` y `N_()`. Falla si alguno no está en el catálogo inglés o si los marcadores `{nombre}` no coinciden entre los dos idiomas. Además comprueba que no hay entradas del catálogo sin usar (avisa de textos huérfanos).

### D5. Página del stream
Los textos fijos de `card.js` («Tú», «Él», «Total») pasan al estado (`labels`), traducidos en `stream/payload.py`. El JS no lleva textos.

### D6. Configuración y Ajustes
`Config.interface_language = "auto"` (sección `[interface]`, valores `auto`/`es`/`en`). En Ajustes, «Idioma de la interfaz» va con las opciones «Automático (idioma de Windows)», «Español» e «English», y «Idioma de la ficha» pasa a «Idioma de los datos Pokémon». Al guardar con otro idioma, `apply_config` llama a `set_language`, vuelve a dibujar la ficha visible, vuelve a publicar la del stream y avisa de que los menús cambian al reiniciar.

### D7. Condiciones de evolución y decimales
Las etiquetas de las condiciones de evolución («Nv. 28», «Intercambio», «Amistad»…) son interfaz y siguen al idioma de la interfaz. Los nombres de los objetos («Piedra Trueno») son datos y siguen a `overlay.language`. `multiplier_text` usa coma decimal en español y punto en inglés (×1,5 / ×1.5).

## Risks / Trade-offs

- [Textos sin marcar] → El test detecta las traducciones que faltan, pero no los textos que no se marcaron. Se mitiga con una revisión manual de cada archivo y con un test de UI en inglés que busca palabras españolas en la bandeja, en Ajustes y en la ficha.
- [Cambios en tests existentes] → Los tests fijan el idioma español (valor por defecto del módulo) y siguen comparando con los textos en español.

## Migration Plan

`[interface] language = "auto"` por defecto: con Windows en español no cambia nada.

## Open Questions

Ninguna.
