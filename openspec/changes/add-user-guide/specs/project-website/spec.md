## MODIFIED Requirements

### Requirement: Contenido de la web
La web SHALL tener dos páginas estáticas que comparten `styles.css` y `app.js`. La portada (`site/index.html`) SHALL incluir: nombre, icono y lema del proyecto; botón de descarga que apunta a `https://github.com/minimorcy/battlelens/releases/latest`; enlace al repositorio; capturas de la ficha en modo Normal, modo Competitivo y combate doble; explicación de cómo funciona en 3 pasos (elegir ventana, calibrar, jugar); lista de características; requisitos (Windows 10/11 de 64 bits, OCR de Windows); enlace a la guía; y pie con licencia, atribución a PokéAPI y el aviso de proyecto no oficial. La guía de uso (`site/guide.html`) SHALL explicar paso a paso la instalación, el menú de la bandeja, la configuración con un preset y a mano, la ficha y sus modos, tu Pokémon y los combates dobles, las formas, las secciones de la ficha, los ajustes, el modo stream, la resolución de problemas, las limitaciones y la desinstalación, con capturas de la app y el mismo pie.

#### Scenario: Descargar desde la web
- **WHEN** un visitante pulsa «Download for Windows»
- **THEN** llega a la página de la última Release de GitHub

#### Scenario: Aviso legal visible
- **WHEN** un visitante llega al final de cualquiera de las dos páginas
- **THEN** ve que BattleLens es un proyecto de fans no oficial, no afiliado a Nintendo, The Pokémon Company, Creatures Inc. ni GAME FREAK inc.

#### Scenario: Leer la guía
- **WHEN** un visitante pulsa «Read the guide» en la portada
- **THEN** llega a `guide.html` en la misma pestaña y en el mismo idioma

### Requirement: Idiomas
La web SHALL estar disponible en inglés y en español, con el mismo contenido en ambos. El idioma inicial MUST ser español si el navegador está en español e inglés en otro caso. Un selector permite cambiarlo, y la elección se recuerda en el navegador si este lo permite y se aplica a las dos páginas. En la guía, cada idioma es un bloque completo con su índice y sus capturas, y solo se muestra el del idioma activo (sin JavaScript, el inglés).

#### Scenario: Navegador en español
- **WHEN** un visitante con el navegador en `es-ES` abre la web por primera vez
- **THEN** la ve en español

#### Scenario: Paridad de textos
- **WHEN** se comprueba la página
- **THEN** cada texto traducible tiene versión en inglés y en español

#### Scenario: Mismo contenido en la guía
- **WHEN** se comparan los dos bloques de la guía
- **THEN** tienen los mismos apartados, capturas (en su idioma), tablas y preguntas, y cada enlace del índice lleva a un apartado de su mismo idioma

### Requirement: Capturas reproducibles
El proyecto SHALL incluir `tools/make_site_screenshots.py`, que genera las capturas de `site/assets/` a doble resolución a partir de la interfaz real de BattleLens, y `tools/make_guide_screenshots.py`, que genera las de la guía en `site/assets/guide/es/` y `site/assets/guide/en/` (bandeja, Ajustes, asistente de presets, calibración y fichas) con perfiles de ejemplo y actualiza sus medidas en `guide.html`. La única imagen de un juego permitida es la captura de una partida real (`site/assets/gameplay.jpg`), que MUST mostrar solo la imagen del juego (sin la interfaz del emulador) e ir acompañada del crédito del juego en ambos idiomas; las capturas de la guía que la usan llevan ese crédito en el pie.

#### Scenario: Regenerar capturas
- **WHEN** se ejecuta `uv run python tools/make_site_screenshots.py`
- **THEN** se generan `card-normal.png`, `card-competitive.png` y `card-double.png` en `site/assets/`

#### Scenario: Regenerar capturas de la guía
- **WHEN** se ejecuta `uv run python tools/make_guide_screenshots.py`
- **THEN** se generan las capturas de la guía en los dos idiomas y cada `<img>` de `guide.html` tiene la mitad del tamaño en píxeles de su imagen

#### Scenario: Captura de partida
- **WHEN** se ejecuta `uv run python tools/make_gameplay_shot.py` con el emulador en un combate
- **THEN** se genera `site/assets/gameplay.jpg` con la imagen del juego recortada (sin barra de menús, barra de estado ni franjas negras del emulador) y la ficha real de BattleLens superpuesta, reconocida con su pipeline

#### Scenario: Crédito visible
- **WHEN** un visitante ve la captura de la partida
- **THEN** debajo aparece el crédito de Pokémon Espada a Nintendo, Creatures Inc. y GAME FREAK inc.

### Requirement: Analítica opcional con Umami
IF el contenedor arranca con `UMAMI_SCRIPT_URL` (URL HTTPS del `script.js` de Umami) y `UMAMI_WEBSITE_ID` (UUID del sitio en Umami), THEN el sistema SHALL insertar en cada página con el marcador (portada y guía) el script de Umami con `defer` y `data-website-id` (y `data-domains` si se define `UMAMI_DOMAINS`), y MUST ampliar la CSP solo al origen de esa URL (`script-src` y `connect-src`), una sola vez. Si alguna variable no tiene un formato válido, MUST NOT insertar nada y MUST registrar un aviso en el log del contenedor. La inserción MUST ser idempotente al reiniciar el contenedor.

#### Scenario: Umami configurado
- **WHEN** el contenedor arranca con `UMAMI_SCRIPT_URL=https://umami.minim-labs.app/script.js` y un `UMAMI_WEBSITE_ID` válido
- **THEN** la portada y la guía incluyen ese script y la CSP permite `https://umami.minim-labs.app` en `script-src` y `connect-src`, y nada más externo

#### Scenario: Valor no válido
- **WHEN** `UMAMI_SCRIPT_URL` no es HTTPS o `UMAMI_WEBSITE_ID` no es un UUID
- **THEN** no se inserta el script, la CSP no cambia y el log lo indica

#### Scenario: Reinicio
- **WHEN** el contenedor se reinicia sin recrearse
- **THEN** el script aparece una sola vez en cada página y el origen aparece una sola vez en cada directiva de la CSP
