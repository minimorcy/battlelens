## Why

Las Megaevoluciones, las formas de Rotom, Deoxys, Giratina Origen, los Tri-Genios Avatar y otras formas cambian los tipos, las estadísticas o las habilidades, pero el nombre que se ve en pantalla es el mismo que el de la forma base. Ahora la ficha siempre muestra la forma original, así que contra Rotom Lavado da Tierra ×2 cuando en realidad le hace ×1, y contra Mega Charizard X no dice que es de tipo Dragón.

## What Changes

- **Formas alternativas en el dataset:** megaevoluciones, regresiones primigenias y las formas no regionales que cambian tipos, estadísticas o habilidades. Se descartan las cosméticas (Unown, Vivillon…), las Gigamax (mismos tipos y estadísticas), las de Pokémon dominante y las de compañero de Let's Go.
- **Disponibilidad según el juego:** cada forma aparece solo en los juegos donde existe, es decir, en el juego en que se introdujo y en los posteriores. Las megas y las primigenias, además, solo en los juegos con Megaevolución (X/Y, Rubí Omega/Zafiro Alfa, Sol/Luna, Ultrasol/Ultraluna, Let's Go, Leyendas Z-A y Champions).
- **«Otras formas»** incluye estas formas con sus tipos, además de las regionales.
- **Nuevo atajo `Ctrl+Alt+F`** («Cambiar de forma», configurable): alterna la forma del rival que tiene otras formas. Si son los dos, la del primero. La ficha se recalcula con los tipos, estadísticas, habilidades, eficacias y comparativa de la forma elegida. La elección se mantiene mientras siga ese Pokémon en combate (también si megaevoluciona), y se olvida cuando sale. La sección «Otras formas» recuerda el atajo.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `pokemon-data`: formas alternativas en el dataset, disponibilidad por juego y vista de una forma elegida.
- `battle-overlay`: atajo «Cambiar de forma» y ficha de la forma elegida.
- `app-settings`: el atajo se edita en Ajustes.

## Impact

- **Código:** `tools/build_dataset.py`, `core/pokedex.py` (formas, `view(..., form=)`, `form_cycle`), `core/config.py`, `app.py` (atajo y elección por especie), `ui/overlay.py` (pista del atajo y movimientos de la forma base para las megas) y `ui/settings.py`.
- **Datos:** `pokedex.json` crece unas 170 formas (unos 150 KB).
- **Configuración:** nueva clave `hotkeys.cycle_form`, con un valor por defecto para las configuraciones existentes.
