# stream-mode Specification

## Purpose
TBD - created by archiving change add-stream-mode. Update Purpose after archive.
## Requirements
### Requirement: Activar el modo stream
El sistema SHALL ofrecer un modo stream, desactivado por defecto (`stream.enabled = false`), que se activa y desactiva desde la bandeja («Modo stream») y desde Ajustes, y se guarda en `config.toml`. Con el modo stream desactivado, el sistema MUST NOT abrir ningún puerto ni cambiar el comportamiento de la ficha privada.

#### Scenario: Activar desde la bandeja
- **WHEN** el usuario marca «Modo stream» en la bandeja
- **THEN** se arranca el servidor de la fuente para OBS, se guarda `stream.enabled = true` y la bandeja indica la URL

#### Scenario: Desactivado
- **WHEN** el modo stream está desactivado
- **THEN** no hay ningún puerto abierto por BattleLens

### Requirement: Servidor local de la fuente para OBS
Con el modo stream activo, el sistema SHALL servir por HTTP, solo en `127.0.0.1` y en el puerto `stream.port` (por defecto 17320), la página de la ficha del stream (`/`, con sus archivos estáticos) y el estado actual de la ficha en JSON (`/state`). El servidor MUST responder solo a peticiones GET, MUST rechazar con 403 las peticiones cuya cabecera `Host` no sea `localhost` o `127.0.0.1` con ese puerto, MUST responder 404 a cualquier otra ruta y MUST NOT servir archivos fuera de la lista de archivos de la página. Si el puerto está ocupado, el sistema SHALL avisar en la bandeja indicando el puerto y seguir funcionando sin la fuente.

#### Scenario: OBS carga la página
- **WHEN** OBS abre `http://localhost:17320/`
- **THEN** recibe la página de la ficha con fondo transparente

#### Scenario: Otro sitio web intenta leer el estado
- **WHEN** llega una petición a `/state` con la cabecera `Host: ejemplo.com`
- **THEN** se responde 403 sin datos

#### Scenario: Ruta desconocida
- **WHEN** se pide `/../config.toml` o `/otra`
- **THEN** se responde 404

#### Scenario: Puerto ocupado
- **WHEN** el puerto 17320 está en uso al activar el modo stream
- **THEN** la bandeja avisa «El puerto 17320 está ocupado: cámbialo en Ajustes» y la ficha privada sigue funcionando

### Requirement: Contenido de la ficha del stream
El estado (`/state`) SHALL describir, para cada rival mostrado, la ficha según el modo de ficha del stream (`stream.card_mode`, por defecto `normal`, independiente del de la ficha privada): nombre (con la forma), número, tipos con su color, ratio de captura con su dificultad, «Contra tu X» con veredicto, tus movimientos con su multiplicador, debilidades e inmunidades, efectos de habilidades y evolución; y en modo Competitivo además el nivel, las resistencias y las estadísticas base con su total. Los textos MUST coincidir con los de la ficha privada. El estado MUST incluir un contador que cambia con cada actualización.

#### Scenario: Rival con tu Pokémon
- **WHEN** se muestra Machop en `sword-shield` contra tu Scorbunny con modo de stream Normal
- **THEN** `/state` contiene una tarjeta «Machop», tipo Lucha, «Captura: 180 · Media», «Contra tu Scorbunny» con el veredicto «Neutral» y la debilidad ×2 a Volador, Psíquico y Hada

#### Scenario: Modo Competitivo en el stream
- **WHEN** `stream.card_mode = "competitive"` y se muestra Machop de nivel 16
- **THEN** la tarjeta incluye «Nv. 16», las resistencias y las estadísticas base

### Requirement: Visibilidad de la ficha del stream
La ficha del stream SHALL aparecer cada vez que se muestra una ficha de combate (manual o automática, incluido al cambiar de forma o de modo), y SHALL ocultarse cuando la detección automática da por terminado el combate. Cerrar la ficha privada con un clic o con el atajo de ocultar MUST NOT ocultar la del stream. El atajo «Mostrar/ocultar ficha del stream» (por defecto `Ctrl+Alt+S`) alterna su visibilidad hasta el siguiente rival. La página MUST consultar el estado periódicamente (como mucho cada 500 ms) y animar la entrada y la salida.

#### Scenario: Fin del combate
- **WHEN** la detección automática oculta la ficha al terminar el combate
- **THEN** la ficha del stream se oculta también

#### Scenario: Ocultar solo la privada
- **WHEN** el streamer hace clic en su ficha privada
- **THEN** la privada se oculta y la del stream sigue visible

#### Scenario: Ocultar la del stream
- **WHEN** el streamer pulsa `Ctrl+Alt+S` con la ficha del stream visible
- **THEN** la ficha del stream se oculta y la privada no cambia

### Requirement: Tamaño de la ficha del stream
La página SHALL aceptar el parámetro `scale` (entre 0,5 y 3; por defecto 1) para escalar la ficha sin perder nitidez, y la bandeja SHALL ofrecer «Copiar URL para OBS», que copia la URL al portapapeles.

#### Scenario: Escala
- **WHEN** OBS abre `http://localhost:17320/?scale=1.5`
- **THEN** la ficha se dibuja al 150 %

