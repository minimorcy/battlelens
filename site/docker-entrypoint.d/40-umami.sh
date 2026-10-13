#!/bin/sh
# Analítica opcional con Umami (spec project-website, «Analítica opcional con Umami").
# La imagen oficial de nginx ejecuta los scripts de /docker-entrypoint.d/ antes de arrancar.
#
# Variables (en Coolify → Environment Variables):
#   UMAMI_SCRIPT_URL  URL HTTPS del script de tu Umami, p. ej. https://umami.minim-labs.app/script.js
#   UMAMI_WEBSITE_ID  UUID del sitio creado en Umami
#   UMAMI_DOMAINS     (opcional) dominios que cuentan, p. ej. battlelens.minim-labs.app
# Sin UMAMI_SCRIPT_URL y UMAMI_WEBSITE_ID no hace nada: la web no carga nada externo.
set -eu

HTML="${UMAMI_HTML_PATH:-/usr/share/nginx/html/index.html}"
HEADERS="${UMAMI_HEADERS_PATH:-/etc/nginx/snippets/security-headers.conf}"
MARKER="<!-- umami -->"
TAG="40-umami"

log() { echo "$TAG: $*"; }

url="${UMAMI_SCRIPT_URL:-}"
id="${UMAMI_WEBSITE_ID:-}"
domains="${UMAMI_DOMAINS:-}"

if [ -z "$url" ] && [ -z "$id" ]; then
    log "Umami no configurado; la web no carga analítica"
    exit 0
fi
if [ -z "$url" ] || [ -z "$id" ]; then
    log "AVISO: hacen falta UMAMI_SCRIPT_URL y UMAMI_WEBSITE_ID; se omite la analítica"
    exit 0
fi
if ! grep -q "$MARKER" "$HTML"; then
    log "el script de Umami ya estaba insertado (reinicio); nada que hacer"
    exit 0
fi

# Validación estricta: nada de comillas, espacios ni caracteres que rompan el HTML o sed.
if ! printf '%s' "$url" | grep -Eq '^https://[A-Za-z0-9.-]+(:[0-9]+)?/[A-Za-z0-9._/-]*$'; then
    log "AVISO: UMAMI_SCRIPT_URL no es una URL HTTPS válida; se omite la analítica"
    exit 0
fi
if ! printf '%s' "$id" | grep -Eq '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'; then
    log "AVISO: UMAMI_WEBSITE_ID no es un UUID; se omite la analítica"
    exit 0
fi
domains_attr=""
if [ -n "$domains" ]; then
    if ! printf '%s' "$domains" | grep -Eq '^[A-Za-z0-9.,-]+$'; then
        log "AVISO: UMAMI_DOMAINS no es válido; se omite la analítica"
        exit 0
    fi
    domains_attr=" data-domains=\"$domains\""
fi

origin=$(printf '%s' "$url" | sed -E 's#^(https://[^/]+).*#\1#')
script="<script defer src=\"$url\" data-website-id=\"$id\"$domains_attr></script>"

sed -i "s#$MARKER#$script#" "$HTML"
sed -i "s#script-src 'self'#script-src 'self' $origin#; s#connect-src 'none'#connect-src $origin#" "$HEADERS"
log "Umami activado ($origin)"
