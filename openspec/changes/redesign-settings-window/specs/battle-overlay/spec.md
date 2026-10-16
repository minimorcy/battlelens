## MODIFIED Requirements

### Requirement: Icono en la bandeja del sistema
El sistema SHALL mostrar un icono en la bandeja del sistema con un menú de opciones rápidas para: reconocer ahora, activar o desactivar la detección automática, elegir el modo de la ficha (Normal o Competitivo), activar el modo stream y copiar su URL, seleccionar ventana objetivo, seleccionar perfil activo, gestionar perfiles (abre Ajustes en la sección Perfiles), crear un perfil nuevo con un preset, instalar el OCR de Windows (solo si falta), descargar la versión nueva (solo si hay una disponible), informar de un problema, abrir los ajustes (acción por defecto) y salir. El juego del perfil, sus regiones, la calibración manual de un perfil nuevo, la eliminación de perfiles, la carpeta de datos y «Acerca de» SHALL estar en la ventana «Ajustes». El doble clic en el icono MUST abrir «Ajustes».

#### Scenario: Salida limpia
- **WHEN** el usuario elige "Salir"
- **THEN** se liberan los atajos globales, se detiene la detección automática, se guarda la configuración y el proceso termina

#### Scenario: Estado de la detección visible
- **WHEN** el usuario abre el menú de la bandeja
- **THEN** «Detección automática» aparece marcada si está activada

#### Scenario: Gestionar perfiles
- **WHEN** el usuario elige «Gestionar perfiles…» en el submenú «Perfil activo»
- **THEN** se abre «Ajustes» en la sección Perfiles

#### Scenario: Doble clic en el icono
- **WHEN** el usuario hace doble clic en el icono de la bandeja
- **THEN** se abre «Ajustes»

#### Scenario: Menú corto
- **WHEN** el usuario abre el menú de la bandeja
- **THEN** no aparecen «Regiones del perfil», «Juego del perfil activo», «Eliminar perfil activo…» ni «Acerca de…»

### Requirement: Ocultación del overlay
El sistema SHALL ocultar el overlay al pulsar el atajo de ocultar, al pulsar el botón ✕ de la esquina superior derecha de la ficha (uno solo, en la tarjeta de la derecha en los combates dobles, y también en la ficha «No reconocido») o, si está configurado, tras un tiempo (por defecto desactivado). Un clic en cualquier otro punto de la ficha MUST NOT ocultarla; el clic en el título de un bloque MUST plegarlo o desplegarlo. Un nuevo reconocimiento MUST reemplazar el contenido del overlay visible.

#### Scenario: Nuevo rival
- **WHEN** el overlay muestra a Pidgey y se reconoce a Rattata
- **THEN** el overlay pasa a mostrar a Rattata sin abrir una segunda ventana

#### Scenario: Clic en el título
- **WHEN** el usuario hace clic en el título «Eficacias»
- **THEN** el bloque se pliega y el overlay sigue visible

#### Scenario: Clic fuera del botón
- **WHEN** el usuario hace clic en una pastilla de tipo de la ficha
- **THEN** el overlay sigue visible

#### Scenario: Botón de cerrar
- **WHEN** el usuario pulsa ✕ en la ficha
- **THEN** el overlay se oculta y la detección automática no lo vuelve a mostrar hasta el siguiente rival

