## Why

Para saber si la web sirve (visitas, de dónde llegan, cuántos pulsan «Descargar») el usuario quiere usar su instancia de Umami: analítica autoalojada, sin cookies y sin datos personales. La spec vigente prohíbe cualquier analítica, así que hay que permitir esta excepción de forma explícita y controlada.

## What Changes

- **Analítica opcional con Umami**, configurada en el despliegue (variables de entorno de Coolify `UMAMI_SCRIPT_URL`, `UMAMI_WEBSITE_ID` y, opcionalmente, `UMAMI_DOMAINS`). El repositorio no contiene identificadores: sin variables, la web queda igual que ahora.
- Al arrancar, un script del contenedor inserta el `<script>` de Umami y amplía la CSP solo al origen de Umami. Valida los valores y es idempotente.
- **Eventos** en los botones de descarga y GitHub (`download`, `github`), con el idioma como propiedad.
- **Aviso** en el pie de la web cuando la analítica está activa.

## Capabilities

### New Capabilities
<!-- Ninguna: se amplía project-website. -->

### Modified Capabilities
- `project-website`: excepción de Umami en «Sin recursos externos», y nuevos requisitos de analítica opcional, eventos y aviso.

## Impact

- `site/index.html` (marcador para el script, atributos de evento, aviso), `site/app.js` (aviso y propiedad de idioma), nuevo `site/docker-entrypoint.d/40-umami.sh`, `site/Dockerfile`, `.gitattributes` (`*.sh` con LF), `docs/deploy-website.md`, tests.
- **Privacidad:** Umami no usa cookies ni guarda IPs; la página lo indica.
