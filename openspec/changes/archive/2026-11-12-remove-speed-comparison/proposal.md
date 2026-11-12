## Why

La sección «Contra tu…» de la ficha competitiva decía quién es más rápido comparando rangos de Velocidad con IVs y EVs de 0 a máximo. Sin conocer los IVs ni los EVs del rival, el veredicto («Eres más rápido», «Es más rápido») puede ser falso y lleva a malas decisiones en combate.

## What Changes

- **BREAKING** (visible): se quita la línea de velocidad de «Contra tu…» en la ficha competitiva.
- Se borran `SpeedVerdict` y `compare_speed` y sus textos traducidos.
- La descripción de la sección en Ajustes pasa a «Ventaja y eficacias de un lado y otro.».
- Las estadísticas reales del rival a su nivel (incluida la Velocidad mín.–máx.) siguen en la ficha.

## Capabilities

### New Capabilities

### Modified Capabilities
- `competitive-data`: se elimina el requisito «¿Quién es más rápido?».

## Impact

`core/competitive.py`, `ui/overlay.py`, `ui/settings.py`, `i18n/en_card.py`, `i18n/en_menus.py`, tests, guía, portada, README y CHANGELOG.
