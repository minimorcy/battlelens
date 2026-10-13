## MODIFIED Requirements

### Requirement: Overlay con la ficha del Pokémon
WHEN un reconocimiento identifica al menos a un rival, el sistema SHALL mostrar una ventana superpuesta con una tarjeta por cada rival identificado (dos tarjetas una al lado de la otra en combates dobles). Cada tarjeta muestra la vista de la especie para el juego del perfil activo: nombre (incluida la forma, p. ej. «Zigzagoon de Galar») en el idioma de la interfaz, número de Pokédex, tipos, debilidades agrupadas (×4, ×2), resistencias (×½, ×¼), inmunidades (×0) según la tabla de la generación del juego, estadísticas base con barras y total, habilidades marcando la oculta (cuando existan en esa generación), con su descripción al pasar el ratón, el ratio de captura con su dificultad, la cadena evolutiva (si la especie evoluciona) y, si la especie tiene otras formas regionales, una línea «Otras formas» con su nombre y tipos. Si además se identifica tu Pokémon, cada tarjeta MUST incluir el apartado «Contra tu <nombre>» con tus ataques, sus ataques y el veredicto.

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
