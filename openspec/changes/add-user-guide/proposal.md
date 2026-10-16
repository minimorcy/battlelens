## Why

El botón «Leer la guía» de la web llevaba al README de GitHub: un texto largo, sin imágenes y pensado a la vez para jugadores y desarrolladores. Hace falta una guía de uso propia, con capturas de la app real, que explique paso a paso cómo instalar, configurar un juego y aprovechar la ficha, en español y en inglés.

## What Changes

- Nueva página `site/guide.html`: guía de uso bilingüe con índice lateral y 15 apartados (inicio rápido, instalación, bandeja, presets, calibración a mano, la ficha, modos, tu Pokémon y dobles, formas, ficha a medida, ajustes, OBS, problemas, limitaciones, actualizar y desinstalar).
- Cada idioma es un bloque completo (`<div class="guide" data-lang="…">`) y se muestra el del idioma elegido con el mismo selector de la portada.
- Nuevo `tools/make_guide_screenshots.py`: genera las capturas en `site/assets/guide/{es,en}/` a partir de la interfaz real (bandeja, páginas de Ajustes, asistente de presets, calibración y fichas), con perfiles de ejemplo, y actualiza sus medidas en la página. La imagen del juego del asistente y de la calibración sale de `gameplay.jpg`, quitando la ficha.
- La portada enlaza a la guía (navegación y «Leer la guía»); `Dockerfile`, `sitemap.xml` y la analítica de Umami incluyen la página nueva.

## Capabilities

### Modified Capabilities
- `project-website`: la web pasa a tener dos páginas (portada y guía) y la analítica se inserta en ambas.

## Impact

- Nuevos: `site/guide.html`, `site/assets/guide/`, `tools/make_guide_screenshots.py`.
- Cambios: `site/index.html`, `site/styles.css`, `site/Dockerfile`, `site/sitemap.xml`, `site/docker-entrypoint.d/40-umami.sh`, `tests/test_site.py`.
