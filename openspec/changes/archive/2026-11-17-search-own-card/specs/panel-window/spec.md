## MODIFIED Requirements

### Requirement: Ventana del panel
En modo Panel, el sistema SHALL mostrar una ventana normal de Windows con marco, título «BattleLens», que se puede redimensionar y que no está «siempre encima». Se organiza en tres columnas: a la izquierda la ficha del rival (o las dos de un combate doble); en el centro la tabla de tipos de la generación del perfil activo, con los tipos del rival y los tuyos resaltados, y la tabla de naturalezas, escaladas para aprovechar el espacio libre; a la derecha el buscador y, debajo, la ficha buscada. Las fichas MUST desplazarse verticalmente si no caben y conservar el plegado de secciones con un clic en el título. Sin posición guardada, el panel SHALL abrirse con un tamaño que deje sitio a dos fichas y a la tabla.

#### Scenario: Combate en modo Panel
- **WHEN** se reconoce a Stufful con el modo Panel activo
- **THEN** el panel muestra la ficha de Stufful a la izquierda, la tabla de tipos en el centro con las columnas Normal y Lucha resaltadas y el buscador a la derecha

#### Scenario: Ficha buscada en el panel
- **WHEN** con la ficha de Stufful en el panel, el usuario busca Rotom
- **THEN** la ficha de Rotom aparece en la columna derecha, debajo del buscador, y la de Stufful sigue a la izquierda

#### Scenario: Redimensionar
- **WHEN** el usuario agranda la ventana del panel
- **THEN** las tablas crecen hasta llenar la columna central, sin pasar de su escala máxima

### Requirement: Panel sin combate
Cuando no hay ficha del rival (fin del combate, ✕, atajo de ocultar o temporizador), el panel SHALL seguir abierto y mostrar «Esperando combate…» en el hueco de la ficha. Además, la tabla de tipos MUST quitar el resaltado. El buscador y la ficha buscada MUST seguir como estaban.

#### Scenario: Fin del combate
- **WHEN** termina el combate con el panel abierto
- **THEN** la ficha del rival desaparece, se ve «Esperando combate…», la tabla sigue visible sin resaltado y el buscador sigue disponible
