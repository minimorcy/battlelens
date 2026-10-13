# window-capture Specification

## Purpose
Seleccionar la ventana del emulador y obtener su área cliente como imagen, con independencia del emulador usado.
## Requirements
### Requirement: Listado de ventanas candidatas
El sistema SHALL listar las ventanas de nivel superior visibles, con título no vacío y no minimizadas, excluyendo las ventanas propias de la aplicación.

#### Scenario: Emulador abierto
- **WHEN** el usuario abre el selector de ventana con un emulador abierto
- **THEN** la lista incluye la ventana del emulador identificada por su título y su ejecutable

#### Scenario: Ventana minimizada
- **WHEN** el emulador está minimizado
- **THEN** su ventana no aparece en la lista

### Requirement: Selección de ventana objetivo
El sistema SHALL permitir seleccionar una ventana objetivo y MUST recordar el nombre del ejecutable y el título de la última ventana seleccionada para volver a seleccionarla automáticamente en el siguiente arranque si existe una ventana que coincida.

#### Scenario: Reselección automática
- **WHEN** la aplicación arranca y existe una ventana del mismo ejecutable que la última seleccionada
- **THEN** esa ventana queda seleccionada como objetivo sin intervención del usuario

#### Scenario: Ventana anterior ausente
- **WHEN** la aplicación arranca y no existe ninguna ventana que coincida
- **THEN** no hay ventana objetivo y la bandeja del sistema indica que hay que seleccionar una

### Requirement: Captura del área cliente
El sistema SHALL capturar el área cliente de la ventana objetivo (sin bordes ni barra de título) como imagen RGB, en píxeles físicos, teniendo en cuenta el escalado DPI de Windows.

#### Scenario: Captura correcta
- **WHEN** se solicita una captura y la ventana objetivo está visible
- **THEN** se obtiene una imagen cuyas dimensiones coinciden con el área cliente en píxeles físicos

#### Scenario: Ventana tapada por otras
- **WHEN** se solicita una captura y otra ventana tapa total o parcialmente al emulador
- **THEN** la imagen contiene el contenido del emulador, no el de la ventana que lo tapa (PrintWindow con PW_RENDERFULLCONTENT; si devuelve una imagen negra, se recurre a copiar la zona de la pantalla)

#### Scenario: Pantalla con escalado DPI
- **WHEN** Windows tiene un escalado del 150 % y se solicita una captura
- **THEN** la imagen corresponde exactamente al área cliente, sin desplazamiento ni recorte

### Requirement: Errores de captura
El sistema MUST devolver un error tipado, sin cerrar la aplicación, cuando la captura no es posible.

#### Scenario: Ventana cerrada
- **WHEN** se solicita una captura y la ventana objetivo ya no existe
- **THEN** se produce el error "ventana no disponible" y la ventana objetivo se borra

#### Scenario: Ventana minimizada al capturar
- **WHEN** se solicita una captura y la ventana objetivo está minimizada
- **THEN** se produce el error "ventana minimizada" y no se ejecuta el reconocimiento

