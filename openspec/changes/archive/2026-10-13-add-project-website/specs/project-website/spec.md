## ADDED Requirements

### Requirement: Contenido de la web
La web SHALL ser una única página estática (`site/index.html`, con `styles.css` y `app.js`) con: nombre, icono y lema del proyecto; botón de descarga que apunta a `https://github.com/minimorcy/battlelens/releases/latest`; enlace al repositorio; capturas de la ficha en modo Normal, modo Competitivo y combate doble; explicación de cómo funciona en 3 pasos (elegir ventana, calibrar, jugar); lista de características; requisitos (Windows 10/11 de 64 bits, OCR de Windows); y pie con licencia, atribución a PokéAPI y el aviso de proyecto no oficial.

#### Scenario: Descargar desde la web
- **WHEN** un visitante pulsa «Download for Windows»
- **THEN** llega a la página de la última Release de GitHub

#### Scenario: Aviso legal visible
- **WHEN** un visitante llega al final de la página
- **THEN** ve que BattleLens es un proyecto de fans no oficial, no afiliado a Nintendo, The Pokémon Company, Creatures Inc. ni GAME FREAK inc.

### Requirement: Idiomas
La web SHALL estar disponible en inglés y en español, con el mismo contenido en ambos. El idioma inicial MUST ser español si el navegador está en español e inglés en otro caso. Un selector permite cambiarlo, y la elección se recuerda en el navegador si este lo permite.

#### Scenario: Navegador en español
- **WHEN** un visitante con el navegador en `es-ES` abre la web por primera vez
- **THEN** la ve en español

#### Scenario: Paridad de textos
- **WHEN** se comprueba la página
- **THEN** cada texto traducible tiene versión en inglés y en español

### Requirement: Sin recursos externos
La web MUST NOT cargar scripts, hojas de estilo, fuentes, imágenes ni analíticas de terceros: todo se sirve desde el propio sitio. Los únicos enlaces externos son a GitHub, PokéAPI y la licencia.

#### Scenario: Recursos locales
- **WHEN** se analiza `site/index.html`
- **THEN** todos los `src` y `href` de recursos apuntan a archivos de `site/`, y cada uno existe

### Requirement: Diseño adaptable y accesible
La web SHALL verse correctamente desde 320 px de ancho hasta escritorio, sin desplazamiento horizontal, con textos alternativos en todas las imágenes y contraste suficiente sobre el tema oscuro de la app.

#### Scenario: Móvil
- **WHEN** se abre en una pantalla de 360 px de ancho
- **THEN** las secciones se apilan en una columna y las capturas caben en el ancho

### Requirement: Capturas reproducibles
El proyecto SHALL incluir `tools/make_site_screenshots.py`, que genera las capturas de `site/assets/` a doble resolución a partir de la interfaz real de BattleLens. MUST NOT incluir capturas ni recursos gráficos de los juegos.

#### Scenario: Regenerar capturas
- **WHEN** se ejecuta `uv run python tools/make_site_screenshots.py`
- **THEN** se generan `card-normal.png`, `card-competitive.png` y `card-double.png` en `site/assets/`

### Requirement: Despliegue con Coolify
El directorio `site/` SHALL incluir un `Dockerfile` que sirva la web con nginx en el puerto 80, con compresión, caché de los recursos estáticos, cabeceras de seguridad básicas y una comprobación de salud. `docs/deploy-website.md` MUST explicar cómo crear el recurso en Coolify desde el repositorio público (directorio base `/site`), asignar el dominio dentro de `minim-labs.app` y activar el despliegue automático.

#### Scenario: Imagen local
- **WHEN** se construye la imagen con `docker build site` y se arranca
- **THEN** `GET /` devuelve la página con código 200 y `GET /health` devuelve 200
