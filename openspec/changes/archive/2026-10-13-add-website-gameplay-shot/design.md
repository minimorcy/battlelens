## Context

La captura se hizo en Eden (emulador de Switch) con Pokémon Espada. El usuario pidió explícitamente no mostrar el emulador.

## Goals / Non-Goals

**Goals:** una imagen real y fiel de cómo se ve BattleLens jugando. **Non-Goals:** galería de varios juegos.

## Decisions

### D1. Recorte automático de la interfaz del emulador
Las barras de menús y de estado se detectan como el primer cambio de color en la columna central desde arriba y desde abajo (las barras no tienen texto en el centro). Las franjas negras laterales se detectan como columnas con luminancia mayoritaria < 12.

### D2. Ficha real, reconocida sobre la propia captura
Se usa `read_crop` del pipeline sobre las regiones del nombre del rival y de tu Pokémon. La ficha se renderiza en un proceso aparte con `QT_SCALE_FACTOR=1.5` (como en una pantalla al 150 %) y se compone en la esquina superior izquierda, sobre el cielo, como cuando el usuario la arrastra ahí.

### D3. Modo Normal
Al generar la captura se comprobó que el OCR no lee el nivel con la fuente grande de Espada («Nv Id» en lugar de «Nv. 16»), así que la ficha competitiva saldría sin movimientos. Se usa el modo Normal, el de por defecto, y la limitación queda documentada en el README.

## Risks / Trade-offs

- [Copyright de la imagen del juego] → Crédito explícito, sin emulador, uso ilustrativo en un proyecto de fans gratuito. Si los titulares lo pidieran, basta con borrar `gameplay.jpg` y la sección.

## Migration Plan

Ninguna.

## Open Questions

Ninguna.
