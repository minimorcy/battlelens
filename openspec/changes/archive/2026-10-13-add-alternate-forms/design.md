## Context

`build_dataset.py` solo guarda las formas con prefijo regional (`alola`, `galar`, `hisui`, `paldea`). `Pokedex.view` elige la forma regional del juego, y `other_forms` lista las demás regionales. El nombre que lee el OCR es siempre el de la especie, así que la forma alternativa no se puede reconocer: tiene que elegirla el usuario. Los atajos se definen en `Config`, `App._parse_hotkeys`, `App._on_hotkey` y `ui/settings.HOTKEY_FIELDS`.

## Goals / Non-Goals

**Goals:**
- Ficha correcta para las formas que cambian el combate, eligiéndolas con una pulsación.
- No mostrar formas que no existen en el juego del perfil.

**Non-Goals:**
- Detectar la forma automáticamente (por el sprite o por el texto de la megaevolución).
- Cambiar la forma de tu Pokémon (la comparativa usa su forma por defecto o regional).
- Gigamax y teracristalización (no cambian los tipos de la ficha, o dependen del combate).

## Decisions

### D1. Formas en el dataset
Cada entrada de `forms` añade `kind` (`regional`, `mega` o `alternate`) e `introduced` (el identificador del grupo de versiones, con las DLC sustituidas por su juego base: `the-isle-of-armor`/`the-crown-tundra` → `sword-shield`, `the-teal-mask`/`the-indigo-disk` → `scarlet-violet`). Se incluye una forma de `pokemon_forms` si:
- su Pokémon no es el de por defecto y no es regional (las regionales siguen igual, con `kind: regional`);
- difiere de la forma por defecto en tipos, estadísticas o habilidades;
- no es `totem`, `starter` (compañeros de Let's Go) ni Gigamax;
- no es idéntica a otra forma alternativa ya incluida de la misma especie (los núcleos de Minior, por ejemplo).

Las megas (`is_mega`) y las primigenias (`-primal`) son `kind: mega`. Los juegos añaden `order` (el orden del grupo de versiones) para comparar cuándo se introdujo cada forma.

### D2. Disponibilidad
`Pokedex.form_available(form, game)` aplica dos reglas: el `order` del juego en que se introdujo es menor o igual que el del juego, y, si `kind == "mega"`, el juego está en `MEGA_GAMES`. Sin juego, todas las formas están disponibles. Las regionales siguen apareciendo todas en «Otras formas» (como ahora) y nunca quedan bloqueadas.

### D3. `view(species_id, game, lang, form=None)`
`form` es el identificador de una forma o el identificador de la especie, que equivale a su forma base. `None` mantiene la elección automática (regional o base). Una forma alternativa usa sus propios tipos, sin `past_types`, y sus estadísticas y habilidades con las reglas de generación ya existentes. `other_forms` lista las formas disponibles distintas de la mostrada, empezando por la base. `SpeciesView` añade `form_id` (el identificador de lo que se muestra) y `base_pokemon` (el Pokémon de la especie, para los movimientos de las megas).

`Pokedex.form_cycle(species_id, game) -> tuple[str, ...]` devuelve la forma automática seguida de las demás disponibles (la base si la automática es regional, las otras regionales y las alternativas), sin repetir.

### D4. Elección en la app
`App._form_choice: dict[int, str]` va de especie a forma elegida. `_show_battle` le pasa al overlay las vistas con `form=self._form_choice.get(sid)` y elimina de `_form_choice` las especies que ya no están entre los rivales de la clave. El atajo `cycle_form` busca el primer rival de `_last_battle` cuyo `form_cycle` tenga más de una entrada, avanza al siguiente elemento (circular) y vuelve a dibujar con `_redraw_last_battle`. La detección automática no reinicia la elección porque la clave (especies) no cambia al megaevolucionar.

### D5. Overlay
La sección «Otras formas» termina con «`Ctrl+Alt+F`: cambiar de forma». El texto del atajo lo fija la app en `Overlay.form_hotkey` y se omite si está vacío. En `_moves`, si `view.pokemon` no tiene movimientos, se usa `view.base_pokemon`.

### D6. Configuración
Se añade `Config.hotkey_cycle_form = "Ctrl+Alt+F"` (clave `hotkeys.cycle_form`), con el mismo tratamiento que `toggle_mode`: plantilla, validación, Ajustes, aviso si no se puede registrar y recarga al guardar.

## Risks / Trade-offs

- [Lo elige el usuario] → Es la única forma fiable sin leer sprites. La pista en la ficha lo hace descubrible.
- [Tamaño del dataset] → Unos 150 KB más sobre ~1 MB, que se cargan al arrancar. Es aceptable.
- [Disponibilidad aproximada] → La regla «introducida en ese juego o antes» no refleja las ausencias de la Pokédex de cada juego (por ejemplo, Rotom en Leyendas Z-A). Eso no muestra datos falsos, solo una opción de más.

## Migration Plan

Se regenera el dataset y se añade un atajo con valor por defecto. Las configuraciones existentes lo reciben al cargarse.

## Open Questions

Ninguna.
