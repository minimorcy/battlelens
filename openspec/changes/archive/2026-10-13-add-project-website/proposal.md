## Why

BattleLens ya es público en GitHub, pero un jugador que llega desde un enlace necesita ver en segundos qué hace y cómo descargarlo, y el README de GitHub está pensado para desarrolladores y escrito solo en español. Además, el proyecto debe poder entenderse fuera de España.

## What Changes

- **README en inglés** como principal (`README.md`) y la versión en español en `README.es.md`, enlazadas entre sí.
- **Web del proyecto** de una sola página en `site/`, con selector inglés/español: qué es, capturas de la ficha (modo Normal, modo Competitivo y combate doble), cómo funciona en 3 pasos, características, requisitos, botón de **descarga** que apunta a la última Release de GitHub y enlace al repositorio. Incluye el aviso de proyecto no oficial.
- **Capturas generadas** con un script a partir de la propia interfaz de BattleLens, sin imágenes de los juegos.
- **Despliegue con Coolify** en el dominio de `minim-labs.app` (subdominio recomendado: `battlelens.minim-labs.app`): `site/Dockerfile` con nginx y una guía de configuración. Cada push que toque `site/` despliega la web de nuevo.

## Capabilities

### New Capabilities
- `project-website`: contenido y comportamiento de la web, sus capturas y su despliegue.
- `project-readme`: README en inglés y en español.

### Modified Capabilities
<!-- Ninguna. -->

## Impact

- **Archivos nuevos:** `site/index.html`, `site/assets/*`, `site/Dockerfile`, `site/nginx.conf`, `site/.dockerignore`, `tools/make_site_screenshots.py`, `docs/deploy-website.md`, `README.es.md`; `README.md` reescrito en inglés.
- **Infraestructura externa:** un recurso nuevo en la instancia de Coolify del usuario y un registro DNS del subdominio (los hace el usuario siguiendo la guía).
- **Sin cambios en la aplicación.**
