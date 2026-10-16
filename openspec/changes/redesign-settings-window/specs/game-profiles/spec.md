## MODIFIED Requirements

### Requirement: Perfil activo
El sistema SHALL mantener exactamente un perfil activo cuando exista al menos un perfil, MUST permitir cambiarlo desde la bandeja del sistema y desde Ajustes › Perfiles, y MUST recordar el último perfil activo entre ejecuciones.

#### Scenario: Cambio de perfil
- **WHEN** el usuario selecciona otro perfil en el menú de la bandeja
- **THEN** los siguientes reconocimientos usan la región de ese perfil

#### Scenario: Cambio de perfil desde Ajustes
- **WHEN** el usuario selecciona otro perfil en la lista de Ajustes › Perfiles
- **THEN** los siguientes reconocimientos usan la región de ese perfil y la bandeja lo marca como activo

#### Scenario: Sin perfiles
- **WHEN** no existe ningún perfil y el usuario lanza un reconocimiento
- **THEN** el sistema indica que hay que calibrar primero

### Requirement: Cambiar el juego de un perfil
El sistema SHALL permitir cambiar el juego del perfil activo desde Ajustes › Perfiles, incluida la opción «Sin especificar».

#### Scenario: Asignar juego a un perfil antiguo
- **WHEN** el usuario elige «Espada / Escudo» como juego del perfil activo en Ajustes › Perfiles
- **THEN** el perfil se guarda con ese juego y las siguientes fichas usan las formas de Galar
