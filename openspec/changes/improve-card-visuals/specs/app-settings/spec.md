## ADDED Requirements

### Requirement: Desplegar todas las secciones
Ajustes SHALL ofrecer el botón «Desplegar todas las secciones», que vacía las secciones plegadas de los dos modos (`collapsed_sections` en `state.json`) y, si hay una ficha visible, la vuelve a dibujar con todos sus bloques desplegados.

#### Scenario: Restablecer
- **WHEN** «Habilidades» y «Entrenamiento» están plegados y el usuario pulsa «Desplegar todas las secciones»
- **THEN** la siguiente ficha competitiva muestra todos sus bloques desplegados
