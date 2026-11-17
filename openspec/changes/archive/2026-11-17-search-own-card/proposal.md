## Why

Hoy el buscador reutiliza la ficha del combate: buscar un Pokémon tapa al rival y la siguiente detección tapa la búsqueda, por eso la detección se pausa mientras el buscador está abierto. Consultar otra especie en pleno combate (¿qué tipos tiene lo que puede salir después?) obliga a perder de vista al rival. En el modo panel, además, el buscador es un diálogo aparte cuando hay sitio de sobra para tenerlo siempre a mano.

## What Changes

- La búsqueda abre su **propia ficha**, distinta de la del rival. Las dos conviven: la detección automática no toca la ficha buscada y la búsqueda no toca la del rival.
- La detección automática **deja de pausarse** mientras se busca.
- La ficha buscada no se oculta con el fin del combate, el atajo de ocultar ni el temporizador; solo con su ✕ (o al buscar otra, que la sustituye). Sigue sin publicarse en el stream.
- El atajo de cambiar forma (`Ctrl+Alt+F`) sigue actuando solo sobre el rival; la ficha buscada cambia de forma con sus flechas ◀ ▶. El cambio de modo (normal/competitivo) se aplica a las dos.
- **Modo overlay**: el buscador sigue siendo un diálogo con atajo; la ficha buscada sale en una segunda ventana flotante que se puede arrastrar y recuerda su posición (`state.json`).
- **Modo panel**: tres columnas. Izquierda, la ficha del rival (o «Esperando combate…»); centro, la tabla de tipos con las naturalezas; derecha, el buscador **siempre visible** y debajo la ficha buscada. En este modo el atajo «Buscar Pokémon» trae el panel al frente y pone el foco en su buscador en lugar de abrir el diálogo.
- El panel arranca más ancho por defecto para que quepan dos fichas y la tabla.

## Capabilities

### New Capabilities
<!-- ninguna -->

### Modified Capabilities
- `pokemon-search`: la ficha buscada es independiente de la del rival; la detección ya no se pausa; en modo panel el buscador está integrado y el atajo lo enfoca.
- `panel-window`: maqueta de tres columnas (rival, tablas, buscador + ficha buscada) y tamaño inicial mayor.

## Impact

- Código: `src/battlelens/ui/search.py` (el campo con sugerencias pasa a un widget reutilizable por el diálogo y el panel), `src/battlelens/ui/panel.py` (tercera columna), `src/battlelens/app.py` (segunda `Overlay`, quitar la pausa y la marca `_searched`), `src/battlelens/core/config.py` (`State.search_card_pos`).
- Tests: `tests/` del buscador, del panel y de la app.
- **Guía de uso** (`site/guide.html`, ES y EN): apartados del buscador y del modo panel; capturas del panel y del buscador regeneradas con `tools/make_guide_screenshots.py`.
- `README.md`, `README.es.md` y `CHANGELOG.md` (los dos idiomas): cambio visible para el usuario.
- Sin dependencias nuevas.
