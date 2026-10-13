# display-modes Specification

## Purpose
Modos de la ficha (Normal y Competitivo): contenido de cada uno y cómo se cambia entre ellos.
## Requirements
### Requirement: Modos de ficha
El sistema SHALL ofrecer dos modos de ficha: **Normal** (por defecto), pensado para la aventura y la captura, y **Competitivo**, pensado para el combate, con más datos. El modo se guarda en `config.toml` (`overlay.mode`).

#### Scenario: Modo por defecto
- **WHEN** se arranca por primera vez
- **THEN** la ficha está en modo Normal

### Requirement: Contenido del modo Normal
En modo Normal, la tarjeta SHALL mostrar de forma compacta: nombre y número, tipos, el ratio de captura destacado con su dificultad, debilidades (×4 y ×2), inmunidades, la comparativa «Contra tu X» si procede, la evolución, el total de estadísticas base y las otras formas. MUST NOT mostrar resistencias, barras de estadísticas ni habilidades.

#### Scenario: Ficha compacta
- **WHEN** se reconoce a Stufful en modo Normal
- **THEN** la tarjeta muestra tipos, «Captura: 140 · Media», debilidades, evolución y «Total 340», sin barras de estadísticas ni habilidades

### Requirement: Contenido del modo Competitivo
En modo Competitivo, la tarjeta SHALL mostrar todo lo del modo Normal más: el nivel leído, resistencias, estadísticas base con barras y rango real a su nivel, habilidades con su descripción visible y los cambios de eficacia que provocan, movimientos probables, «¿quién es más rápido?» dentro de la comparativa y datos de entrenamiento.

#### Scenario: Ficha competitiva
- **WHEN** se reconoce a Stufful de nivel 10 en modo Competitivo
- **THEN** la tarjeta muestra «Nv. 10», los rangos de sus estadísticas a nivel 10, la descripción de Peluche con «Fuego ×2», sus movimientos probables y que da 1 EV de Ataque

### Requirement: Cambiar de modo
El usuario SHALL poder cambiar de modo desde la bandeja (submenú «Modo de la ficha»), con un atajo global (`hotkeys.toggle_mode`, por defecto `Ctrl+Alt+M`) y desde Ajustes. El cambio se guarda y, si hay una ficha visible, MUST volver a dibujarse en el nuevo modo sin repetir el reconocimiento.

#### Scenario: Cambio con la ficha abierta
- **WHEN** la ficha de Stufful está visible en modo Normal y el usuario pulsa `Ctrl+Alt+M`
- **THEN** la misma ficha pasa a modo Competitivo y el modo queda guardado

