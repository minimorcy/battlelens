## MODIFIED Requirements

### Requirement: Ventana de ajustes
El sistema SHALL ofrecer desde la bandeja una ventana «Ajustes» con navegación lateral por secciones (General, Ficha, Reconocimiento, Atajos, Modo stream, Perfiles y Acerca de) y tema oscuro coherente con la ficha, para editar todos los valores de `config.toml`: idioma de la interfaz (automático, español o inglés) y comprobación de actualizaciones (General); modo de la ficha, idioma de los datos Pokémon y ocultación automática de la ficha (Ficha); umbral de reconocimiento, detección automática (activada, intervalo y ocultación al terminar el combate) y modo depuración (Reconocimiento); atajos de reconocer, calibrar, ocultar, cambiar de modo, cambiar de forma y mostrar u ocultar la ficha del stream (Atajos); y modo stream (activado, puerto entre 1024 y 65535 y modo de su ficha) (Modo stream).

#### Scenario: Abrir con los valores actuales
- **WHEN** el usuario abre «Ajustes…»
- **THEN** cada control muestra el valor vigente de la configuración

#### Scenario: Navegación por secciones
- **WHEN** el usuario elige «Atajos» en la barra lateral
- **THEN** se muestran los seis atajos y la sección queda resaltada

#### Scenario: Atajo de cambiar de forma
- **WHEN** el usuario abre «Ajustes…» con la configuración por defecto
- **THEN** el atajo «Cambiar de forma» muestra `Ctrl+Alt+F`

#### Scenario: Modo stream
- **WHEN** el usuario activa el modo stream en Ajustes, cambia el puerto a 18000 y guarda
- **THEN** el servidor se reinicia en el puerto 18000 sin reiniciar la aplicación

#### Scenario: Idioma de la interfaz
- **WHEN** el usuario abre «Ajustes…» con la configuración por defecto
- **THEN** «Idioma de la interfaz» muestra «Automático (idioma de Windows)» y «Idioma de los datos Pokémon» muestra el de `overlay.language`

### Requirement: Validación
La ventana SHALL validar los valores antes de guardar con las mismas reglas que `config.toml` (atajos con modificador y tecla conocida; rangos numéricos) y MUST NOT guardar si alguno no es válido, indicando cuál junto a su campo y mostrando la sección del primer error.

#### Scenario: Atajo sin modificador
- **WHEN** el usuario escribe «F8» como atajo de reconocer y pulsa Guardar desde otra sección
- **THEN** se muestra la sección Atajos con el error junto a ese campo y no se guarda nada

### Requirement: Guardar y aplicar sin reiniciar
WHEN el usuario guarda, el sistema SHALL reescribir `config.toml` (conservando los comentarios explicativos de la plantilla) y MUST aplicar los cambios sin reiniciar: volver a registrar los atajos, idioma de la ficha, umbral, depuración, ocultación automática y parámetros de la detección. «Guardar» SHALL estar activo solo si hay cambios sin guardar y MUST dejar la ventana abierta; al cerrar con cambios sin guardar, el sistema MUST preguntar si guardarlos, descartarlos o seguir editando.

#### Scenario: Cambio de idioma
- **WHEN** el usuario cambia el idioma a «en» y guarda
- **THEN** la siguiente ficha se muestra en inglés y `config.toml` contiene `language = "en"`

#### Scenario: Cambio de atajo
- **WHEN** el usuario cambia el atajo de reconocer a `Ctrl+Alt+R` y guarda
- **THEN** `Ctrl+Alt+R` reconoce y `Ctrl+Alt+P` deja de estar registrado

#### Scenario: Ida y vuelta
- **WHEN** se guarda una configuración y se vuelve a leer `config.toml`
- **THEN** se obtienen exactamente los mismos valores

#### Scenario: Sin cambios
- **WHEN** el usuario abre «Ajustes…» sin tocar nada
- **THEN** «Guardar» está desactivado

#### Scenario: Cerrar con cambios pendientes
- **WHEN** el usuario cambia el umbral y cierra la ventana
- **THEN** se le pregunta si quiere guardar los cambios, descartarlos o cancelar el cierre

## ADDED Requirements

### Requirement: Ventana única y no modal
La ventana «Ajustes» SHALL ser única y no modal: abrirla con ella ya abierta MUST traerla al frente sin crear otra, la detección automática MUST seguir funcionando mientras está abierta, y los diálogos de calibración que se abran desde ella MUST mostrarse por encima. Los cambios hechos desde la bandeja con la ventana abierta (modo de la ficha, detección automática, modo stream, perfiles y ventana) SHALL reflejarse en ella sin marcarse como cambios pendientes.

#### Scenario: Abrir dos veces
- **WHEN** el usuario elige «Ajustes…» con la ventana ya abierta
- **THEN** se trae al frente la misma ventana, con sus cambios sin guardar intactos

#### Scenario: Cambio desde la bandeja
- **WHEN** con Ajustes abierto el usuario cambia el modo de la ficha a Competitivo desde la bandeja
- **THEN** la sección Ficha muestra «Competitivo» y «Guardar» no se activa por ello

### Requirement: Perfiles en Ajustes
La sección «Perfiles» SHALL permitir, aplicando cada cambio al momento: elegir la ventana del emulador, ver la lista de perfiles y cambiar el activo, cambiar el juego del perfil activo (incluido «Sin especificar»), ver el estado de cada región del perfil activo (rival, 2.º rival, tu Pokémon y menú de ataques), calibrarla o recalibrarla y quitar las opcionales, crear un perfil con un preset o calibrándolo a mano y eliminar el perfil activo con confirmación. La sección MUST indicar que estos cambios no dependen de «Guardar».

#### Scenario: Cambiar el perfil activo
- **WHEN** el usuario selecciona otro perfil en la lista
- **THEN** ese perfil pasa a ser el activo sin pulsar «Guardar»

#### Scenario: Estado de las regiones
- **WHEN** el perfil activo tiene región de tu Pokémon pero no del 2.º rival
- **THEN** «Tu Pokémon» aparece como calibrada con «Recalibrar…» y «Quitar», y «2.º rival» como sin calibrar con «Calibrar…» y sin «Quitar»

#### Scenario: Sin perfiles
- **WHEN** no hay ningún perfil
- **THEN** la sección explica que hay que crear uno y ofrece «Nuevo con un preset…»

### Requirement: Mantenimiento y «Acerca de» en Ajustes
La sección «General» SHALL ofrecer abrir la carpeta de datos, informar de un problema, instalar el OCR de Windows (solo si falta) y descargar la versión nueva (solo si hay una). «Modo stream» SHALL mostrar la URL para OBS con un botón para copiarla, activo solo con el servidor en marcha. «Acerca de» SHALL mostrar versión, enlace al repositorio, licencia, atribución de datos y aviso legal.

#### Scenario: Versión nueva
- **WHEN** hay disponible BattleLens 0.4.0 y el usuario abre General
- **THEN** aparece «Descargar BattleLens 0.4.0…», que abre la página de la Release

#### Scenario: Aviso legal
- **WHEN** el usuario abre «Acerca de»
- **THEN** se muestra el aviso de proyecto de fans no oficial

### Requirement: Ficha a medida
La sección «Ficha» de Ajustes SHALL permitir mostrar u ocultar, por separado en el modo Normal y en el Competitivo, cada sección de la ficha que exista en ese modo (contra tu Pokémon, tus movimientos, eficacias, evolución y otras formas; y en Competitivo también estadísticas, habilidades, movimientos probables y entrenamiento), y SHALL ofrecer «Mostrar todas». La elección MUST guardarse en `config.toml` (`overlay.hidden_normal` y `overlay.hidden_competitive`), MUST aplicarse a la ficha y a la ficha del stream (según el modo de cada una) sin reiniciar, y la cabecera con el nombre, los tipos y la captura MUST mostrarse siempre.

#### Scenario: Ocultar las estadísticas en Competitivo
- **WHEN** el usuario desactiva «Estadísticas» en la columna Competitivo y guarda
- **THEN** la ficha Competitiva deja de mostrar las estadísticas y la Normal no cambia

#### Scenario: La ficha del stream sigue la elección
- **WHEN** «Evolución» está oculta en Normal y la ficha del stream está en modo Normal
- **THEN** la ficha del stream no muestra la evolución

#### Scenario: Sección que no existe en un modo
- **WHEN** el usuario abre la tabla de secciones
- **THEN** «Entrenamiento» no tiene interruptor en la columna Normal

#### Scenario: Ficha por defecto
- **WHEN** se instala BattleLens y no se ha tocado la tabla de secciones
- **THEN** la ficha Normal muestra solo «Eficacias» y la Competitiva «Eficacias» y «Estadísticas», además de la cabecera

#### Scenario: Valor no válido
- **WHEN** `config.toml` contiene `hidden_normal = ["stats"]`
- **THEN** se rechaza la configuración indicando los valores admitidos

