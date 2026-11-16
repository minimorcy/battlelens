## ADDED Requirements

### Requirement: Imagen del Pokémon en la cabecera
Con `overlay.sprites` activado y el sprite disponible, la cabecera de cada tarjeta SHALL mostrar a la izquierda del nombre el sprite de la forma mostrada, centrado en un recuadro y escalado sin suavizado. Si la imagen llega con la ficha ya visible, MUST colocarse sin mover la ficha. Sin imagen, la cabecera MUST mostrarse sin el recuadro. Al cambiar de forma, la imagen MUST cambiar a la de la nueva forma.

#### Scenario: Forma regional
- **WHEN** se reconoce a Zigzagoon con un perfil de Pokémon Espada y la imagen está en caché
- **THEN** la cabecera muestra el sprite de Zigzagoon de Galar (10174)

#### Scenario: Cambio de forma
- **WHEN** la ficha muestra a Rotom en `platinum` y el usuario pulsa `Ctrl+Alt+F`
- **THEN** la cabecera muestra el sprite de Rotom Calor (o ninguno, si aún no se ha descargado)

#### Scenario: Imágenes desactivadas
- **WHEN** `overlay.sprites = false`
- **THEN** la cabecera no muestra imagen y no se hace ninguna petición de red
