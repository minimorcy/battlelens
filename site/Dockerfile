# Web de BattleLens servida con nginx. En Coolify: Build Pack «Dockerfile», Base Directory «/site», puerto 80.
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY security-headers.conf /etc/nginx/snippets/security-headers.conf
COPY index.html guide.html styles.css app.js robots.txt sitemap.xml /usr/share/nginx/html/
COPY assets/ /usr/share/nginx/html/assets/
# Analítica opcional (Umami) configurada con variables de entorno; ver docs/deploy-website.md
COPY docker-entrypoint.d/40-umami.sh /docker-entrypoint.d/40-umami.sh
RUN chmod 755 /docker-entrypoint.d/40-umami.sh

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s CMD wget -qO- http://127.0.0.1/health || exit 1
