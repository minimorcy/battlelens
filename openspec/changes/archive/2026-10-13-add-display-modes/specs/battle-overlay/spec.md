## MODIFIED Requirements

### Requirement: Overlay con la ficha del Pokémon
WHEN un reconocimiento identifica al menos a un rival, el sistema SHALL mostrar una ventana superpuesta con una tarjeta por cada rival identificado (dos tarjetas una al lado de la otra en combates dobles). El contenido de cada tarjeta depende del modo de ficha (spec `display-modes`); la ficha completa muestra la vista de la especie para el juego del perfil activo: nombre (incluida la forma, p. ej. «Zigzagoon de Galar») en el idioma de la interfaz, número de Pokédex, tipos, debilidades agrupadas (×4, ×2), resistencias (×½, ×¼), inmunidades (×0) según la tabla de la generación del juego, estadísticas base con barras y total, habilidades marcando la oculta (cuando existan en esa generación), con su descripción al pasar el ratón, el ratio de captura con su dificultad, la cadena evolutiva (si la especie evoluciona) y, si la especie tiene otras formas regionales, una línea «Otras formas» con su nombre y tipos. Si además se identifica tu Pokémon, cada tarjeta MUST incluir el apartado «Contra tu <nombre>» con tus ataques, sus ataques y el veredicto.

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

#### Scenario: Datos adicionales
- **WHEN** se reconoce Stufful sin juego asignado
- **THEN** la tarjeta muestra «Captura: 140 · Media», la evolución «Stufful → Bewear (Nv. 27)» y, al pasar el ratón por «Peluche», su descripción

### Requirement: Atajos de teclado globales
El sistema SHALL registrar atajos de teclado globales que funcionen aunque el emulador tenga el foco: reconocer (por defecto `Ctrl+Alt+P`), calibrar (por defecto `Ctrl+Alt+C`) ocultar el overlay (por defecto `Ctrl+Alt+H`) y cambiar el modo de la ficha (por defecto `Ctrl+Alt+M`). Los atajos MUST ser configurables en `config.toml` y MUST NOT usar teclas F sin modificador, porque los emuladores las usan para los estados guardados.

#### Scenario: Reconocimiento con el emulador en primer plano
- **WHEN** el emulador tiene el foco y el usuario pulsa `Ctrl+Alt+P`
- **THEN** se ejecuta el reconocimiento y el emulador no recibe ninguna acción adicional

#### Scenario: Atajo ocupado
- **WHEN** otra aplicación ya tiene registrado el mismo atajo
- **THEN** el sistema muestra un aviso en la bandeja indicando qué atajo no se pudo registrar y sigue funcionando con el resto

### Requirement: Icono en la bandeja del sistema
El sistema SHALL mostrar un icono en la bandeja del sistema con un menú para: reconocer ahora, activar o desactivar la detección automática, elegir el modo de la ficha (Normal o Competitivo), seleccionar ventana objetivo, seleccionar perfil activo, cambiar el juego del perfil activo, gestionar las regiones del perfil activo (recalibrar el rival; calibrar o quitar el 2.º rival; calibrar o quitar tu Pokémon), calibrar un perfil nuevo, eliminar el perfil activo, abrir los ajustes, abrir la carpeta de datos, descargar la versión nueva (solo si hay una disponible) y salir.

#### Scenario: Salida limpia
- **WHEN** el usuario elige "Salir"
- **THEN** se liberan los atajos globales, se detiene la detección automática, se guarda la configuración y el proceso termina

#### Scenario: Estado de la detección visible
- **WHEN** el usuario abre el menú de la bandeja
- **THEN** «Detección automática» aparece marcada si está activada

#### Scenario: Regiones disponibles
- **WHEN** el perfil activo no tiene región del 2.º rival
- **THEN** el submenú «Regiones del perfil» ofrece «Calibrar 2.º rival…» y no ofrece «Quitar 2.º rival»
