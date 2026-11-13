## Why

Con la ficha y la tabla de tipos abiertas a la vez, el overlay tapa buena parte del juego. Muchos jugadores tienen una segunda pantalla: allí podrían ver toda la información en una ventana normal, sin que nada flote encima del emulador.

## What Changes

- Nuevo ajuste **«Mostrar la ficha en»**: *Overlay* (como hasta ahora, por defecto) o *Panel* (`overlay.display` en `config.toml`). Se aplica al momento, sin reiniciar.
- En modo Panel, la ficha y la tabla de tipos dejan de ser ventanas flotantes. Pasan a estar dentro de una **ventana normal de Windows** con marco, que se puede redimensionar, maximizar y llevar a otro monitor, y que no está «siempre encima»:
  - a la izquierda, la ficha del rival (o las dos de un combate doble), con desplazamiento vertical si no cabe;
  - a la derecha, la tabla de tipos de la generación del perfil, visible desde el principio, con los tipos del rival y los tuyos resaltados y escalada para ocupar el espacio libre.
- Cuando no hay ficha (fin del combate, ✕, atajo de ocultar, temporizador), el panel sigue abierto y muestra «Esperando combate…» en el hueco de la ficha.
- El panel aparece al reconocer un rival sin quitar el foco al juego. Si se cierra, se puede volver a abrir con la nueva opción de la bandeja «Mostrar el panel», que solo aparece en modo Panel.
- El panel guarda su posición y su tamaño en `state.json`.

## Capabilities

### New Capabilities
- `panel-window`: modo Panel. Cubre el ajuste para elegir dónde se muestra la ficha, la ventana que contiene la ficha y la tabla de tipos, el estado sin combate, cómo se abre y se cierra, y qué guarda.

### Modified Capabilities
<!-- Ninguna: el overlay y la tabla flotante siguen igual en modo Overlay. -->

## Impact

- Código: `ui/overlay.py` y `ui/type_chart.py` (comportamiento cuando están dentro del panel), `ui/panel.py` (nuevo), `app.py`, `ui/settings.py` (Ajustes › Ficha), `ui/tray.py`, `core/config.py` (`overlay.display` y geometría del panel en `AppState`), catálogo inglés en `i18n/`.
- No se añaden dependencias.
- **Guía de uso:** sí la afecta. Ajustes › Ficha (opción nueva), menú de la bandeja («Mostrar el panel») y un apartado nuevo «Modo panel (dos pantallas)» con captura nueva del panel en los dos idiomas.
- README.md, README.es.md y CHANGELOG.md: se menciona el modo Panel.
