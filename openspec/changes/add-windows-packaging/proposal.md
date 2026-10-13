## Why

Ahora mismo, para usar Pokémon Stats Live hay que clonar el repositorio, instalar `uv` y ejecutarlo desde la consola. Queremos publicarlo en GitHub para que cualquier jugador pueda descargarlo e instalarlo como una aplicación normal de Windows, sin conocimientos técnicos ni Python.

## What Changes

- Empaquetado con PyInstaller (modo carpeta, *onedir*) que incluye Python, las dependencias y `pokedex.json`.
- Instalador `PokemonStatsLive-Setup-<versión>.exe` (Inno Setup): acceso directo en el menú Inicio, arranque con Windows opcional, desinstalador. Además, un ZIP portable.
- Pipeline de GitHub Actions: al publicar una etiqueta `v*` ejecuta los tests, compila, hace una prueba de humo del ejecutable y publica una *Release* con el instalador, el ZIP y sus sumas SHA-256.
- **Reducción de tamaño:** se sustituye OpenCV (unos 113 MB) por numpy + Pillow en el preprocesado, sin cambiar su comportamiento.
- Ayuda guiada para instalar el paquete de OCR de Windows cuando falta (el requisito más probable con el que se encontrará un usuario nuevo).
- Ventana «Acerca de» con la versión, la licencia, la atribución de datos y el aviso de proyecto no oficial; archivo `LICENSE` en el repositorio.
- Una única fuente de verdad para la versión (`pyproject.toml`), visible en la app, el ejecutable y el instalador.

**Fuera de alcance:** firma de código (certificado de pago), actualización automática, publicación en winget o Microsoft Store, macOS y Linux.

## Capabilities

### New Capabilities
- `windows-packaging`: compilación reproducible del ejecutable con PyInstaller, inclusión de recursos, versión y prueba de humo del ejecutable.
- `installer`: instalador de Inno Setup y ZIP portable (instalación, accesos directos, arranque con Windows, desinstalación, datos de usuario).
- `release-pipeline`: flujo de GitHub Actions que valida, compila y publica las versiones.
- `ocr-language-setup`: detección del paquete de OCR que falta e instalación guiada con elevación de permisos.
- `app-info`: ventana «Acerca de», licencia y avisos legales.

### Modified Capabilities
<!-- Ninguna. El cambio add-battle-overlay-mvp todavía no está archivado, así que sus capacidades aún no existen en openspec/specs/.
     Sustituir OpenCV no cambia ningún requisito: la spec de name-recognition no depende de la librería. -->

## Impact

- **Código:** `vision/preprocess.py` (sin OpenCV), `pipeline.py` (escritura de PNG con Pillow), `platform/ocr.py` (conversión de imagen y comprobación de idiomas), nuevos `ui/about.py` y `platform/ocr_setup.py`, menú de la bandeja.
- **Archivos nuevos:** `packaging/` (spec de PyInstaller, script de Inno Setup, icono `.ico`, script de compilación), `.github/workflows/release.yml` y `ci.yml`, `LICENSE`, `CHANGELOG.md`.
- **Dependencias:** se elimina `opencv-python-headless`; se añaden `pyinstaller` (solo para desarrollo) e Inno Setup 6 (herramienta de compilación, en CI viene instalada en el runner `windows-latest`).
- **Usuarios:** descargan el instalador desde GitHub Releases. Verán el aviso de SmartScreen por no estar firmado, documentado en el README.
- **Repositorio:** necesita un remoto en GitHub y una cuenta autenticada en `gh` para la primera publicación.
