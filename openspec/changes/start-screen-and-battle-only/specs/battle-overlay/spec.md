## ADDED Requirements

### Requirement: Pantalla de inicio
Al abrir la aplicación, si `interface.start_screen` está activo (por defecto), el sistema SHALL mostrar una pantalla de inicio para elegir la ventana del emulador, el perfil, el modo de la ficha y si la detección automática está activa, con los valores actuales ya seleccionados. La ventana elegida MUST aplicarse al momento (y con ella el perfil de su juego, si existe). La pantalla SHALL ofrecer «Nuevo perfil con un preset…» y, al terminar el asistente, mostrar el perfil creado. Al pulsar «Empezar», el sistema MUST aplicar el perfil, el modo y la detección elegidos, y guardar si la pantalla se muestra al abrir la app.

#### Scenario: Arranque
- **WHEN** el usuario abre la aplicación con la configuración por defecto
- **THEN** aparece la pantalla de inicio con la ventana del emulador y el perfil activo seleccionados

#### Scenario: Empezar
- **WHEN** el usuario elige otro perfil y el modo Competitivo y pulsa «Empezar»
- **THEN** ese perfil queda activo y la ficha pasa a modo Competitivo

#### Scenario: No volver a mostrarla
- **WHEN** el usuario desactiva «Mostrar al abrir la app» y pulsa «Empezar»
- **THEN** `interface.start_screen` se guarda como `false` y la pantalla no aparece en el siguiente arranque
