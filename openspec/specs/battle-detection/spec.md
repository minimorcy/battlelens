# battle-detection Specification

## Purpose
Detección automática del combate: vigilar la región del nombre, decidir cuándo reconocer y cuándo mostrar u ocultar la ficha, sin intervención del usuario.
## Requirements
### Requirement: Vigilancia periódica
WHILE la detección automática está activada, hay ventana objetivo y perfil activo, el sistema SHALL capturar cada `detection.interval_ms` milisegundos (500 por defecto) la región del nombre del perfil activo y calcular su huella: una miniatura en escala de grises de 32×12 píxeles. Si la ventana está minimizada o una vigilancia anterior no ha terminado, ese ciclo se omite sin avisar.

#### Scenario: Vigilancia en marcha
- **WHEN** la detección automática está activada con ventana objetivo y perfil
- **THEN** la región se captura periódicamente sin interferir con el reconocimiento manual

#### Scenario: Ventana minimizada
- **WHEN** el emulador está minimizado
- **THEN** los ciclos se omiten sin mostrar ningún aviso

### Requirement: Disparo del reconocimiento
El sistema SHALL lanzar un reconocimiento sobre el recorte capturado cuando la huella lleva al menos 2 ciclos consecutivos estable (diferencia media absoluta ≤ 8 sobre 255 respecto al ciclo anterior) y además difiere de la huella del último intento de reconocimiento. Mientras la región cambia, no se reconoce.

#### Scenario: Entrada en combate
- **WHEN** aparece el recuadro con el nombre del rival y se mantiene estable 2 ciclos
- **THEN** se reconoce una sola vez

#### Scenario: Escena en movimiento
- **WHEN** la región cambia en todos los ciclos (por ejemplo, al caminar)
- **THEN** no se lanza ningún reconocimiento

#### Scenario: Región sin cambios
- **WHEN** la región sigue igual que en el último intento
- **THEN** no se vuelve a reconocer

### Requirement: Mostrar la ficha en modo automático
WHEN un reconocimiento automático identifica una especie distinta de la que muestra la ficha, el sistema SHALL mostrar su ficha. Si identifica la misma especie, no hace nada (tampoco vuelve a mostrar una ficha que el usuario haya ocultado). Si no la identifica, MUST NOT mostrar el aviso de «No reconocido».

#### Scenario: Nuevo rival
- **WHEN** la ficha muestra a Pidgey y la detección automática reconoce a Rattata
- **THEN** la ficha pasa a mostrar a Rattata

#### Scenario: Ficha ocultada por el usuario
- **WHEN** el usuario oculta la ficha de Stufful y la detección vuelve a reconocer a Stufful
- **THEN** la ficha no vuelve a aparecer

#### Scenario: Sin reconocer
- **WHEN** un reconocimiento automático no identifica ninguna especie
- **THEN** no se muestra ningún aviso

### Requirement: Ocultación al terminar el combate
IF `detection.hide_after_seconds` es mayor que 0, THEN el sistema SHALL ocultar la ficha mostrada cuando la huella de la región lleve ese tiempo distinta de la del último reconocimiento correcto sin que se haya vuelto a reconocer esa especie. Al ocultarla, la especie deja de considerarse mostrada, de modo que el mismo rival en un combate posterior vuelve a mostrarse.

#### Scenario: Fin del combate
- **WHEN** termina el combate y la región muestra el escenario durante 4 s
- **THEN** la ficha se oculta

#### Scenario: Cambio breve durante el combate
- **WHEN** una animación tapa el nombre durante 1 s y después vuelve a reconocerse la misma especie
- **THEN** la ficha no se oculta

#### Scenario: Mismo rival en otro combate
- **WHEN** la ficha de Stufful se ocultó al terminar el combate y empieza otro combate contra Stufful
- **THEN** la ficha vuelve a mostrarse

### Requirement: Activar y desactivar
La detección automática SHALL estar activada por defecto según `detection.enabled` de `config.toml`, y el usuario MUST poder activarla o desactivarla desde la bandeja. El cambio hecho desde la bandeja se recuerda entre sesiones y tiene prioridad sobre `config.toml`.

#### Scenario: Desactivar desde la bandeja
- **WHEN** el usuario desmarca «Detección automática» y reinicia BattleLens
- **THEN** la detección sigue desactivada y solo funciona el atajo manual

