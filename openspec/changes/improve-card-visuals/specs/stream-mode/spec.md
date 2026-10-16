## ADDED Requirements

### Requirement: Estilo de la ficha del stream
La ficha del stream SHALL seguir el mismo estilo visual que la ficha privada (spec `battle-overlay`, «Estilo visual de la ficha»): cabecera con los tipos en color pleno, bloques con fondo sutil, pastillas suaves en el resto de tipos y los mismos colores semánticos para multiplicadores y veredictos.

#### Scenario: Ficha del stream coherente
- **WHEN** el modo stream muestra a Machop contra tu Scorbunny
- **THEN** la pastilla Lucha de la cabecera es sólida, las debilidades usan pastillas suaves y el veredicto usa el mismo color que en la ficha privada
