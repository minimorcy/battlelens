## Why

Para retocar un perfil que ya funciona (el rival se lee mal, cambiaste de emulador o de tamaño de ventana), el camino natural, `Ctrl+Alt+C`, siempre crea un perfil nuevo. Al final se acumulan perfiles casi iguales. Recalibrar una región existe, pero escondido en *Ajustes › Perfiles*, y no hay forma de renombrar un perfil ni de devolverlo a las regiones de su preset.

## What Changes

- `Ctrl+Alt+C` con un perfil activo pregunta qué hacer: recalibrar una de sus regiones (Rival, 2.º rival, Tu Pokémon, Menú de ataques) o crear un perfil nuevo. Sin perfiles, crea uno como hasta ahora.
- *Ajustes › Perfiles → Perfil activo* tiene un campo **Nombre** para renombrar el perfil; el cambio se aplica al momento.
- *Ajustes › Perfiles → Perfil activo* tiene el botón **Aplicar un preset…**: abre el asistente de preset sobre el perfil activo y sustituye sus regiones y su juego por los del preset, sin crear otro perfil. Conserva el nombre y el identificador.

## Capabilities

### New Capabilities
<!-- Ninguna. -->

### Modified Capabilities
- `game-profiles`: «Recalibrar y eliminar» pasa a cubrir también el atajo de calibrar con un perfil activo, renombrar y reaplicar un preset.

## Impact

- Código: `app.py` (`calibrate` como entrada del atajo, `rename_profile`, `apply_preset_to_active`), `ui/calibrator.py` (diálogo para elegir qué recalibrar), `ui/settings.py` (campo Nombre y botón «Aplicar un preset…») y catálogos de `i18n`.
- Tests: el atajo con y sin perfil, renombrar (incluido el nombre vacío) y reaplicar un preset conservando id y nombre.
- **Guía de uso (`site/guide.html`): sí la afecta.** Hay que tocar «Calibrar a mano» (lo que hace `Ctrl+Alt+C` con un perfil activo), la tarjeta Perfil activo de Ajustes › Perfiles (Nombre y Aplicar un preset…) y la captura de Ajustes › Perfiles, y añadir la captura nueva del diálogo de recalibrar.
- README.md, README.es.md, CHANGELOG.md y la sección de novedades de la portada.
