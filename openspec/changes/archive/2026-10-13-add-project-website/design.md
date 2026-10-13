## Context

El usuario tiene una instancia de Coolify con el dominio `minim-labs.app` y quiere publicar ahí la web. El repositorio es público (`minimorcy/battlelens`). Las capturas no pueden usar material de los juegos.

## Goals / Non-Goals

**Goals:** una página clara y rápida, bilingüe, sin dependencias externas, fácil de desplegar y de actualizar.

**Non-Goals:** blog, documentación completa (sigue en el README), analíticas, formularios o backend.

## Decisions

### D1. HTML, CSS y JS sin framework
Una sola página (`index.html`) con su hoja de estilos (`styles.css`) y un JS mínimo para el cambio de idioma (`app.js`). No hay paso de compilación y carga al instante. Se separan en tres archivos, en vez de incrustarlos, para que la CSP de nginx pueda ser estricta (`'self'`, sin `'unsafe-inline'`). Los textos van en atributos `data-en` y `data-es` de cada elemento traducible, lo que facilita comprobar la paridad con un test.
*Alternativa descartada:* un generador estático (Astro, Hugo). Es demasiado para una sola página.

### D2. Estilo coherente con la app
Se usa la paleta de la ficha (fondo oscuro, acento amarillo `#ffcb05`, colores de los tipos) y el icono del proyecto, con fuente del sistema (sin Google Fonts, por D4). Las capturas son la propia ficha, así que la web «se parece» al programa.

### D3. Capturas generadas desde la interfaz real
`tools/make_site_screenshots.py` crea las fichas con `Overlay` y `QT_SCALE_FACTOR=2` (nitidez en pantallas HiDPI) y las guarda en `site/assets/`. Se incluyen en el repositorio para que el despliegue no dependa de Qt.

### D4. Sin recursos externos
Ni fuentes, ni CDN, ni analíticas: es más rápido, no hace falta aviso de cookies y es coherente con la privacidad de la app. Un test lo comprueba.

### D5. Coolify con Dockerfile (nginx)
`site/Dockerfile` usa `nginx:1.27-alpine`, copia el sitio y un `nginx.conf` con gzip, `Cache-Control` largo para `assets/` y corto para `index.html`, cabeceras (`X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`, una CSP restrictiva sin recursos externos) y `/health`. En Coolify: recurso «Public Repository» → *Build Pack: Dockerfile* → *Base Directory: `/site`* → puerto 80 → dominio `https://battlelens.minim-labs.app`. Coolify gestiona el certificado (Let's Encrypt) con su proxy. El despliegue automático se activa con la GitHub App de Coolify o el webhook, limitado a la ruta `site/**`.
*Alternativa:* el *build pack* «Static» de Coolify. Es válido, pero el Dockerfile fija la configuración de nginx (cabeceras, `/health`) y se puede probar en local.

### D6. Enlaces que no se rompen
La descarga apunta a `releases/latest`: siempre lleva a la última versión sin tocar la web. Hasta que exista la primera Release, GitHub muestra la página de Releases vacía. Es aceptable y está documentado.

## Risks / Trade-offs

- [DNS del subdominio] → Lo crea el usuario (registro A o CNAME hacia el servidor de Coolify, o comodín `*.minim-labs.app`). La guía lo explica.
- [La web y la app pueden desalinearse] → Las capturas se regeneran con un comando y la guía de publicación lo incluye como paso.

## Migration Plan

No aplica.

## Open Questions

- El subdominio final lo decide el usuario. Por defecto, `battlelens.minim-labs.app`.
