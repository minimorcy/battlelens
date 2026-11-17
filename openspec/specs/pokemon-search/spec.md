# pokemon-search Specification

## Purpose
Buscador de Pokémon con atajo global y ficha a demanda de cualquier especie y forma, fuera del combate.
## Requirements
### Requirement: Atajo y opción de bandeja para buscar
El sistema SHALL ofrecer el atajo global «Buscar Pokémon» (por defecto `Ctrl+Alt+B`, configurable en `hotkeys.search` y en *Ajustes → Atajos*, con las mismas reglas de validación que el resto de atajos) y la opción «Buscar Pokémon…» en la bandeja, con la pista del atajo. En modo overlay ambos SHALL abrir el diálogo del buscador y, si ya está abierto, MUST traerlo al frente en lugar de abrir otro. En modo panel ambos SHALL mostrar el panel delante y poner el foco en su buscador. La detección automática MUST NOT pausarse mientras se busca.

#### Scenario: Abrir con el atajo
- **WHEN** el usuario pulsa `Ctrl+Alt+B` con el emulador en primer plano y el modo overlay
- **THEN** aparece el buscador, siempre encima y con el foco en el campo de texto

#### Scenario: Atajo con el buscador ya abierto
- **WHEN** el usuario pulsa `Ctrl+Alt+B` con el buscador abierto
- **THEN** no se abre otro: el mismo buscador pasa al frente

#### Scenario: Atajo en modo panel
- **WHEN** el usuario pulsa `Ctrl+Alt+B` con el modo panel activo
- **THEN** el panel pasa al frente con el foco en su buscador y no se abre ningún diálogo

#### Scenario: La detección sigue mientras se busca
- **WHEN** el buscador está abierto y la detección automática reconoce a un rival
- **THEN** se muestra la ficha del rival sin cerrar el buscador

#### Scenario: Atajo personalizado
- **WHEN** el usuario cambia el atajo a `Ctrl+Shift+K` en Ajustes y guarda
- **THEN** `Ctrl+Shift+K` abre el buscador, se guarda `hotkeys.search` y la bandeja muestra la nueva pista

### Requirement: Buscar por nombre
El buscador SHALL sugerir, mientras se escribe, los nombres en el idioma de la interfaz que contengan el texto, sin distinguir mayúsculas, con una sugerencia por cada forma disponible en el juego del perfil activo (la base, las regionales, las megaevoluciones donde existan y las demás formas; sin perfil, todas). Cada sugerencia SHALL mostrar a la derecha del nombre los tipos de esa forma en ese juego (o, sin perfil, en la generación actual) como píldoras con el color de cada tipo. Elegir una sugerencia, o escribir su nombre exacto, SHALL abrir la ficha con esa forma. Cualquier otro texto SHALL resolverse con el emparejador aproximado de nombres (con la forma automática del juego), así que MUST aceptar nombres en cualquiera de los idiomas del índice, sin tildes y con pequeñas erratas. Si no se reconoce ninguna especie, el buscador MUST seguir abierto con un aviso. En el diálogo, `Esc` SHALL cerrarlo sin hacer nada; en el panel, `Esc` SHALL vaciar el campo. Las sugerencias SHALL actualizarse al cambiar de perfil o de idioma.

#### Scenario: Sugerencias
- **WHEN** el usuario escribe «saur» con la interfaz en español
- **THEN** se sugieren Bulbasaur, Ivysaur y Venusaur, cada uno con las píldoras Planta y Veneno

#### Scenario: Una sugerencia por forma
- **WHEN** el perfil activo es de Pokémon Espada y el usuario escribe «Rapidash»
- **THEN** se sugieren «Rapidash» (Fuego) y «Rapidash de Galar» (Psíquico y Hada), y elegir cualquiera abre la ficha de esa forma

#### Scenario: Formas que no existen en el juego
- **WHEN** el perfil activo es de Pokémon Espada y el usuario escribe «Charizard»
- **THEN** no se sugiere ninguna megaevolución

#### Scenario: Nombre sin tilde o en otro idioma
- **WHEN** el usuario escribe «flabebe» o «Bisaflor» y pulsa Enter
- **THEN** se muestra la ficha de Flabébé o de Venusaur

#### Scenario: Texto sin coincidencia
- **WHEN** el usuario escribe «xyzzy» y pulsa Enter
- **THEN** el buscador sigue abierto e indica que no ha encontrado ese Pokémon

#### Scenario: Cambio de perfil con el panel abierto
- **WHEN** el modo panel está activo y el perfil pasa de Pokémon Rojo Fuego a Pokémon Espada
- **THEN** el buscador del panel sugiere ya «Rapidash de Galar»

### Requirement: Ficha del Pokémon buscado
Al resolver la búsqueda, el sistema SHALL mostrar la ficha de esa especie con el juego del perfil activo o, si no hay perfil, con los datos de la generación actual, en una **ficha propia, distinta de la del rival**. Las dos fichas MUST poder verse a la vez: una búsqueda MUST NOT cambiar la ficha del rival, y la detección automática MUST NOT cambiar ni ocultar la ficha buscada. Una búsqueda nueva SHALL sustituir a la ficha buscada anterior. La ficha buscada SHALL ocultarse solo con su ✕; el fin del combate, el atajo de ocultar y el temporizador MUST NOT ocultarla. SHALL cambiar de forma con sus flechas ◀ ▶ (el atajo de cambiar forma actúa solo sobre el rival), SHALL seguir el modo de ficha (normal o competitivo) y MUST NOT publicarse en la ficha del stream.

En modo overlay, la ficha buscada SHALL aparecer en una ventana flotante propia sobre la ventana del emulador si hay una seleccionada y, si no, en la pantalla principal; se puede arrastrar y su posición SHALL guardarse en `state.json` aparte de la de la ficha del rival. En modo panel SHALL aparecer en la columna del buscador, debajo del campo.

#### Scenario: Con perfil activo
- **WHEN** el perfil activo es de Pokémon Rojo Fuego y el usuario busca Clefairy
- **THEN** la ficha buscada muestra a Clefairy con los tipos y stats de la generación 3

#### Scenario: Buscar durante un combate
- **WHEN** se ve la ficha del rival Stufful y el usuario busca Rotom
- **THEN** las fichas de Stufful y de Rotom se ven a la vez

#### Scenario: Llega un rival con la ficha buscada abierta
- **WHEN** se ve la ficha buscada de Rotom y la detección reconoce a Stufful
- **THEN** aparece la ficha de Stufful y la de Rotom sigue igual

#### Scenario: Fin del combate
- **WHEN** termina el combate con la ficha buscada visible
- **THEN** se oculta la ficha del rival y la buscada sigue visible

#### Scenario: Formas de la ficha buscada
- **WHEN** se ven el rival Stufful y la ficha buscada de Rotom, y el usuario pulsa ▶ en la ficha de Rotom
- **THEN** Rotom pasa a su siguiente forma y la ficha de Stufful no cambia

#### Scenario: Posición recordada en modo overlay
- **WHEN** el usuario arrastra la ficha buscada a otro sitio, la cierra y busca otro Pokémon
- **THEN** la nueva ficha buscada aparece donde la dejó, sin mover la ficha del rival

#### Scenario: Modo stream activo
- **WHEN** el modo stream está activo y el usuario busca un Pokémon
- **THEN** la ficha del stream no cambia

### Requirement: Buscador en el panel
En modo panel, el buscador SHALL estar siempre visible arriba de la columna derecha del panel, con el mismo campo, sugerencias y resolución que el diálogo. Al resolver una búsqueda, el campo SHALL vaciarse y la ficha buscada SHALL aparecer debajo. Sin ficha buscada, ese hueco SHALL quedar vacío.

#### Scenario: Buscar desde el panel
- **WHEN** el modo panel está activo y el usuario escribe «Clefairy» en el buscador del panel y pulsa Enter
- **THEN** la ficha de Clefairy aparece debajo del buscador, el campo se vacía y la ficha del rival no cambia

#### Scenario: Cerrar la ficha buscada en el panel
- **WHEN** el usuario pulsa la ✕ de la ficha buscada en el panel
- **THEN** la ficha desaparece y el buscador sigue visible

