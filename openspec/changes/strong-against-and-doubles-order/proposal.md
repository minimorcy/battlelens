## Why

- El usuario echa de menos ver contra qué es fuerte el rival: la ficha dice qué le hace daño, pero no a qué tipos amenaza.
- En combates dobles de Espada las fichas salían al revés que los Pokémon en el campo. En individuales el rival sale a la derecha, así que el usuario calibra ahí el «rival» y a su izquierda el «2.º rival»; la ficha pintaba siempre «rival, 2.º rival» de izquierda a derecha.

## What Changes

- «Fuerte contra» en las eficacias (ficha y ficha del stream), justo después de «Debilidades»: los tipos a los que alguno de los tipos del rival hace ×2 (ataques con STAB), con la tabla de la generación del juego. En rojo, porque son una amenaza para ti. Se calcula en `Pokedex.strong_against` y viaja en `SpeciesView.strong_against`.
- En dobles, las tarjetas siguen el orden de izquierda a derecha de las regiones en pantalla (también en el modo stream). El reconocimiento y la clave (rival, 2.º rival, tu Pokémon) no cambian.

## Capabilities

### Modified Capabilities
- `battle-overlay`: «Fuerte contra» y orden de las tarjetas en dobles.

## Impact

- Código: `core/pokedex.py`, `ui/overlay.py`, `stream/payload.py`, `app.py`, `i18n/en_card.py`.
- Tests: `tests/test_pokedex.py`, `tests/test_card_visuals.py`, `tests/test_stream.py`, `tests/test_app.py`.
- **Guía de uso: sí.** «Eficacias» y «2.º rival» en la ficha y en Ajustes (es/en); capturas de la guía y de la web regeneradas. Web: sección nueva de la 0.5 con la pantalla de inicio (imagen según el idioma). README (es/en) y CHANGELOG.
