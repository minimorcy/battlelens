## ADDED Requirements

### Requirement: Tipos como iconos en la ficha
Cuando los iconos están disponibles (spec `type-icons`), la ficha SHALL dibujar como icono cada tipo que hoy sale como etiqueta: los tipos del Pokémon en la cabecera, «Contra tu…», «Tus movimientos», Eficacias, Movimientos probables y Otras formas. Los multiplicadores, los colores de cada apartado y el orden de los tipos MUST NOT cambiar. Los iconos de la cabecera SHALL ser más grandes que los del resto de secciones.

#### Scenario: Eficacias con iconos
- **WHEN** los iconos están disponibles y aparece la ficha de Pidgey
- **THEN** Debilidades muestra los iconos de Roca, Eléctrico y Hielo junto a su ×2, en su franja verde

#### Scenario: Movimiento sin tipo
- **WHEN** un movimiento leído no tiene tipo conocido
- **THEN** su casilla muestra «?» como ahora
