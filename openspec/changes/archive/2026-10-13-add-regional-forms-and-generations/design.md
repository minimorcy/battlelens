## Context

`pokedex.json` solo tiene la forma por defecto de cada especie y la tabla de tipos actual. PokéAPI ofrece en CSV todo lo que falta:

- `pokemon_forms` + `pokemon` + `pokemon_form_names`: formas no predeterminadas, con `form_identifier` (`alola`, `galar`, `galar-standard`, `hisui`, `paldea`, `paldea-*-breed`…) y nombres localizados («Zigzagoon de Galar»).
- `pokemon_types_past (pokemon_id, generation_id, type_id, slot)`: tipos que tuvo un Pokémon **hasta** esa generación inclusive (p. ej. Clefairy → Normal hasta la Gen 5).
- `type_efficacy_past (damage_type_id, target_type_id, damage_factor, generation_id)`: multiplicadores distintos **hasta** esa generación inclusive (6 filas: Veneno↔Bicho en Gen 1, Fantasma→Psíquico ×0 en Gen 1, Fantasma/Siniestro→Acero ×½ hasta la Gen 5…).
- `types.generation_id`: generación en que aparece cada tipo (Siniestro y Acero en la 2, Hada en la 6).
- `version_groups`, `versions`, `version_names`: juegos, su generación y sus nombres localizados.

## Goals / Non-Goals

**Goals:**
- Ficha correcta en juegos con formas regionales y en generaciones antiguas.
- Elegir el perfil sin intervención cuando el título de la ventana identifica el juego.
- Retrocompatibilidad: los perfiles existentes siguen funcionando igual.

**Non-Goals:**
- Estadísticas base antiguas (el «Especial» único de la Gen 1, los cambios de estadísticas de la Gen 6). Se mantienen las actuales.
- Formas no regionales (megaevoluciones, formas Gigamax, formas de Rotom, Deoxys…).
- Detectar la forma por la imagen. La forma se deduce del juego.

## Decisions

### D1. Vista de especie como objeto de dominio (`SpeciesView`)
`Pokedex.view(species_id, game=None) -> SpeciesView` concentra todas las reglas: forma, tipos por generación, habilidades por generación, otras formas y tabla de tipos. El overlay solo pinta la vista y no decide nada. Así las reglas se prueban sin Qt.

### D2. Forma regional según el juego, con mapa explícito
La forma regional de un juego **no** sale de `version_group_regions`: Let's Go (región Kanto) usa formas de Alola, y las DLC de Espada/Escudo cuentan como Galar. Se define en `build_dataset.py` un mapa `grupo de versiones → forma`: sun-moon, ultra-sun-ultra-moon y lets-go → `alola`; sword-shield, the-isle-of-armor y the-crown-tundra → `galar`; legends-arceus → `hisui`; scarlet-violet, the-teal-mask y the-indigo-disk → `paldea`. Una forma encaja si su `form_identifier` empieza por ese prefijo. Si hay varias (Tauros de Paldea tiene tres razas, Darmanitan de Galar tiene modo normal y zen), se usa la primera según `form_order` y el resto aparece en «Otras formas».
*Alternativa descartada:* elegir la forma leyendo la imagen. Es mucho más complejo, y el juego ya determina la forma en casi todos los casos. Las excepciones se cubren con «Otras formas».

### D3. Tipos y eficacias anteriores: «hasta la generación N inclusive»
Para los tipos de una especie en la generación G, se toma la entrada de `past_types` con el menor `until_generation ≥ G`; si no hay ninguna, se usan los tipos actuales. La tabla de la generación G se construye partiendo de la actual, eliminando los tipos con `generation > G` y aplicando para cada par atacante-defensor la entrada pasada con el menor `until_generation ≥ G`. Las tablas se cachean por generación.
Los tipos anteriores solo se aplican a la forma por defecto: las formas regionales son de la Gen 7 en adelante y PokéAPI no les asigna tipos anteriores.

### D4. Detección del juego por título
`core/games.py` normaliza el título (mayúsculas, sin acentos, sin signos salvo espacios) y busca cada nombre de versión, también normalizado, como palabra completa con `\b…\b`. Los nombres de 4 caracteres o menos exigen «POKEMON » delante, para evitar falsos positivos con «X», «Y», «Sol» o «Rojo». Si coinciden varios, gana el más largo («Rojo Fuego» frente a «Rojo»). Se añade una tabla corta de títulos internos de ROM (`POKEMON EMER`, `POKEMON FIRE`, `POKEMON LEAF`, `POKEMON RUBY`, `POKEMON SAPP`, `POKEMON PL`, `POKEMON HG`, `POKEMON SS`), que son los que muestran mGBA y DeSmuME cuando no hay nombre de archivo.
El identificador detectado es el del **grupo de versiones**, que es lo que guarda el perfil. Las DLC (`the-isle-of-armor`…) se reducen a su juego base para la detección.

### D5. `game` opcional en el perfil y activación automática
El campo `game` en el JSON del perfil es opcional (`None` = comportamiento actual), lo que mantiene la compatibilidad. La activación automática ocurre en `select_window` y al principio de `recognize`: `detect_game(title)` → `ProfileStore.find_by_game(game)`. Así, si el usuario cambia de ROM en el mismo emulador, el siguiente reconocimiento ya usa el perfil correcto. Si hay varios perfiles del mismo juego, se mantiene el activo cuando ya es de ese juego y, si no, se elige el primero por nombre.

### D6. Diálogo de perfil nuevo
`ask_profile_name` pasa a ser `ProfileDialog`, con un nombre (propuesto: «Pokémon <versión detectada>» o el título de la ventana) y un desplegable de juegos ordenado por generación, con «Sin especificar» al principio. Por defecto queda seleccionado el juego detectado.

### D7. Formato del dataset
`pokedex.json` añade: `games` (lista ordenada por `order`), `type_generation`, `type_efficacy_past` y, por especie, `past_types` y `forms` (cada forma con `identifier`, `form`, `names`, `types`, `stats` y `abilities`). Se mantiene `"format": 2` para detectar datasets antiguos. Tamaño estimado: unos 700 KB (antes 625 KB).

## Risks / Trade-offs

- [Juegos donde conviven la forma regional y la original (DLC de Espada con Vulpix de Alola, Wooper de Johto en Paldea)] → «Otras formas» muestra la alternativa con sus tipos, así que el usuario la ve sin cambiar nada.
- [La detección por título falla en emuladores que no muestran el nombre del juego] → El juego se puede elegir a mano al calibrar o desde la bandeja. La detección solo sugiere.
- [Falso positivo de detección en títulos con palabras como «Esmeralda»] → Solo se analiza la ventana objetivo, que es el emulador, y un perfil solo se activa si existe uno de ese juego.
- [Estadísticas antiguas no contempladas] → Documentado en el README como limitación.

## Migration Plan

No hay migración: el dataset se regenera y se incluye en el repositorio, y los perfiles sin `game` funcionan igual que antes.

## Open Questions

Ninguna.
