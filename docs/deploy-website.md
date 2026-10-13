# Desplegar la web con Coolify

La web es estática (`site/`) y se sirve con nginx desde `site/Dockerfile`. Estos pasos la publican en **`https://battlelens.minim-labs.app`** y la actualizan sola con cada push que toque `site/`.

## 1. DNS

En el proveedor DNS de `minim-labs.app`, crea un registro que apunte al servidor de Coolify:

| Tipo | Nombre | Valor |
|---|---|---|
| `A` | `battlelens` | IP pública del servidor de Coolify |

Si ya tienes un comodín `*.minim-labs.app` apuntando a ese servidor, no hace falta nada más.

## 2. Crear el recurso en Coolify

1. **Projects** → tu proyecto (o uno nuevo, p. ej. `minim-labs`) → **+ New** → **Public Repository**.
2. **Repository URL:** `https://github.com/minimorcy/battlelens` · **Branch:** `main`.
3. **Build Pack:** `Dockerfile`.
4. **Base Directory:** `/site` · **Dockerfile Location:** `/Dockerfile` (relativo al directorio base).
5. **Ports Exposes:** `80`.
6. Guarda.

## 3. Dominio y certificado

En **Configuration → General → Domains** pon:

```
https://battlelens.minim-labs.app
```

Coolify configura su proxy (Traefik/Caddy) y pide el certificado de Let's Encrypt al desplegar. El DNS del paso 1 tiene que resolver ya.

## 4. Comprobación de salud (opcional, recomendado)

En **Configuration → Health Checks**: activado, ruta `/health`, puerto `80`. La imagen también trae su propio `HEALTHCHECK`.

## 5. Despliegue automático

Para que cada cambio de la web se publique solo:

1. En **Configuration → General → Watch Paths** pon `site/**`: así, los commits que no tocan la web no la vuelven a desplegar.
2. Elige una de estas dos opciones:
   - **Webhook** (repositorio público): en Coolify, **Configuration → Webhooks** → copia la URL de *GitHub* y define un *secret*. En GitHub: **Settings → Webhooks → Add webhook**, con *Payload URL* = esa URL, *Content type* = `application/json`, *Secret* = el mismo y el evento *Just the push event*.
   - **GitHub App** de Coolify: si ya la tienes conectada a tu cuenta, crea el recurso como *Private Repository (with GitHub App)* en lugar de *Public Repository*; el despliegue automático viene activado.

## 6. Primer despliegue

Pulsa **Deploy**. Cuando termine:

- `https://battlelens.minim-labs.app` muestra la web (en español si tu navegador está en español; el botón **EN/ES** cambia el idioma).
- `https://battlelens.minim-labs.app/health` responde `ok`.

## Actualizar la web

- **Textos o diseño:** edita `site/index.html` o `site/styles.css`, haz commit y push.
- **Capturas** (cuando cambie la ficha de la app): `uv run python tools/make_site_screenshots.py`, comprueba las imágenes de `site/assets/` y súbelas.
- El botón **Descargar** apunta siempre a la última Release (`releases/latest`), así que publicar una versión nueva no requiere tocar la web. Hasta la primera Release, ese enlace muestra la página de Releases vacía.

## ¿Bajo una ruta en vez de un subdominio?

Si prefieres `https://minim-labs.app/battlelens`, la web funciona igual porque usa rutas relativas. Pero hay que configurar el proxy de Coolify para que quite el prefijo `/battlelens` (en Traefik, un *middleware* `stripprefix`). El subdominio es más sencillo y no interfiere con lo que ya sirva `minim-labs.app`.
