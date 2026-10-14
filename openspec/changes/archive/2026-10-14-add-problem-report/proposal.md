## Why

Vamos a repartir BattleLens a streamers y testers que no son desarrolladores. Hoy, para informar de un fallo, tienen que activar la depuración, buscar `%APPDATA%\BattleLens`, localizar `app.log` y los recortes y adjuntarlos a mano en un formulario en español. Casi nadie lo hará, y sin la captura de lo que veía el emulador es muy difícil reproducir un fallo de reconocimiento.

## What Changes

- **«Informar de un problema…» en la bandeja:** abre un diálogo donde el tester describe qué ha pasado (opcional) y crea, con un clic, un ZIP con todo lo necesario:
  - un resumen (`informe.json`): versión, Windows, idiomas de OCR instalados, idiomas de la interfaz y de los datos, emulador y juego, perfil activo y la descripción;
  - `config.toml`, los perfiles y los registros (`app.log`);
  - una **captura del emulador**, los **recortes de cada región** del perfil activo y lo que lee el OCR en cada una (se puede desmarcar);
  - los últimos recortes de depuración, si los hay.
- **Privacidad:** no se envía nada. El ZIP se guarda en `%APPDATA%\BattleLens\informes\` y la captura es solo de la ventana del emulador. En los textos se sustituyen la carpeta del usuario y su nombre de usuario de Windows por marcadores.
- **Al terminar:** se abre la carpeta con el ZIP seleccionado y, si el tester quiere, el formulario de fallo de GitHub con la versión, el emulador y el juego ya rellenados, para adjuntar el ZIP.
- **Formulario de fallo de GitHub bilingüe** (español/inglés), que pide adjuntar el ZIP del informe.

## Capabilities

### New Capabilities
- `problem-report`: crear el informe de un problema desde la app, su contenido, la privacidad y el formulario de GitHub prerrellenado.

### Modified Capabilities
- `issue-templates`: el formulario de fallo es bilingüe y pide el ZIP del informe.

## Impact

- **Código:** nuevo `core/report.py` (contenido del ZIP y limpieza de rutas), nuevo `ui/report.py` (diálogo), `app.py` (captura, lecturas, creación en segundo plano y apertura de la carpeta y del formulario), `ui/tray.py` y catálogos de `i18n`.
- **Repositorio:** `.github/ISSUE_TEMPLATE/bug_report.yml`.
- **Sin red ni dependencias nuevas** (`zipfile` de la biblioteca estándar).
