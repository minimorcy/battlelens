## Context

`Controller.calibrate_region(role)` ya recalibra una región del perfil activo (y la ancla a su `game_area`), y *Ajustes › Perfiles* la ofrece con «Recalibrar…». `calibrate_new` crea un perfil nuevo y es lo que ejecuta el atajo. `_new_profile_from_preset_with` usa `PresetWizard` y `to_profile_regions` para construir un perfil. `ProfileStore.save` guarda por id, así que un `replace(profile, …)` actualiza el mismo archivo.

## Goals / Non-Goals

**Goals:** que modificar un perfil sea el camino corto y crear otro el explícito.

**Non-Goals:** duplicar perfiles, editar regiones con números, deshacer.

## Decisions

- **D1 · El atajo apunta a `calibrate()`**, que decide: sin perfil activo → `calibrate_new()`; con perfil → `ask_calibration_target(nombre, regiones)` (diálogo nuevo en `ui/calibrator.py`) y después `calibrate_region(role)` o `calibrate_new()`. El botón de Ajustes sigue llamando a `calibrate_new()`, porque allí ya está claro que es «nuevo». El diálogo es una lista de botones: las cuatro regiones (con «✓» en las ya calibradas) y «Crear un perfil nuevo…». Así sigue siendo un solo clic.
- **D2 · Renombrar en línea**: `QLineEdit` en la tarjeta Perfil activo con `editingFinished` → señal `rename_requested(str)` → `Controller.rename_profile`. Encaja con la página, donde los cambios «se aplican al momento». Un nombre vacío o igual al actual no hace nada y el campo vuelve al nombre guardado en `refresh`. Descartado `QInputDialog`: un clic más y otra ventana.
- **D3 · Reaplicar un preset reutiliza el asistente**: se extrae de `_new_profile_from_preset_with` el cálculo de regiones (`_preset_regions(wizard, image)` → regiones + `game_area`). `apply_preset_to_active()` abre `PresetWizard` proponiendo `profile.game`. Al guardar hace `replace(profile, region=…, own_region=…, moves_region=…, game=wizard.game_id, game_area=…)` sin pedir nombre. Si el preset no trae alguna región opcional, se quita, porque la antigua no casaría con la nueva imagen del juego. `rival2_region` se lleva con `Region.remap(antiguo game_area, nuevo)` cuando hay los dos; si no, se conserva tal cual. Con «Calibrar a mano…» en el asistente se abre el diálogo de D1 sin la opción de perfil nuevo.
- **D4 · Sin cambios en el modelo**: `Profile` y `ProfileStore` no cambian; todo es `replace` + `save`.

## Risks / Trade-offs

- [El usuario esperaba que `Ctrl+Alt+C` creara un perfil directamente] → «Crear un perfil nuevo…» está en el mismo diálogo, a un clic. La guía lo explica.
- [Reaplicar un preset borra regiones opcionales calibradas a mano que el preset no trae] → el diálogo del asistente ya muestra lo que lee con el preset y la guía avisa. Se pueden volver a calibrar.
