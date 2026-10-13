## 1. README

- [x] 1.1 Reescribir `README.md` en inglés y crear `README.es.md` con el contenido actual, con enlaces cruzados y a la web

## 2. Web

- [x] 2.1 `tools/make_site_screenshots.py` y capturas en `site/assets/` (más el icono)
- [x] 2.2 `site/index.html`: secciones, textos en/es, selector de idioma, diseño adaptable (D1-D2)
- [x] 2.3 Tests: paridad en/es, recursos locales existentes, sin recursos externos, enlace de descarga y aviso legal

## 3. Despliegue

- [x] 3.1 `site/Dockerfile`, `site/nginx.conf` y `site/.dockerignore` (D5)
- [x] 3.2 `docs/deploy-website.md`: guía de Coolify (recurso, dominio, DNS, despliegue automático)
- [x] 3.3 Comprobar la imagen en local si hay Docker disponible: **no hay Docker en el equipo**; la comprobación de `/` y `/health` pasa a `docs/manual-validation.md` y se hará en el primer despliegue de Coolify

## 4. Cierre

- [x] 4.1 CHANGELOG; todos los tests y `openspec validate --all --strict`
- [x] 4.2 Registrar en `docs/manual-validation.md` el despliegue en Coolify (DNS, recurso, `/` y `/health`, despliegue automático), que hace el usuario siguiendo `docs/deploy-website.md`
