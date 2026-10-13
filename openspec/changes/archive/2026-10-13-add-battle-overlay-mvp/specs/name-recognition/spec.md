## ADDED Requirements

### Requirement: Recorte de la región
El sistema SHALL recortar de la captura la región del perfil activo, convirtiendo las fracciones a píxeles según el tamaño actual de la captura.

#### Scenario: Ventana redimensionada
- **WHEN** el perfil se calibró a 960×640 y la captura actual es de 1440×960
- **THEN** el recorte cubre la misma zona relativa del juego, escalada proporcionalmente

### Requirement: Preprocesado para OCR
El sistema SHALL generar a partir del recorte, en este orden: el recorte original sin procesar; variantes en escala de grises sin binarizar, con la altura normalizada a varios valores (para texto suavizado de juegos 3D y regiones con fondos mezclados); y variantes binarizadas para fuentes pixeladas (escala de grises, binarización con normalización de polaridad a texto oscuro sobre fondo claro y altura normalizada entre 18 y 40 px con vecino más próximo al ampliar, con y sin un desenfoque leve). Todas las variantes procesadas MUST llevar margen blanco.

#### Scenario: Texto claro sobre fondo oscuro
- **WHEN** el recorte contiene texto blanco sobre fondo oscuro
- **THEN** las variantes binarizadas contienen texto negro sobre fondo blanco

#### Scenario: Recorte de cualquier tamaño
- **WHEN** el recorte mide 16 px o 120 px de alto
- **THEN** cada variante binarizada tiene la altura normalizada a su valor objetivo y las que no llevan desenfoque conservan los bordes nítidos (solo valores 0 y 255)

#### Scenario: Región holgada en un juego 3D
- **WHEN** la región calibrada incluye el nombre, el nivel, la barra de PS y parte del fondo del escenario (p. ej. Pokémon Espada)
- **THEN** alguna variante permite reconocer la especie correctamente

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
El sistema SHALL comparar con los nombres normalizados de todas las especies en inglés, español, francés, alemán e italiano los siguientes candidatos: el texto completo normalizado; si hay varias palabras, cada palabra y cada par de palabras contiguas de 4 o más caracteres (con una penalización de 5 puntos); y cada candidato de 6 o más caracteres sin sus 1-2 últimos caracteres (con una penalización de 2 puntos por carácter), para absorber símbolos de género leídos como letras. El sistema MUST devolver la especie con mayor puntuación penalizada (0–100) junto a esa puntuación.

#### Scenario: Error típico de OCR
- **WHEN** el OCR devuelve "P1DGEY"
- **THEN** se resuelve a Pidgey (#16) con puntuación ≥ 80

#### Scenario: Nombre en otro idioma
- **WHEN** el OCR devuelve "SALAMÈCHE" en un juego en francés
- **THEN** se resuelve a Charmander (#4)

#### Scenario: Texto de más alrededor del nombre
- **WHEN** el OCR devuelve "~~ Stufful ##" o "StutfulO" (con el símbolo ♂ leído como «O»)
- **THEN** se resuelve a Stufful (#759) con puntuación ≥ 82

#### Scenario: Palabra corta suelta
- **WHEN** el OCR devuelve "PII NG"
- **THEN** el resultado es "no reconocido": la palabra "PII" (nombre alemán de Cleffa) es demasiado corta para considerarse por separado

#### Scenario: Puntuación insuficiente
- **WHEN** la mejor coincidencia tiene una puntuación inferior al umbral
- **THEN** el resultado es "no reconocido", nunca esa especie

### Requirement: Umbral de confianza
El sistema SHALL considerar reconocido un resultado solo si su puntuación es ≥ 80 (configurable) y MUST informar de "no reconocido" incluyendo el texto leído cuando no lo sea.

#### Scenario: Texto irreconocible
- **WHEN** el OCR devuelve "~~ ##" o una cadena vacía
- **THEN** el resultado es "no reconocido" y el overlay muestra el texto leído para ayudar a recalibrar

### Requirement: Volcado de depuración
WHERE el modo depuración está activado en la configuración, el sistema SHALL guardar en `%APPDATA%\BattleLens\debug\` el recorte original, la imagen preprocesada y un JSON con el texto OCR, el candidato y la puntuación de cada reconocimiento.

#### Scenario: Depuración activa
- **WHEN** el modo depuración está activado y se ejecuta un reconocimiento
- **THEN** se crean los tres archivos con la misma marca de tiempo

### Requirement: Rendimiento
El sistema SHALL completar el ciclo captura → recorte → OCR → coincidencia en menos de 500 ms en un equipo de sobremesa típico.

#### Scenario: Reconocimiento bajo demanda
- **WHEN** el usuario pulsa el atajo de reconocimiento
- **THEN** el overlay muestra el resultado en menos de 500 ms desde la pulsación
