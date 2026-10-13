# project-website Specification

## Purpose
Web pública del proyecto: contenido bilingüe, capturas generadas desde la app y despliegue con Coolify.
## Requirements
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
La web MUST NOT cargar scripts, hojas de estilo, fuentes ni imágenes de terceros: todo se sirve desde el propio sitio. La única excepción permitida es la analítica de Umami del propio usuario (spec `website-analytics`), que solo se carga si está configurada en el despliegue. Los únicos enlaces externos son a GitHub, PokéAPI y la licencia.

#### Scenario: Recursos locales
- **WHEN** se analiza `site/index.html` en el repositorio
- **THEN** todos los `src` y `href` de recursos apuntan a archivos de `site/`, y cada uno existe

#### Scenario: Sin analítica configurada
- **WHEN** el contenedor arranca sin las variables de Umami
- **THEN** la página no incluye ningún script externo y la CSP sigue permitiendo solo `'self'`

### Requirement: Diseño adaptable y accesible
La web SHALL verse correctamente desde 320 px de ancho hasta escritorio, sin desplazamiento horizontal, con textos alternativos en todas las imágenes y contraste suficiente sobre el tema oscuro de la app.

#### Scenario: Móvil
- **WHEN** se abre en una pantalla de 360 px de ancho
- **THEN** las secciones se apilan en una columna y las capturas caben en el ancho

### Requirement: Capturas reproducibles
El proyecto SHALL incluir `tools/make_site_screenshots.py`, que genera las capturas de `site/assets/` a doble resolución a partir de la interfaz real de BattleLens. La única imagen de un juego permitida es la captura de una partida real (`site/assets/gameplay.jpg`), que MUST mostrar solo la imagen del juego (sin la interfaz del emulador) e ir acompañada del crédito del juego en ambos idiomas.

#### Scenario: Regenerar capturas
- **WHEN** se ejecuta `uv run python tools/make_site_screenshots.py`
- **THEN** se generan `card-normal.png`, `card-competitive.png` y `card-double.png` en `site/assets/`

#### Scenario: Captura de partida
- **WHEN** se ejecuta `uv run python tools/make_gameplay_shot.py` con el emulador en un combate
- **THEN** se genera `site/assets/gameplay.jpg` con la imagen del juego recortada (sin barra de menús, barra de estado ni franjas negras del emulador) y la ficha real de BattleLens superpuesta, reconocida con su pipeline

#### Scenario: Crédito visible
- **WHEN** un visitante ve la captura de la partida
- **THEN** debajo aparece el crédito de Pokémon Espada a Nintendo, Creatures Inc. y GAME FREAK inc.

### Requirement: Despliegue con Coolify
El directorio `site/` SHALL incluir un `Dockerfile` que sirva la web con nginx en el puerto 80, con compresión, caché de los recursos estáticos, cabeceras de seguridad básicas y una comprobación de salud. `docs/deploy-website.md` MUST explicar cómo crear el recurso en Coolify desde el repositorio público (directorio base `/site`), asignar el dominio dentro de `minim-labs.app` y activar el despliegue automático.

#### Scenario: Imagen local
- **WHEN** se construye la imagen con `docker build site` y se arranca
- **THEN** `GET /` devuelve la página con código 200 y `GET /health` devuelve 200

### Requirement: Analítica opcional con Umami
IF el contenedor arranca con `UMAMI_SCRIPT_URL` (URL HTTPS del `script.js` de Umami) y `UMAMI_WEBSITE_ID` (UUID del sitio en Umami), THEN el sistema SHALL insertar en la página el script de Umami con `defer` y `data-website-id` (y `data-domains` si se define `UMAMI_DOMAINS`), y MUST ampliar la CSP solo al origen de esa URL (`script-src` y `connect-src`). Si alguna variable no tiene un formato válido, MUST NOT insertar nada y MUST registrar un aviso en el log del contenedor. La inserción MUST ser idempotente al reiniciar el contenedor.

#### Scenario: Umami configurado
- **WHEN** el contenedor arranca con `UMAMI_SCRIPT_URL=https://umami.minim-labs.app/script.js` y un `UMAMI_WEBSITE_ID` válido
- **THEN** la página incluye ese script y la CSP permite `https://umami.minim-labs.app` en `script-src` y `connect-src`, y nada más externo

#### Scenario: Valor no válido
- **WHEN** `UMAMI_SCRIPT_URL` no es HTTPS o `UMAMI_WEBSITE_ID` no es un UUID
- **THEN** no se inserta el script, la CSP no cambia y el log lo indica

#### Scenario: Reinicio
- **WHEN** el contenedor se reinicia sin recrearse
- **THEN** el script aparece una sola vez y el origen aparece una sola vez en la CSP

### Requirement: Eventos de descarga
Los botones de descarga y de GitHub SHALL llevar atributos de evento de Umami (`data-umami-event`), de modo que, si la analítica está activa, se registren los clics en «Descargar» y «GitHub» con el idioma de la página. Sin Umami, estos atributos no tienen ningún efecto.

#### Scenario: Clic en descargar
- **WHEN** con Umami activo un visitante pulsa «Download for Windows»
- **THEN** Umami registra el evento `download` con la propiedad del idioma

### Requirement: Aviso de analítica
IF la analítica está activa, THEN el pie de la web SHALL indicar, en el idioma de la página, que se usa analítica anónima sin cookies (Umami).

#### Scenario: Aviso visible
- **WHEN** Umami está configurado y un visitante llega al pie
- **THEN** lee «Anonymous, cookie-free analytics by Umami» (o su versión en español)

