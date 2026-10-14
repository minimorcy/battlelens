## MODIFIED Requirements

### Requirement: Coincidencia aproximada multilingüe
El sistema SHALL comparar con los nombres normalizados de todas las especies en inglés, español, francés, alemán e italiano los siguientes candidatos: el texto completo normalizado; si hay varias palabras, cada palabra y cada par de palabras contiguas de 4 o más caracteres (con una penalización de 5 puntos); y cada candidato de 6 o más caracteres sin sus 1-2 últimos caracteres (con una penalización de 2 puntos por carácter), para absorber símbolos de género leídos como letras. Cada candidato SHALL compararse también con las letras que el OCR confunde en las fuentes pixeladas unificadas («A» con «R» y «D» con «O»), con una penalización de 3 puntos. El sistema MUST devolver la especie con mayor puntuación penalizada (0–100) junto a esa puntuación.

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

#### Scenario: Letras confundidas en una fuente pixelada
- **WHEN** el OCR devuelve "RRTTRTR" o "CHRRIZRRD" (la «A» de la fuente de GBA leída como «R»)
- **THEN** se resuelven a Rattata (#19) y Charizard (#6) con puntuación 97
