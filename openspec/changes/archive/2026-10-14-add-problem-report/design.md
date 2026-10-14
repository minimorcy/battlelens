## Context

Los datos útiles para un fallo están repartidos: `config.toml`, `profiles/*.json`, `app.log*` (rotativo, 3 archivos) y `debug/` (solo con depuración activa) en `%APPDATA%\BattleLens`. La captura del emulador (`capture_client`), el recorte de regiones (`crop_regions`, `crop_region`) y la lectura (`read_crop`, `read_moves`) ya existen. Las plantillas de GitHub admiten rellenar campos de un formulario por la URL (`?template=…&<id>=<valor>`).

## Goals / Non-Goals

**Goals:**
- Un clic para tener un ZIP que permita reproducir el fallo sin pedir nada más.
- Nada sale del PC sin que el tester lo adjunte, y sin datos personales evidentes.

**Non-Goals:**
- Subir el informe automáticamente o crear la issue por API (exigiría credenciales o un servicio propio).
- Informes automáticos de errores no capturados.

## Decisions

### D1. `core/report.py`, sin Qt
`ReportInputs` es un dataclass con lo siguiente: rutas de datos, versión, descripción, resumen (dict), imagen del emulador (`np.ndarray | None`), recortes por rol, lecturas por rol y motivo de captura fallida. `write_report(inputs, out_dir, now) -> Path` escribe el ZIP (`ZIP_DEFLATED`) de forma atómica, con un `.tmp` y `os.replace`. `sanitize(text, home, username)` sustituye, sin distinguir mayúsculas, la ruta de la carpeta del usuario (con `\` y con `/`) por `%USERPROFILE%` y el nombre de usuario como palabra completa por `<usuario>`. Se aplica a todo archivo de texto (`.log*`, `.toml`, `.json`). Los PNG se guardan con Pillow.

### D2. Recogida de datos en la app
`Controller.create_report(description, include_capture, open_form)` lanza una tarea en el pool. La tarea captura el emulador (si se pidió y hay ventana), recorta las regiones del perfil activo, las lee con `read_crop` (y el menú con `read_moves`) y llama a `write_report`. Si la captura falla (`CaptureError`, ventana minimizada o cerrada), guarda el motivo y sigue. El resumen sale de `platform.platform()`, `ocr.available_languages()` (con su propio try), la configuración, el perfil, la ventana y el juego. Al terminar, en el hilo de la interfaz:
- abre el Explorador con `explorer /select,<zip>`;
- si `open_form`, abre `issue_form_url(version, emulator_exe, game_name)` con `QDesktopServices`.

### D3. Diálogo (`ui/report.py`)
`ReportDialog(has_window)` contiene:
- una explicación breve de qué incluye y que no se envía nada;
- un `QPlainTextEdit` para la descripción;
- las dos casillas;
- los botones «Crear informe» y «Cancelar».

Mientras se crea, la bandeja avisa con «Creando el informe…» y, al terminar, con la ruta del ZIP.

### D4. URL del formulario
`issue_form_url` construye `REPO_URL + "/issues/new?" + urlencode({"template": "bug_report.yml", "version": …, "emulator": …, "game": …})` y omite los valores vacíos.

## Risks / Trade-offs

- [Datos personales en los títulos de ventana o en los nombres de ROM] → El título del emulador puede incluir el nombre del archivo, y se incluye porque es útil. El diálogo avisa de que el ZIP contiene la captura y el título de la ventana y de que puede revisarse antes de adjuntarlo.
- [Tamaño] → La captura de 1080p son unos pocos MB y como mucho 20 archivos de depuración, aceptable para adjuntar en GitHub (límite de 25 MB).

## Migration Plan

Nada que migrar.

## Open Questions

Ninguna.
