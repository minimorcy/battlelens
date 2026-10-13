## Why

La ficha siempre muestra la forma original de cada especie y la tabla de tipos actual. En juegos con formas regionales eso da **información incorrecta**: en Pokémon Espada, Zigzagoon de Galar es Siniestro/Normal y no Normal, así que sus debilidades salen mal. En juegos antiguos también: Clefairy era Normal hasta la Gen 5, y la Gen 1 no tenía tipos Siniestro, Acero ni Hada. Además, el usuario tiene que elegir a mano el perfil cuando cambia de juego, aunque el título de la ventana del emulador ya suele decir qué juego es.

## What Changes

- El dataset incluye los **juegos** (grupos de versiones, con su generación y su forma regional), las **formas regionales** (Alola, Galar, Hisui, Paldea) con sus tipos, estadísticas y habilidades, los **tipos anteriores** de cada especie y la **tabla de eficacia** de cada generación.
- Cada perfil puede indicar su **juego**. La ficha usa entonces la forma regional que corresponda, los tipos y la tabla de esa generación, y oculta las habilidades en las generaciones que no las tenían.
- La ficha indica la forma mostrada («Forma de Galar») y lista las **otras formas** con sus tipos, para los juegos donde conviven varias.
- **Detección del juego por el título de la ventana:** al calibrar, se propone el juego y el nombre del perfil. Al cambiar de ventana o de juego, se **activa automáticamente** el perfil de ese juego si existe.
- Desde la bandeja se puede cambiar el juego del perfil activo.

## Capabilities

### New Capabilities
- `game-catalog`: catálogo de juegos (grupo de versiones, generación, forma regional y nombres) y detección del juego a partir del título de una ventana.

### Modified Capabilities
- `pokemon-data`: el dataset incluye formas regionales, tipos anteriores, eficacias por generación y juegos; la eficacia se calcula para una generación concreta; se añade la resolución de la forma y de los tipos según el juego.
- `game-profiles`: el perfil incluye el juego (opcional); la calibración propone juego y nombre; activación automática del perfil por juego.
- `battle-overlay`: la ficha muestra la forma, las otras formas y los datos propios de la generación; el menú de la bandeja permite cambiar el juego del perfil.

## Impact

- **Código:** `tools/build_dataset.py` (CSV nuevos: pokemon_forms, pokemon_form_names, pokemon_types_past, type_efficacy_past, versions, version_names, version_groups), `core/pokedex.py` (vista de especie según el juego), nuevo `core/games.py`, `core/profiles.py` (campo `game`, compatible con los perfiles existentes), `ui/overlay.py`, `ui/calibrator.py`, `ui/tray.py`, `app.py`.
- **Datos:** `pokedex.json` crece (formas y juegos). Los perfiles existentes siguen funcionando sin juego asignado (comportamiento actual).
- **Sin dependencias nuevas.**
