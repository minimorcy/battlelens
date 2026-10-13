## Context

El MVP (`add-battle-overlay-mvp`) funciona desde el código fuente con `uv`. Para publicarlo en GitHub, hace falta que un jugador sin conocimientos técnicos pueda descargarlo, instalarlo y usarlo. Situación de partida:

- Dependencias medidas en `.venv`: PyQt6 214 MB (143 MB de DLL de Qt, de las que solo se necesitan Core, Gui y Widgets), **OpenCV 113 MB**, numpy 25 MB, Pillow 15 MB, rapidfuzz 6 MB y winrt 3 MB.
- OpenCV solo se usa para 6 operaciones: escala de grises, Otsu, redimensionar, desenfoque gaussiano, margen y codificar PNG.
- La app ya guarda los datos de usuario en `%APPDATA%` y carga el dataset con `importlib.resources`, lo que encaja bien con el empaquetado.
- No hay certificado de firma de código.

## Goals / Non-Goals

**Goals:**
- Instalar con un clic, sin permisos de administrador y sin Python.
- Publicar versiones de forma reproducible con una etiqueta de git.
- Descarga de 60 MB como máximo.
- Que un usuario nuevo pueda resolver solo la falta del paquete de OCR.
- Distribución prudente en cuanto a marcas registradas.

**Non-Goals:**
- Firma de código, actualización automática, winget o Microsoft Store.
- Compilaciones para macOS o Linux.

## Decisions

### D1. PyInstaller en modo carpeta (*onedir*)
Es la herramienta más madura con PyQt6 (tiene *hooks* oficiales para Qt) y genera un `.exe` con metadatos de versión.
*Alternativas:* **Nuitka** compila a C, arranca algo más rápido y tiene menos falsos positivos, pero las compilaciones son mucho más lentas (más de 10 minutos en CI), necesita compilador de C y da más problemas con `winrt`. **Briefcase** genera MSI, pero tiene menos control sobre la exclusión de módulos.
*Por qué onedir y no onefile:* onefile se descomprime en `%TEMP%` en cada arranque (más lento) y los antivirus lo marcan más a menudo. Como el instalador ya entrega un solo archivo, onefile no aporta nada.
*Sin UPX:* comprimir las DLL de Qt con UPX las rompe a veces y aumenta los falsos positivos.

### D2. Archivo `.spec` versionado y `packaging/build.py`
`packaging/pokemon_stats_live.spec` declara: punto de entrada `packaging/entry.py` (importa `pokemon_stats_live.app:main`), `datas` (pokedex.json, icono y LICENSE), `copy_metadata("pokemon-stats-live")` para que `importlib.metadata.version()` funcione congelado, `hiddenimports` para `winrt.windows.*` (se cargan de forma dinámica) y `excludes` (QtQml, QtQuick, QtWebEngine, QtMultimedia, QtNetwork, QtSql, tkinter, unittest…). `build.py` lee la versión de `pyproject.toml`, genera el archivo de versión de Windows (`VSVersionInfo`), limpia `build/` y `dist/`, llama a PyInstaller, elimina las traducciones de Qt sobrantes, mide el tamaño y, si existe ISCC, compila también el instalador y el ZIP.

### D3. Versión desde `pyproject.toml`
En tiempo de ejecución: `importlib.metadata.version("pokemon-stats-live")`, con `"0.0.0+dev"` si falla. Al compilar: `build.py` la inyecta en los metadatos del `.exe` y en ISCC (`/DAppVersion=…`). En CI: se compara con la etiqueta (`v${version}`).

### D4. Autocomprobación `--self-test`
Como el `.exe` es de tipo ventana, no tiene stdout. Por eso el resultado se escribe en el JSON indicado por `--self-test-output` y el código de salida indica el éxito. Comprueba: importación de los módulos (PyQt6.QtWidgets, mss, winrt OCR, rapidfuzz, numpy, PIL), carga del dataset, `match("PIDGEY") == 16` y disponibilidad del OCR (solo como aviso, porque el runner de CI puede no tener el paquete de idioma). No crea `QApplication` ni registra atajos. En CI se lanza con `Start-Process -Wait -PassThru` y se comprueba `ExitCode`.

### D5. OpenCV → numpy + Pillow
| OpenCV | Sustituto |
|---|---|
| `cvtColor(RGB2GRAY)` | `Image.convert("L")` (misma fórmula de luminancia ITU-R 601) |
| `threshold(OTSU)` | Otsu en numpy sobre el histograma de 256 niveles (unas 10 líneas) |
| `resize(INTER_NEAREST/INTER_AREA)` | `Image.resize(NEAREST/BOX)` |
| `GaussianBlur(σ)` | `ImageFilter.GaussianBlur(radius=σ)` |
| `copyMakeBorder` | `np.pad(constant_values=255)` |
| `imencode(".png")` | `Image.save(PNG)` |

**Criterio de aceptación:** el banco de pruebas de precisión (hoy un script temporal) pasa a ser un test del repositorio (`tests/test_ocr_accuracy.py`) y debe dar ≥ 34/36 antes y después del cambio. Si Pillow da peores resultados, se ajustan σ y las alturas de las variantes antes de dar la tarea por cerrada.

### D6. Instalador Inno Setup por usuario
`PrivilegesRequired=lowest` instala en `{localappdata}\Programs\PokemonStatsLive` sin UAC. `AppId` es un GUID fijo, para que las versiones nuevas se instalen encima de las anteriores. `AppMutex=pokemon-stats-live` hace que el instalador detecte la app abierta. **Implica cambiar el nombre del mutex de la app** de `Local\pokemon-stats-live` a `pokemon-stats-live`; dentro de la sesión del usuario el efecto es el mismo. Las tareas opcionales son `desktopicon` e `startup` (clave `HKCU\…\Run`). Idiomas: Spanish y English. Al desinstalar, el `[Code]` pregunta si se borra `{userappdata}\pokemon-stats-live`, con «No» como respuesta por defecto.
*Alternativas descartadas:* MSI con WiX (más complejo y sin ventaja aquí) y NSIS (scripts menos legibles).

### D7. GitHub Actions
- `ci.yml` (push y pull request): `windows-latest` → `astral-sh/setup-uv` → `uv sync` → `uv run pytest` → `npx @fission-ai/openspec validate --all --strict`. En push a `main` también compila y sube el instalador y el ZIP como artefactos (14 días).
- `release.yml` (etiquetas `v*`): comprueba la versión → tests → compila → `--self-test` → ISCC → ZIP → `SHA256SUMS.txt` → extrae las notas de `CHANGELOG.md` → `gh release create` (el CLI `gh` viene en el runner; no hace falta una acción de terceros). Permisos: `contents: write`.
- Inno Setup 6 viene preinstalado en las imágenes `windows-2022`/`windows-latest`. Si faltara, `choco install innosetup` como alternativa en el propio flujo.

### D8. Tests de OCR condicionados
Un marcador o *fixture* `requires_ocr` comprueba `available_languages()` y omite el test con el motivo «sin paquete de OCR es/en» si no hay ninguno. Se aplica a los tests de OCR, de precisión y de integración con la app.

### D9. Instalación guiada del OCR
Se usa `ShellExecuteExW` con el verbo `runas` sobre `powershell.exe -NoProfile -Command "Add-WindowsCapability -Online -Name 'Language.OCR~~~<tag>~0.0.1.0'"` y `SEE_MASK_NOCLOSEPROCESS`. El handle del proceso se espera en un `QThreadPool` y luego se lee el código de salida. Si el usuario cancela el UAC, se recibe `ERROR_CANCELLED` (1223). El idioma propuesto se obtiene de `GetUserDefaultUILanguage` → `LCIDToLocaleName` y, si no está entre los soportados, se usa `en-US`. Después se vuelve a comprobar con `available_languages()`. Si WinRT tiene la lista en caché, se pide reiniciar la app.

### D10. Icono original
Se sustituye la Poké Ball dibujada en `tray.py` por un diseño propio: una lupa sobre unas barras de estadísticas, en colores neutros. `packaging/make_icon.py` lo genera con Pillow (`.ico` multirresolución de 16 a 256 px, más el PNG que usa Qt), sin depender de recursos externos.

### D11. Licencia MIT
Es permisiva y habitual en herramientas de fans. Los datos de PokéAPI tienen licencia BSD-3-Clause; se atribuyen en «Acerca de» y en el README.

## Risks / Trade-offs

- [Falsos positivos de antivirus con PyInstaller] → Sin onefile ni UPX. Se publican los SHA-256. Si se informan casos, se envía el ejecutable a los fabricantes como falso positivo. El README lo explica.
- [Aviso de SmartScreen por no estar firmado] → Documentado con capturas en el README. La reputación del archivo mejora con las descargas. La firma de código queda para el futuro.
- [`winrt` no encontrado al congelar (importaciones dinámicas)] → `hiddenimports` explícitos y la autocomprobación, que importa el OCR, lo detecta en CI antes de publicar.
- [Pillow da una precisión distinta de OpenCV] → El test de precisión es la puerta de aceptación (D5).
- [El runner de CI no tiene OCR en español ni en inglés] → Los tests se omiten (D8) y la autocomprobación lo trata como aviso. La precisión real se vigila en local.
- [Marca registrada en el nombre «Pokémon Stats Live»] → Aviso de proyecto no oficial y ningún recurso visual oficial. Ver Open Questions.
- [Cambiar el nombre del mutex rompe la detección de instancia única entre versiones durante la transición] → Solo afecta a quien tenga abierta una versión de desarrollo mientras arranca otra. Se acepta.

## Migration Plan

1. Fusionar este cambio en `main` y comprobar que la CI y los artefactos de `main` funcionan.
2. Instalar el artefacto en una máquina o VM limpia (sin Python) y repasar los escenarios del instalador.
3. Crear la etiqueta `v0.2.0` para la primera Release pública.
**Vuelta atrás:** borrar la Release o la etiqueta; los usuarios pueden desinstalar desde «Aplicaciones instaladas». Los datos de usuario no cambian de formato.

## Open Questions

- **Nombre del repositorio y de la app:** ¿se mantiene «Pokémon Stats Live» o se elige un nombre sin la marca (por ejemplo «Battle Dex Live») para reducir el riesgo de una retirada por marca registrada? No bloquea la implementación: el nombre se define en un único punto.
- **Usuario u organización de GitHub** donde se publica. Hace falta para el enlace de «Acerca de» y el README.
- **Licencia:** se propone MIT (D11); falta confirmarlo.
