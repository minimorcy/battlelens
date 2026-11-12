## ADDED Requirements

### Requirement: Atajo y opción de bandeja para buscar
El sistema SHALL ofrecer el atajo global «Buscar Pokémon» (por defecto `Ctrl+Alt+B`, configurable en `hotkeys.search` y en *Ajustes → Atajos*, con las mismas reglas de validación que el resto de atajos) y la opción «Buscar Pokémon…» en la bandeja, con la pista del atajo. Ambos SHALL abrir el buscador. Mientras el buscador está abierto, la detección automática MUST quedar en pausa y el atajo MUST traerlo al frente en lugar de abrir otro.

#### Scenario: Abrir con el atajo
- **WHEN** el usuario pulsa `Ctrl+Alt+B` con el emulador en primer plano
- **THEN** aparece el buscador, siempre encima y con el foco en el campo de texto

#### Scenario: Atajo con el buscador ya abierto
- **WHEN** el usuario pulsa `Ctrl+Alt+B` con el buscador abierto
- **THEN** no se abre otro: el mismo buscador pasa al frente

#### Scenario: Atajo personalizado
- **WHEN** el usuario cambia el atajo a `Ctrl+Shift+K` en Ajustes y guarda
- **THEN** `Ctrl+Shift+K` abre el buscador, se guarda `hotkeys.search` y la bandeja muestra la nueva pista

### Requirement: Buscar por nombre
El buscador SHALL sugerir, mientras se escribe, los nombres en el idioma de la interfaz que contengan el texto, sin distinguir mayúsculas, con una sugerencia por cada forma disponible en el juego del perfil activo (la base, las regionales, las megaevoluciones donde existan y las demás formas; sin perfil, todas). Cada sugerencia SHALL mostrar a la derecha del nombre los tipos de esa forma en ese juego (o, sin perfil, en la generación actual) como píldoras con el color de cada tipo. Elegir una sugerencia, o escribir su nombre exacto, SHALL abrir la ficha con esa forma. Cualquier otro texto SHALL resolverse con el emparejador aproximado de nombres (con la forma automática del juego), así que MUST aceptar nombres en cualquiera de los idiomas del índice, sin tildes y con pequeñas erratas. Si no se reconoce ninguna especie, el buscador MUST seguir abierto con un aviso. `Esc` SHALL cerrarlo sin hacer nada.

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

### Requirement: Ficha del Pokémon buscado
Al resolver la búsqueda, el sistema SHALL mostrar la ficha de esa especie con el juego del perfil activo o, si no hay perfil, con los datos de la generación actual. La ficha SHALL aparecer sobre la ventana del emulador si hay una seleccionada y, si no, en la pantalla principal. La ficha buscada SHALL admitir el cambio de forma y de modo como una ficha de combate, y MUST NOT publicarse en la ficha del stream. Si la detección automática muestra después un rival, su ficha SHALL sustituir a la buscada como siempre.

#### Scenario: Con perfil activo
- **WHEN** el perfil activo es de Pokémon Rojo Fuego y el usuario busca Clefairy
- **THEN** la ficha muestra a Clefairy con los tipos y stats de la generación 3

#### Scenario: Sin ventana del emulador
- **WHEN** no hay ninguna ventana seleccionada y el usuario busca Rotom
- **THEN** la ficha aparece en la pantalla principal y `Ctrl+Alt+F` alterna sus formas

#### Scenario: Modo stream activo
- **WHEN** el modo stream está activo y el usuario busca un Pokémon
- **THEN** la ficha del stream no cambia
