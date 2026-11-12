## MODIFIED Requirements

### Requirement: Recalibrar y eliminar
El sistema SHALL permitir modificar los perfiles existentes en lugar de crear otros: recalibrar cualquiera de las regiones del perfil activo, cambiarle el nombre, reaplicarle un preset y eliminar perfiles.

- **Atajo de calibrar:** con un perfil activo, el atajo de calibrar (por defecto `Ctrl+Alt+C`) SHALL preguntar si se quiere recalibrar una región del perfil activo (Rival, 2.º rival, Tu Pokémon o Menú de ataques) o crear un perfil nuevo. Sin perfiles, SHALL empezar directamente la calibración de un perfil nuevo. El botón «Calibrar a mano…» de Ajustes sigue creando siempre un perfil nuevo.
- **Renombrar:** la tarjeta Perfil activo de *Ajustes › Perfiles* SHALL tener un campo Nombre que renombra el perfil al terminar de editarlo, sin cambiar su identificador ni sus regiones. Un nombre vacío MUST rechazarse y volver al anterior.
- **Aplicar un preset:** la tarjeta Perfil activo SHALL ofrecer «Aplicar un preset…», que abre el asistente de preset proponiendo el juego del perfil. Al guardar, el perfil activo SHALL pasar a tener las regiones, el juego y la imagen del juego del preset, conservando su nombre y su identificador. La región del 2.º rival (que los presets no traen) SHALL conservarse, llevada a la nueva imagen del juego si se puede. Si en el asistente se elige «Calibrar a mano…», SHALL ofrecerse recalibrar las regiones del perfil, no crear otro.

#### Scenario: Recalibración
- **WHEN** el usuario recalibra el perfil activo y confirma un nuevo rectángulo
- **THEN** se sobrescribe la región manteniendo el identificador y el nombre del perfil

#### Scenario: Atajo con un perfil activo
- **WHEN** el perfil «Espada» está activo, el usuario pulsa `Ctrl+Alt+C` y elige «Tu Pokémon»
- **THEN** se abre la calibración de la región de su Pokémon en «Espada» y no se crea ningún perfil

#### Scenario: Atajo para un perfil nuevo
- **WHEN** el perfil «Espada» está activo, el usuario pulsa `Ctrl+Alt+C` y elige «Crear un perfil nuevo…»
- **THEN** empieza la calibración de un perfil nuevo como hasta ahora

#### Scenario: Atajo sin perfiles
- **WHEN** no hay perfiles y el usuario pulsa `Ctrl+Alt+C`
- **THEN** empieza la calibración de un perfil nuevo sin preguntar

#### Scenario: Renombrar
- **WHEN** el usuario cambia el nombre «Pokémon Espada» por «Espada (Eden)» y sale del campo
- **THEN** el perfil se guarda con el nombre nuevo, el mismo identificador y las mismas regiones, y la lista y la bandeja lo muestran

#### Scenario: Nombre vacío
- **WHEN** el usuario borra el nombre y sale del campo
- **THEN** el campo vuelve al nombre anterior y el perfil no cambia

#### Scenario: Reaplicar un preset
- **WHEN** el usuario pulsa «Aplicar un preset…» en el perfil «Espada (Eden)» y guarda el asistente
- **THEN** «Espada (Eden)» conserva nombre e identificador y pasa a tener las regiones del preset, y no aparece ningún perfil nuevo

#### Scenario: Eliminación del perfil activo
- **WHEN** el usuario elimina el perfil activo y quedan otros perfiles
- **THEN** se borra su archivo y pasa a ser activo otro perfil existente
