## ADDED Requirements

### Requirement: Estilo visual de la ficha
La ficha SHALL presentar una jerarquía visual clara: una cabecera con el nombre, el número, el nivel (modo Competitivo) y los tipos del Pokémon, seguida de bloques diferenciados por un fondo sutil (Combate, Eficacias, Estadísticas, Habilidades, Movimientos, Datos), con más separación entre bloques que dentro de ellos. El color pleno de tipo MUST reservarse para los tipos del propio Pokémon; en el resto de la ficha, los tipos MUST mostrarse con una pastilla suave (fondo teñido del color del tipo y texto claro) cuyo texto tenga un contraste mínimo de 4,5:1. Los multiplicadores y los veredictos MUST usar colores semánticos coherentes (bueno, malo y neutral para el jugador) en toda la ficha. El estilo MUST NOT cambiar los datos ni los textos que muestra cada modo.

#### Scenario: Tipos destacados
- **WHEN** se muestra Stufful (Normal/Lucha) en modo Competitivo
- **THEN** solo las pastillas Normal y Lucha de la cabecera usan el color pleno, y las de debilidades, resistencias, inmunidades y movimientos usan la variante suave

#### Scenario: Multiplicadores con significado
- **WHEN** la ficha de Zigzagoon de Galar muestra Lucha ×4 en debilidades y Fantasma ×0 en inmunidades
- **THEN** «×4» y «×0» se muestran con colores distintos según su efecto para el jugador, no con el mismo color de acento

#### Scenario: Comparativa destacada
- **WHEN** se muestra Venusaur contra tu Charizard
- **THEN** el bloque «Contra tu Charizard» muestra el veredicto «Ventaja» en el color de ventaja, y cada tipo con su multiplicador como insignia separada

#### Scenario: Contraste de las pastillas suaves
- **WHEN** se genera la pastilla suave de cualquiera de los 18 tipos
- **THEN** el contraste entre su texto y su fondo es de al menos 4,5:1

#### Scenario: Eficacias agrupadas
- **WHEN** se muestra Stufful en modo Competitivo
- **THEN** debilidades, resistencias e inmunidades aparecen dentro de un único bloque «Eficacias»

#### Scenario: Mismo contenido
- **WHEN** se reconoce a Stufful en modo Normal
- **THEN** la tarjeta sigue mostrando «Captura: 140 · Media», sus debilidades, la evolución y el total de estadísticas, sin barras ni habilidades

### Requirement: Bloques plegables
Cada bloque de la ficha (todos salvo la cabecera, incluido «Contra tu X») SHALL poder plegarse y desplegarse con un clic en su título, que muestra una flecha con su estado. Un bloque plegado MUST mostrar solo su fila de título; en «Contra tu X», esa fila incluye el veredicto. Las secciones plegadas MUST guardarse por modo de ficha en `state.json` (`collapsed_sections`) y aplicarse a todas las tarjetas visibles y a las fichas siguientes. Al plegar o desplegar, la ficha MUST ajustar su altura sin moverse de su posición.

#### Scenario: Plegar habilidades
- **WHEN** en modo Competitivo el usuario hace clic en el título «Habilidades»
- **THEN** el bloque se reduce a su título, la ficha sigue visible y la siguiente ficha competitiva aparece con «Habilidades» plegado

#### Scenario: Plegado por modo
- **WHEN** «Habilidades» está plegado en modo Competitivo y el usuario cambia a modo Normal y vuelve
- **THEN** en Normal no hay nada plegado y, al volver a Competitivo, «Habilidades» sigue plegado

#### Scenario: Combate doble
- **WHEN** se muestran Pidgey y Rattata y el usuario pliega «Eficacias» en la tarjeta de Pidgey
- **THEN** «Eficacias» queda plegado en las dos tarjetas

#### Scenario: Veredicto con el bloque plegado
- **WHEN** el usuario pliega «Contra tu Charizard» en la ficha de Venusaur
- **THEN** el título sigue mostrando el veredicto «Ventaja»

#### Scenario: Foco preservado al plegar
- **WHEN** el emulador tiene el foco y el usuario pliega un bloque
- **THEN** las pulsaciones de teclado siguen llegando al emulador

## MODIFIED Requirements

### Requirement: Ocultación del overlay
El sistema SHALL ocultar el overlay al pulsar el atajo de ocultar, al hacer clic en él fuera del título de un bloque o, si está configurado, tras un tiempo (por defecto desactivado). El clic en el título de un bloque MUST plegarlo o desplegarlo sin ocultar el overlay. Un nuevo reconocimiento MUST reemplazar el contenido del overlay visible.

#### Scenario: Nuevo rival
- **WHEN** el overlay muestra a Pidgey y se reconoce a Rattata
- **THEN** el overlay pasa a mostrar a Rattata sin abrir una segunda ventana

#### Scenario: Clic en el título
- **WHEN** el usuario hace clic en el título «Eficacias»
- **THEN** el bloque se pliega y el overlay sigue visible

#### Scenario: Clic fuera de los títulos
- **WHEN** el usuario hace clic en una pastilla de tipo de la ficha
- **THEN** el overlay se oculta
