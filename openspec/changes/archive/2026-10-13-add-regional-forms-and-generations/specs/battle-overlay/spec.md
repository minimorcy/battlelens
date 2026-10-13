## MODIFIED Requirements

### Requirement: Overlay con la ficha del Pokémon
WHEN un reconocimiento tiene éxito, el sistema SHALL mostrar una ventana superpuesta con la vista de la especie para el juego del perfil activo: nombre (incluida la forma, p. ej. «Zigzagoon de Galar») en el idioma de la interfaz, número de Pokédex, tipos, debilidades agrupadas (×4, ×2), resistencias (×½, ×¼), inmunidades (×0) según la tabla de la generación del juego, estadísticas base con barras y total, habilidades marcando la oculta (cuando existan en esa generación) y, si la especie tiene otras formas regionales, una línea «Otras formas» con su nombre y tipos.

#### Scenario: Ficha mostrada
- **WHEN** se reconoce Charizard
- **THEN** el overlay muestra todos los campos anteriores con los valores del dataset

#### Scenario: Forma regional
- **WHEN** se reconoce Zigzagoon con un perfil de Pokémon Espada
- **THEN** el overlay muestra «Zigzagoon de Galar», Siniestro/Normal, Lucha en ×4, y en «Otras formas» Zigzagoon (Normal)

#### Scenario: Resultado no reconocido
- **WHEN** el reconocimiento devuelve "no reconocido"
- **THEN** el overlay muestra un aviso breve con el texto leído por el OCR y la sugerencia de recalibrar

### Requirement: Icono en la bandeja del sistema
El sistema SHALL mostrar un icono en la bandeja del sistema con un menú para: seleccionar ventana objetivo, seleccionar perfil activo, cambiar el juego del perfil activo, calibrar, recalibrar o eliminar el perfil activo, abrir la carpeta de datos y salir.

#### Scenario: Salida limpia
- **WHEN** el usuario elige "Salir"
- **THEN** se liberan los atajos globales, se guarda la configuración y el proceso termina
