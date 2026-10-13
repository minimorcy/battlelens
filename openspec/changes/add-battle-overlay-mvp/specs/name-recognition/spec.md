## ADDED Requirements

### Requirement: Recorte de la región
El sistema SHALL recortar de la captura la región del perfil activo, convirtiendo las fracciones a píxeles según el tamaño actual de la captura.

#### Scenario: Ventana redimensionada
- **WHEN** el perfil se calibró a 960×640 y la captura actual es de 1440×960
- **THEN** el recorte cubre la misma zona relativa del juego, escalada proporcionalmente

### Requirement: Preprocesado para OCR
El sistema SHALL generar a partir del recorte varias variantes preprocesadas: conversión a escala de grises, binarización con normalización de polaridad a texto oscuro sobre fondo claro, normalización de la altura a varios valores entre 20 y 40 px (vecino más próximo al ampliar), con y sin un desenfoque leve, y margen blanco.

#### Scenario: Texto claro sobre fondo oscuro
- **WHEN** el recorte contiene texto blanco sobre fondo oscuro
- **THEN** todas las variantes contienen texto negro sobre fondo blanco

#### Scenario: Recorte de cualquier tamaño
- **WHEN** el recorte mide 16 px o 120 px de alto
- **THEN** cada variante tiene la altura de texto normalizada a su valor objetivo y las variantes sin desenfoque conservan los bordes nítidos (solo valores 0 y 255)

### Requirement: Ejecución del OCR
El sistema SHALL ejecutar el OCR nativo de Windows sobre cada variante con los idiomas del perfil, en orden y quedándose con el primer resultado no vacío de cada variante. Después MUST conservar la lectura cuya coincidencia (ver «Coincidencia aproximada multilingüe») tenga mayor puntuación, y SHALL dejar de probar variantes en cuanto una alcance 100.

#### Scenario: Mejor variante
- **WHEN** las variantes producen las lecturas "~~", "P1DGEY" y "PIDGEY"
- **THEN** el resultado es Pidgey con puntuación 100 y no se evalúan más variantes

#### Scenario: Idioma de OCR no instalado
- **WHEN** ninguno de los idiomas del perfil tiene paquete de OCR instalado en Windows
- **THEN** el sistema muestra un error que indica qué paquete de idioma instalar

### Requirement: Normalización del texto
El sistema SHALL normalizar tanto el texto del OCR como los nombres del dataset: pasar a mayúsculas, eliminar acentos, eliminar indicadores de nivel y símbolos de género separados del nombre por un espacio, eliminar caracteres que no sean letras ni dígitos, y conservar `♂`/`♀` pegados al nombre como `M`/`F` (Nidoran).

#### Scenario: Símbolo de género del combate
- **WHEN** el OCR devuelve "PIDGEY ♂"
- **THEN** se normaliza a "PIDGEY"

#### Scenario: Nidoran
- **WHEN** el OCR devuelve "NIDORAN♀"
- **THEN** se normaliza a "NIDORANF" y se resuelve a Nidoran♀ (#29)

#### Scenario: Nombre con signos
- **WHEN** el OCR devuelve "Farfetch'd" o "FARFETCH D"
- **THEN** ambos se normalizan a "FARFETCHD"

#### Scenario: Prefijos de juego
- **WHEN** el OCR devuelve "PIDGEY Nv5" o "PIDGEY Lv.5"
- **THEN** se eliminan los indicadores de nivel antes de comparar y queda "PIDGEY"

### Requirement: Coincidencia aproximada multilingüe
El sistema SHALL comparar el texto normalizado con los nombres normalizados de todas las especies en inglés, español, francés, alemán e italiano, y MUST devolver la especie con mayor puntuación junto a esa puntuación (0–100).

#### Scenario: Error típico de OCR
- **WHEN** el OCR devuelve "P1DGEY"
- **THEN** se resuelve a Pidgey (#16) con puntuación ≥ 80

#### Scenario: Nombre en otro idioma
- **WHEN** el OCR devuelve "SALAMÈCHE" en un juego en francés
- **THEN** se resuelve a Charmander (#4)

#### Scenario: Puntuación insuficiente
- **WHEN** la mejor coincidencia tiene una puntuación inferior al umbral
- **THEN** el resultado es "no reconocido", nunca esa especie

### Requirement: Umbral de confianza
El sistema SHALL considerar reconocido un resultado solo si su puntuación es ≥ 80 (configurable) y MUST informar de "no reconocido" incluyendo el texto leído cuando no lo sea.

#### Scenario: Texto irreconocible
- **WHEN** el OCR devuelve "~~ ##" o una cadena vacía
- **THEN** el resultado es "no reconocido" y el overlay muestra el texto leído para ayudar a recalibrar

### Requirement: Volcado de depuración
WHERE el modo depuración está activado en la configuración, el sistema SHALL guardar en `%APPDATA%\pokemon-stats-live\debug\` el recorte original, la imagen preprocesada y un JSON con el texto OCR, el candidato y la puntuación de cada reconocimiento.

#### Scenario: Depuración activa
- **WHEN** el modo depuración está activado y se ejecuta un reconocimiento
- **THEN** se crean los tres archivos con la misma marca de tiempo

### Requirement: Rendimiento
El sistema SHALL completar el ciclo captura → recorte → OCR → coincidencia en menos de 500 ms en un equipo de sobremesa típico.

#### Scenario: Reconocimiento bajo demanda
- **WHEN** el usuario pulsa el atajo de reconocimiento
- **THEN** el overlay muestra el resultado en menos de 500 ms desde la pulsación
