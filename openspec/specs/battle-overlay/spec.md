# battle-overlay Specification

## Purpose
Interfaz de BattleLens durante el juego: atajos globales, ficha superpuesta del Pokémon rival, icono en la bandeja e instancia única.
## Requirements
### Requirement: Atajos de teclado globales
El sistema SHALL registrar atajos de teclado globales que funcionen aunque el emulador tenga el foco: reconocer (por defecto `Ctrl+Alt+P`), calibrar (por defecto `Ctrl+Alt+C`) y ocultar el overlay (por defecto `Ctrl+Alt+H`). Los atajos MUST ser configurables en `config.toml` y MUST NOT usar teclas F sin modificador, porque los emuladores las usan para los estados guardados.

#### Scenario: Reconocimiento con el emulador en primer plano
- **WHEN** el emulador tiene el foco y el usuario pulsa `Ctrl+Alt+P`
- **THEN** se ejecuta el reconocimiento y el emulador no recibe ninguna acción adicional

#### Scenario: Atajo ocupado
- **WHEN** otra aplicación ya tiene registrado el mismo atajo
- **THEN** el sistema muestra un aviso en la bandeja indicando qué atajo no se pudo registrar y sigue funcionando con el resto

### Requirement: Overlay con la ficha del Pokémon
WHEN un reconocimiento identifica al menos a un rival, el sistema SHALL mostrar una ventana superpuesta con una tarjeta por cada rival identificado (dos tarjetas una al lado de la otra en combates dobles). Cada tarjeta muestra la vista de la especie para el juego del perfil activo: nombre (incluida la forma, p. ej. «Zigzagoon de Galar») en el idioma de la interfaz, número de Pokédex, tipos, debilidades agrupadas (×4, ×2), resistencias (×½, ×¼), inmunidades (×0) según la tabla de la generación del juego, estadísticas base con barras y total, habilidades marcando la oculta (cuando existan en esa generación) y, si la especie tiene otras formas regionales, una línea «Otras formas» con su nombre y tipos. Si además se identifica tu Pokémon, cada tarjeta MUST incluir el apartado «Contra tu <nombre>» con tus ataques, sus ataques y el veredicto.

#### Scenario: Ficha mostrada
- **WHEN** se reconoce Charizard
- **THEN** el overlay muestra todos los campos anteriores con los valores del dataset

#### Scenario: Forma regional
- **WHEN** se reconoce Zigzagoon con un perfil de Pokémon Espada
- **THEN** el overlay muestra «Zigzagoon de Galar», Siniestro/Normal, Lucha en ×4, y en «Otras formas» Zigzagoon (Normal)

#### Scenario: Combate doble
- **WHEN** se reconocen Pidgey como rival y Rattata como 2.º rival
- **THEN** el overlay muestra dos tarjetas, Pidgey y Rattata, una al lado de la otra

#### Scenario: Comparativa con tu Pokémon
- **WHEN** se reconoce Venusaur como rival y Charizard como tu Pokémon
- **THEN** la tarjeta de Venusaur incluye «Contra tu Charizard» con Fuego ×2, Volador ×2, Planta ×¼, Veneno ×1 y el veredicto «Ventaja»

#### Scenario: Resultado no reconocido
- **WHEN** el reconocimiento manual no identifica a ningún rival
- **THEN** el overlay muestra un aviso breve con el texto leído por el OCR y la sugerencia de recalibrar

### Requirement: Comportamiento de la ventana
El overlay SHALL estar siempre por encima del resto de ventanas, sin marco, MUST NOT robar el foco del teclado al emulador y MUST NOT aparecer en la barra de tareas. Se SHALL posicionar por defecto junto al borde derecho de la ventana objetivo, o dentro de la pantalla si no cabe, y MUST recordar la posición si el usuario lo arrastra.

#### Scenario: Foco preservado
- **WHEN** el overlay aparece mientras el usuario juega
- **THEN** las pulsaciones de teclado siguen llegando al emulador

#### Scenario: Emulador a pantalla completa en el borde
- **WHEN** la ventana objetivo ocupa toda la pantalla
- **THEN** el overlay se coloca dentro de la pantalla, en la esquina superior derecha

### Requirement: Ocultación del overlay
El sistema SHALL ocultar el overlay al pulsar el atajo de ocultar, al hacer clic en él o, si está configurado, tras un tiempo (por defecto desactivado). Un nuevo reconocimiento MUST reemplazar el contenido del overlay visible.

#### Scenario: Nuevo rival
- **WHEN** el overlay muestra a Pidgey y se reconoce a Rattata
- **THEN** el overlay pasa a mostrar a Rattata sin abrir una segunda ventana

### Requirement: Icono en la bandeja del sistema
El sistema SHALL mostrar un icono en la bandeja del sistema con un menú para: reconocer ahora, activar o desactivar la detección automática, seleccionar ventana objetivo, seleccionar perfil activo, cambiar el juego del perfil activo, gestionar las regiones del perfil activo (recalibrar el rival; calibrar o quitar el 2.º rival; calibrar o quitar tu Pokémon), calibrar un perfil nuevo, eliminar el perfil activo, abrir la carpeta de datos y salir.

#### Scenario: Salida limpia
- **WHEN** el usuario elige "Salir"
- **THEN** se liberan los atajos globales, se detiene la detección automática, se guarda la configuración y el proceso termina

#### Scenario: Estado de la detección visible
- **WHEN** el usuario abre el menú de la bandeja
- **THEN** «Detección automática» aparece marcada si está activada

#### Scenario: Regiones disponibles
- **WHEN** el perfil activo no tiene región del 2.º rival
- **THEN** el submenú «Regiones del perfil» ofrece «Calibrar 2.º rival…» y no ofrece «Quitar 2.º rival»

### Requirement: Instancia única
El sistema SHALL impedir que se ejecuten dos instancias a la vez.

#### Scenario: Segundo arranque
- **WHEN** se lanza la aplicación con otra instancia ya en ejecución
- **THEN** la segunda instancia muestra un aviso y termina sin registrar atajos

