## Why

Al publicar la web y ejecutar la CI salieron dos fallos de la ficha: con escalado de pantalla alto, los textos largos se recortaban en los combates dobles; y, una vez corregido eso, la ficha competitiva (~860 px) no cabía en pantallas de 720-768 px de alto (la del runner de GitHub y muchos portátiles).

## What Changes

- Cada tarjeta reserva la altura que necesita para su ancho (textos partidos en líneas).
- El overlay se limita a la altura disponible de la pantalla y su contenido se desplaza con la rueda del ratón, con una barra fina que no recorta la tarjeta.

## Capabilities

### New Capabilities
<!-- Ninguna. -->

### Modified Capabilities
- `battle-overlay`: el comportamiento de la ventana incluye ajustarse a la pantalla y no recortar textos.

## Impact

- `ui/overlay.py` (área desplazable y cálculo de tamaño), tests de UI (incluido uno en un proceso con escala ×2) y `tools/make_site_screenshots.py` (capturas sin límite de altura y medidas del HTML sincronizadas).
