## Why

Para publicar BattleLens a usuarios no técnicos faltan tres cosas: cambiar opciones sin editar un archivo TOML a mano, enterarse de que hay una versión nueva sin visitar GitHub, y que los informes de fallos lleguen con la información necesaria (emulador, juego, recortes de depuración) para poder arreglarlos.

## What Changes

- **Ventana «Ajustes…»** en la bandeja con todos los valores de `config.toml`, validación y aplicación inmediata (sin reiniciar), incluido volver a registrar los atajos.
- **Aviso de versión nueva:** al arrancar (como máximo una vez al día) se consulta la última Release en GitHub. Si es más nueva, se avisa y se ofrece «Descargar BattleLens X.Y.Z…». Se desactiva con `updates.check = false`. Es la única petición de red de la app, y por eso se modifica el requisito «sin conexión» del dataset.
- **Plantillas de issues** en GitHub (fallo y mejora) que piden versión, emulador, juego y archivos de depuración.
- El ejecutable vuelve a incluir el módulo `ssl` (necesario para HTTPS).

## Capabilities

### New Capabilities
- `app-settings`: ventana de ajustes, validación, guardado conservando comentarios y aplicación en caliente.
- `update-check`: comprobación de la última Release y comparación de versiones.
- `issue-templates`: formularios de GitHub para fallos y mejoras.

### Modified Capabilities
- `pokemon-data`: se permite una única petición de red (comprobación de actualizaciones, desactivable).
- `battle-overlay`: el menú de la bandeja incluye «Ajustes…» y «Descargar BattleLens X.Y.Z…» cuando procede.

## Impact

- **Código:** nuevo `ui/settings.py`, nuevo `core/updates.py`, `core/config.py` (sección `[updates]`, `render_config` y `last_update_check` en el estado), `ui/tray.py`, `app.py` (aplicar ajustes en caliente).
- **Archivos nuevos:** `.github/ISSUE_TEMPLATE/{bug_report.yml, feature_request.yml, config.yml}`.
- **Empaquetado:** se quita `ssl` de las exclusiones de PyInstaller (unos 2-3 MB más).
- **Privacidad:** una petición GET anónima a `api.github.com` al día como máximo; desactivable.
