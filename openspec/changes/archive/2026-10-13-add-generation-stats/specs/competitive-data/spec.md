## MODIFIED Requirements

### Requirement: Estadísticas reales a su nivel
Conocido el nivel, el sistema SHALL calcular para cada estadística el rango real con la fórmula del juego del perfil (Shedinja siempre tiene 1 PS):
- **Gen 3 en adelante** (y sin juego): mínimo con IV 0, EV 0 y naturaleza desfavorable; máximo con IV 31, EV 252 y naturaleza favorable (los PS no dependen de la naturaleza).
- **Gen 1-2:** `⌊((Base + DV) × 2 + ⌊⌈√EXP⌉ / 4⌋) × Nivel / 100⌋ + 5` (PS: `+ Nivel + 10`); mínimo con DV 0 y experiencia de estadística 0, máximo con DV 15 y 65 535.
- **Let's Go Pikachu/Eevee:** `⌊⌊(⌊(2 × Base + IV) × Nivel / 100⌋ + 5) × Naturaleza⌋ × Amistad⌋ + AV` (PS: `⌊(2 × Base + IV) × Nivel / 100⌋ + Nivel + 10 + AV`); mínimo con IV 0, naturaleza ×0,9 y amistad ×1,0; máximo con IV 31, naturaleza ×1,1 y amistad ×1,1. Los AVs son 0 para el rival y 0-200 para tu Pokémon.
- **Leyendas: Arceus:** `⌊⌊(Nivel / 50 + 1) × Base / 1,5⌋ × Naturaleza⌋ + B` (PS: `⌊(Nivel / 100 + 1) × Base⌋ + Nivel + B`), con `B = ⌊(√Base × f(NE) + Nivel) / 2,5⌋` y `f` = 0, 2, 3, 4, 7, 8, 9, 14, 15, 16, 25 para los niveles de esfuerzo 0-10; mínimo con nivel de esfuerzo 0 y naturaleza ×0,9; máximo con nivel de esfuerzo 10 y naturaleza ×1,1.

#### Scenario: Rango a nivel 50
- **WHEN** se calcula Garchomp (PS 108, Velocidad 102) a nivel 50 sin juego
- **THEN** los PS van de 168 a 215 y la Velocidad de 96 a 169

#### Scenario: Shedinja
- **WHEN** se calculan los PS de Shedinja a cualquier nivel
- **THEN** el rango es 1-1

#### Scenario: Gen 1
- **WHEN** se calcula Pikachu de nivel 5 en `red-blue`
- **THEN** los PS van de 18 a 23 y la Velocidad de 14 a 18

#### Scenario: Let's Go
- **WHEN** se calcula un Pikachu rival de nivel 5 en `lets-go-pikachu-lets-go-eevee`
- **THEN** los PS van de 18 a 20 y la Velocidad de 12 a 17

#### Scenario: Leyendas: Arceus
- **WHEN** se calcula Pikachu de nivel 5 en `legends-arceus`
- **THEN** la Velocidad va de 61 a 168
