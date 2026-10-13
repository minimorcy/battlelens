## MODIFIED Requirements

### Requirement: Recorte de la región
El sistema SHALL recortar de una misma captura cada región configurada en el perfil activo (rival, 2.º rival y tu Pokémon), convirtiendo las fracciones a píxeles según el tamaño actual de la captura, y SHALL leer cada recorte por separado con el mismo procedimiento de preprocesado, OCR y coincidencia.

#### Scenario: Ventana redimensionada
- **WHEN** el perfil se calibró a 960×640 y la captura actual es de 1440×960
- **THEN** el recorte cubre la misma zona relativa del juego, escalada proporcionalmente

#### Scenario: Varias regiones
- **WHEN** el perfil tiene región de rival, de 2.º rival y de tu Pokémon
- **THEN** un único reconocimiento devuelve tres resultados, uno por región, a partir de una sola captura

#### Scenario: Apodo en tu Pokémon
- **WHEN** tu Pokémon tiene un apodo que no coincide con ninguna especie
- **THEN** el resultado de esa región es «no reconocido» y los de los rivales no se ven afectados
