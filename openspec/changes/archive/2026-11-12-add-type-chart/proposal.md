## Why

La ficha da las eficacias contra el rival, pero para planear un cambio, elegir un ataque o repasar un emparejamiento que no está en pantalla hay que recordar la tabla de tipos. Y esa tabla cambia según la generación: la Gen 1 tiene 15 tipos y un Fantasma que no afecta a Psíquico, y de la Gen 2 a la 5 Acero resiste Fantasma y Siniestro. Una chuleta con atajo, ajustada al juego, evita salir a una web.

## What Changes

- Nuevo atajo global «Tabla de tipos» (por defecto `Ctrl+Alt+T`, configurable en `hotkeys.type_chart` y en *Ajustes → Atajos*). Muestra u oculta una ventana flotante con la tabla.
- Opción «Tabla de tipos» en la bandeja, con la pista del atajo.
- Tabla con el atacante en filas y el defensor en columnas: ×2, ×½ y ×0 en color; ×1 vacía. Solo aparecen los tipos de la generación del juego del perfil activo (sin perfil, la actual), y el título indica la generación.
- Si hay una ficha visible, las columnas de los tipos del Pokémon de la ficha se resaltan. El resaltado se actualiza al cambiar la ficha.
- La ventana está siempre delante, se arrastra, se cierra con su ✕ o con el atajo y queda excluida de la captura, como la ficha.
- Es reescalable (tirador o `Ctrl` + rueda) y recuerda posición y tamaño entre sesiones.

## Capabilities

### New Capabilities
- `type-chart`: tabla de tipos flotante por generación, con atajo y resaltado de los tipos de la ficha.

### Modified Capabilities
<!-- Ninguna. -->

## Impact

- Código: `ui/type_chart.py` (nuevo), `app.py` (atajo, mostrar/ocultar, resaltado), `core/config.py` (`hotkey_type_chart`), `ui/settings.py`, `ui/tray.py` y los catálogos de `i18n`. Se reutilizan `Pokedex.type_chart(generation)` y la exclusión de captura de `ui/overlay.py`.
- Tests: config, contenido de la tabla por generación (Gen 1, 2 y 9), resaltado y conmutación desde `Controller`.
- **Guía de uso (`site/guide.html`): sí la afecta.** Apartado nuevo «Tabla de tipos» con captura, fila en la tabla de atajos y opción nueva en el menú de la bandeja. Se regeneran las capturas de la bandeja y de Ajustes → Atajos.
- README.md, README.es.md y CHANGELOG.md (cambio visible para el usuario), y una sección en la portada de la web con la captura de la tabla y el buscador.
