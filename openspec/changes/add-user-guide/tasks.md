## 1. Capturas

- [x] 1.1 `tools/make_guide_screenshots.py`: bandeja, Ajustes (General, Ficha, Reconocimiento, Atajos, Modo stream, Perfiles), asistente de presets, calibración y fichas (por defecto, Normal, Competitivo, doble y formas), en español e inglés, a doble resolución
- [x] 1.2 Imagen del emulador a partir de `gameplay.jpg` sin la ficha y con barras de emulador; JPEG para las que llevan imagen del juego
- [x] 1.3 Medidas `width`/`height` de las capturas sincronizadas en `guide.html`

## 2. Página

- [x] 2.1 `site/guide.html` con índice y un bloque completo por idioma
- [x] 2.2 Estilos de la guía en `styles.css` (sin estilos en línea por la CSP), adaptables a móvil
- [x] 2.3 Enlaces desde la portada, `Dockerfile`, `sitemap.xml` y crédito del juego en el pie

## 3. Analítica y pruebas

- [x] 3.1 `40-umami.sh`: inserta el script en todas las páginas con el marcador y amplía la CSP una sola vez
- [x] 3.2 Tests: recursos locales, paridad de idiomas, mismo contenido en los dos bloques, índice, medidas de las capturas y Umami en las dos páginas
- [ ] 3.3 Revisión manual en el navegador (escritorio y móvil real) antes de desplegar
