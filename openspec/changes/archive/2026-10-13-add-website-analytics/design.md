## Context

La web se sirve con la imagen oficial de nginx, que ejecuta al arrancar los scripts de `/docker-entrypoint.d/*.sh`. La CSP vive en `security-headers.conf` y solo permite `'self'`.

## Goals / Non-Goals

**Goals:** activar Umami sin tocar el repositorio, sin romper la CSP y sin nada externo cuando no está configurado.

**Non-Goals:** banner de cookies (Umami no usa cookies), otras plataformas de analítica, eventos más allá de descarga y GitHub.

## Decisions

### D1. Inyección al arrancar el contenedor
`40-umami.sh` sustituye el marcador `<!-- umami -->` del `<head>` por el `<script defer src=… data-website-id=… [data-domains=…]>` y añade el origen a `script-src` y a `connect-src` de la CSP. Solo actúa si el marcador sigue presente, lo que lo hace idempotente en los reinicios. Las rutas se pueden cambiar con variables para poder probar el script fuera de Docker.
*Alternativa descartada:* poner el ID en el repositorio. Ataría el código abierto a una instancia concreta, y cualquier fork enviaría visitas a la analítica del usuario.

### D2. Validación estricta antes de tocar nada
URL: `^https://[A-Za-z0-9.-]+(:[0-9]+)?/[A-Za-z0-9._/-]*$`. ID: UUID. Dominios: `[A-Za-z0-9.,-]+`. Así no se puede inyectar HTML ni romper `sed`. Si algo no es válido, se registra un aviso y la web arranca sin analítica.

### D3. Eventos con atributos de Umami
`data-umami-event="download"` / `"github"` en los enlaces; `app.js` pone `data-umami-event-lang` con el idioma actual. Sin el script, los atributos no hacen nada.

### D4. Aviso en el pie solo si hay Umami
`app.js` muestra el aviso traducido si existe `script[data-website-id]`. Así el texto está en el HTML (y tiene sus traducciones) pero permanece oculto sin analítica.

## Risks / Trade-offs

- [Los bloqueadores de anuncios bloquean Umami] → Se acepta; las cifras serán aproximadas. Umami permite renombrar el script en el servidor si se quiere evitar.
- [Fines de línea CRLF en el `.sh` al clonar en Windows] → `.gitattributes` fuerza LF para `*.sh`. Coolify clona en Linux.

## Migration Plan

Sin variables, la web se comporta igual que antes. Para activar Umami, se añaden las variables en Coolify y se vuelve a desplegar.

## Open Questions

Ninguna.
