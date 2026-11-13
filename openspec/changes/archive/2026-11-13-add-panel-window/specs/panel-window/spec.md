## ADDED Requirements

### Requirement: Elegir dónde se muestra la ficha
El sistema SHALL ofrecer en Ajustes › Ficha la opción «Mostrar la ficha en» con dos valores: **Overlay** (por defecto, ventanas flotantes sobre el juego) y **Panel** (una ventana normal). Se guarda en `config.toml` (`overlay.display`) y MUST aplicarse al momento, sin reiniciar.

#### Scenario: Valor por defecto
- **WHEN** se arranca por primera vez
- **THEN** la ficha se muestra como overlay

#### Scenario: Cambio en caliente
- **WHEN** el usuario elige «Panel» en Ajustes y guarda
- **THEN** la ficha y la tabla de tipos dejan de flotar sobre el juego y pasan a la ventana del panel

#### Scenario: Valor no válido
- **WHEN** `config.toml` tiene `display = "otro"`
- **THEN** se informa del error de configuración como con el resto de claves

### Requirement: Ventana del panel
En modo Panel, el sistema SHALL mostrar una ventana normal de Windows con marco, título «BattleLens», que se puede redimensionar y que no está «siempre encima». Contiene a la izquierda la ficha (o las dos de un combate doble) y a la derecha la tabla de tipos de la generación del perfil activo, con los tipos del rival y los tuyos resaltados y escalada para aprovechar el espacio libre. La ficha MUST desplazarse verticalmente si no cabe y conservar el plegado de secciones con un clic en el título.

#### Scenario: Combate en modo Panel
- **WHEN** se reconoce a Stufful con el modo Panel activo
- **THEN** el panel muestra la ficha de Stufful a la izquierda y la tabla de tipos a la derecha con las columnas Normal y Lucha resaltadas

#### Scenario: Redimensionar
- **WHEN** el usuario agranda la ventana del panel
- **THEN** la tabla de tipos crece hasta llenar el espacio libre, sin pasar de su escala máxima

### Requirement: Panel sin combate
Cuando no hay ficha (fin del combate, ✕, atajo de ocultar o temporizador), el panel SHALL seguir abierto y mostrar «Esperando combate…» en el hueco de la ficha. Además, la tabla de tipos MUST quitar el resaltado.

#### Scenario: Fin del combate
- **WHEN** termina el combate con el panel abierto
- **THEN** la ficha desaparece, se ve «Esperando combate…» y la tabla sigue visible sin resaltado

### Requirement: Abrir y cerrar el panel
El panel SHALL aparecer, sin quitar el foco al juego, al mostrarse una ficha o al activar el modo Panel. Si se cierra con la ✕ del marco, solo se oculta y MUST reaparecer con la siguiente ficha o con «Mostrar el panel» en la bandeja. Esa opción solo aparece en modo Panel.

#### Scenario: Reabrir desde la bandeja
- **WHEN** el usuario ha cerrado el panel y pulsa «Mostrar el panel» en la bandeja
- **THEN** el panel vuelve a abrirse donde estaba

### Requirement: Recordar posición y tamaño
El sistema SHALL guardar la posición y el tamaño del panel en `state.json` y MUST restaurarlos al volver a abrirlo, recolocándolo en una pantalla existente si el monitor guardado ya no está.

#### Scenario: Segunda pantalla
- **WHEN** el usuario deja el panel maximizado en su segundo monitor y reinicia BattleLens
- **THEN** el panel vuelve a abrirse en ese monitor con el mismo tamaño
