## Context

PokéAPI ofrece: `pokemon_species.capture_rate`, `evolves_from_species_id` y `evolution_chain_id`; `pokemon_evolution` (desencadenante, nivel mínimo, objeto, objeto equipado, amistad, momento del día… con varias filas por especie según el juego y `is_default`); `ability_flavor_text` (descripción por grupo de versiones e idioma, con saltos de línea); `items` e `item_names`.

## Goals / Non-Goals

**Goals:** datos útiles en combate sin salir del juego; cadena coherente con la generación del juego.

**Non-Goals:** movimientos que aprende, localización de los Pokémon, EVs y estadísticas de crecimiento; formas regionales con evolución propia (Galar Meowth → Perrserker): se muestra la cadena de la especie.

## Decisions

### D1. Descripción de habilidad: la más reciente por idioma
Por cada habilidad e idioma se toma el texto del grupo de versiones más alto y se normalizan los espacios (los textos traen saltos de línea del juego). Se guarda en un mapa global `ability_descriptions[identificador]`, que no se repite en cada especie, para no inflar el JSON.

### D2. Evolución: una condición por especie
Para cada especie que evoluciona de otra se toma la fila de `pokemon_evolution` con `is_default = 1` (si no hay, la primera) y se guardan `trigger`, `min_level`, `item`, `held_item`, `min_happiness` y `time_of_day`. Los nombres de objeto se guardan en un mapa global `items` (solo los que aparecen). Las condiciones raras (lugar concreto, movimiento conocido…) se muestran como «Especial».

### D3. Cadena calculada en `Pokedex`
`evolution_stages(species_id, generation)` sube por `evolves_from` hasta la raíz y recorre en anchura sus descendientes, saltando las especies de una generación posterior. Devuelve una lista de etapas, cada una con pares (nombre, condición). La ficha la pinta en una sola línea, con «→» entre etapas y «/» entre ramas, y con salto de línea automático.

### D4. Etiquetas de condición localizadas en el código
Las condiciones («Nv.», «Intercambio», «Amistad», «de día»…) se traducen en una pequeña tabla para es/en; el resto de idiomas usa el inglés.

### D5. Descripción como *tooltip*
La descripción se muestra al pasar el ratón (tooltip de Qt) para no alargar la tarjeta. El overlay no roba el foco, pero sí recibe el ratón, así que el tooltip funciona.

## Risks / Trade-offs

- [Evoluciones con condiciones múltiples o que dependen del juego (p. ej. Eevee → Leafeon por lugar, más tarde por Piedra Hoja)] → Se muestra la condición por defecto de PokéAPI; aceptable como orientación.
- [Tamaño del dataset] → Unos 200 KB más; el instalador apenas cambia (JSON comprimido).

## Migration Plan

Ninguna.

## Open Questions

Ninguna.
