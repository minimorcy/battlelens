# BattleLens

La constitución del proyecto está en `openspec/config.yaml` (contexto y reglas de OpenSpec). Resumen de lo que se aplica también fuera de OpenSpec:

## Guía de uso siempre al día

Cualquier cambio que altere algo que la guía de uso (`site/guide.html`) explica o muestra se entrega con la guía actualizada:

- **Qué cuenta:** menús de la bandeja, ventana de Ajustes, asistente de presets, calibración, la ficha y sus secciones, modos, atajos, modo stream, textos de la interfaz, valores por defecto, requisitos, instalación y limitaciones.
- **Texto:** actualiza los dos bloques de idioma de `site/guide.html` (`data-lang="es"` y `data-lang="en"`), que deben tener la misma estructura. Los nombres de botones y menús tienen que coincidir con los de la app (catálogo inglés en `src/battlelens/i18n/`).
- **Capturas:** regenéralas con `uv run python tools/make_guide_screenshots.py`. Si hay una pantalla u opción nueva que el usuario deba conocer, añade su captura al script y a la guía.
- **Comprobación:** `uv run pytest tests/test_site.py`.

Si el cambio es visible para el usuario, actualiza también `README.md`, `README.es.md` y `CHANGELOG.md` (en los dos idiomas).
