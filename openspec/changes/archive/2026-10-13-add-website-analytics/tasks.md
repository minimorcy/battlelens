## 1. Web

- [x] 1.1 `site/index.html`: marcador `<!-- umami -->`, atributos `data-umami-event` en descarga y GitHub, aviso del pie (oculto)
- [x] 1.2 `site/app.js`: propiedad de idioma en los eventos y aviso visible solo con Umami

## 2. Contenedor

- [x] 2.1 `site/docker-entrypoint.d/40-umami.sh` (D1-D2) y `Dockerfile`; `.gitattributes` con LF para `*.sh`
- [x] 2.2 Tests ejecutando el script con `sh`: sin variables, configurado, valores no válidos e idempotencia

## 3. Cierre

- [x] 3.1 `docs/deploy-website.md` (crear el sitio en Umami y las variables en Coolify), CHANGELOG, tests y `openspec validate --all --strict`
- [x] 3.2 Registrar en `docs/manual-validation.md` la comprobación con Umami real (variables en Coolify, visita y evento `download`), que hace el usuario
