## Context

Qt no aplica `heightForWidth` al calcular el tamaño de una ventana de nivel superior, y con escalados altos las etiquetas que se parten en líneas necesitan más alto que el que la ventana les daba.

## Goals / Non-Goals

**Goals:** ninguna ficha recortada y ninguna ficha más alta que la pantalla. **Non-Goals:** rediseñar el contenido del modo Competitivo.

## Decisions

### D1. Altura mínima por tarjeta
Tras construir cada tarjeta con ancho fijo, `setMinimumHeight(layout.totalHeightForWidth(ancho))`.

### D2. Área desplazable dentro del panel
`QScrollArea` sin marco, con barra vertical solo cuando hace falta (8 px, sin flechas). El tamaño final es `min(alto del contenido, alto disponible de la pantalla − márgenes)`. Si hay desplazamiento, el ancho crece lo que mide la barra, para no recortar la tarjeta. Los bordes y márgenes del panel se leen de los widgets, no se fijan a mano.

### D3. Test con escala ×2 en un proceso aparte
El fallo de recorte solo se reproduce con escalado alto, así que el test lanza un proceso con `QT_SCALE_FACTOR=2`. Se comprobó que falla sin el arreglo y pasa con él.

## Risks / Trade-offs

- [Desplazar en lugar de ver todo de un vistazo en pantallas pequeñas] → Solo afecta al modo Competitivo en pantallas de menos de unos 880 px de alto. El modo Normal (~320 px) siempre cabe.

## Migration Plan

Ninguna.

## Open Questions

Ninguna.
