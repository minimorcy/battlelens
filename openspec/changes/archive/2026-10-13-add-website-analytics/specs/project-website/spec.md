## MODIFIED Requirements

### Requirement: Sin recursos externos
La web MUST NOT cargar scripts, hojas de estilo, fuentes ni imágenes de terceros: todo se sirve desde el propio sitio. La única excepción permitida es la analítica de Umami del propio usuario (spec `website-analytics`), que solo se carga si está configurada en el despliegue. Los únicos enlaces externos son a GitHub, PokéAPI y la licencia.

#### Scenario: Recursos locales
- **WHEN** se analiza `site/index.html` en el repositorio
- **THEN** todos los `src` y `href` de recursos apuntan a archivos de `site/`, y cada uno existe

#### Scenario: Sin analítica configurada
- **WHEN** el contenedor arranca sin las variables de Umami
- **THEN** la página no incluye ningún script externo y la CSP sigue permitiendo solo `'self'`

## ADDED Requirements

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
