## 1. Base del proyecto

- [x] 1.1 Inicializar el repositorio git, `.gitignore` (Python, uv, `.venv`, `debug/`) y `README.md` con propósito, requisitos e instrucciones de arranque
- [x] 1.2 Crear `pyproject.toml` (layout `src/`, Python 3.12 en `.python-version`, dependencias de D1 y pytest como dependencia de desarrollo) y generar `uv.lock` con `uv sync`
- [x] 1.3 Crear la estructura de paquetes de D2 con `__init__.py` y un punto de entrada `pokemon-stats-live` → `app:main`
- [x] 1.4 Configurar pytest (`tests/`, marcador `windows` para los tests que necesitan Win32/OCR) y comprobar que `uv run pytest` funciona sin tests

## 2. Dataset (pokemon-data)

- [x] 2.1 Implementar `tools/build_dataset.py`: descargar los CSV de D9, unirlos y escribir `pokedex.json` de forma atómica; salir con código ≠ 0 si falla la descarga sin sobrescribir el anterior
- [x] 2.2 Ejecutar el script y añadir `src/pokemon_stats_live/data/pokedex.json` al repositorio
- [x] 2.3 Implementar `core/pokedex.py`: carga desde los recursos del paquete, error claro si falta, `get_species(id)` y `defensive_matchups(types)` con agrupación ×4/×2/×½/×¼/×0
- [x] 2.4 Tests: ficha de Charizard (#6, tipos, estadísticas 534, habilidades en español), eficacia de Charizard y Gengar según los escenarios de la spec y dataset ausente

## 3. Normalización y coincidencia (name-recognition, núcleo)

- [x] 3.1 Implementar `core/normalize.py` según la spec: mayúsculas, sin acentos, eliminar nivel (`Lv`, `Nv`, `:L`, `N.`) y género separado, conservar ♂/♀ pegados como M/F
- [x] 3.2 Implementar `core/matcher.py`: índice multilingüe (en/es/fr/de/it) y `match(text) -> MatchResult(species_id | None, score, raw_text)` con `fuzz.ratio` y umbral configurable
- [x] 3.3 Tests: Farfetch'd, "PIDGEY Nv5", "PIDGEY ♂", "NIDORAN♀"→#29, "P1DGEY"→#16 (≥80), "SALAMÈCHE"→#4, "MEW" no da Mewtwo, cadenas vacías o basura → no reconocido

## 4. Perfiles y configuración (game-profiles)

- [x] 4.1 Implementar `core/profiles.py`: modelo `Profile` con región relativa validada en [0,1], conversión fracción↔píxeles, guardar/cargar JSON, ignorar y registrar en el log los archivos corruptos, eliminar
- [x] 4.2 Implementar `core/config.py`: `config.toml` con valores por defecto (atajos, umbral 80, idioma `es`, depuración desactivada, ocultación desactivada) creado si no existe; `state.json` (última ventana, perfil activo, posición del overlay)
- [x] 4.3 Tests: ejemplo 960×640 → (0.5, 0.0625, 0.1667, 0.0375), ida y vuelta de serialización, archivo corrupto ignorado, rectángulo < 8 px rechazado, selección de otro perfil activo al eliminar el actual

## 5. Visión y OCR

- [x] 5.1 Implementar `vision/preprocess.py` (D6): recorte por región, ampliación con vecino más próximo hasta ≥ 64 px de alto, Otsu, normalización de polaridad y margen
- [x] 5.2 Tests de preprocesado con imágenes sintéticas: texto blanco sobre negro → negro sobre blanco; recorte de 16 px → ≥ 64 px conservando solo los valores 0 y 255
- [x] 5.3 Implementar `platform/ocr.py`: `recognize(image, langs)` con winocr, primer resultado no vacío, error que indica el paquete de idioma a instalar si no hay ninguno disponible
- [x] 5.4 Test `windows`: renderizar "PIDGEY" con una fuente del sistema, pasarlo por preprocesado + OCR y comprobar la coincidencia → #16

## 6. Integración con Windows (window-capture)

- [x] 6.1 Implementar `platform/windows.py`: listar ventanas visibles con título (excluyendo las minimizadas y las propias) con hwnd, título y ejecutable; rectángulo del área cliente en píxeles físicos; volver a encontrar la ventana por ejecutable
- [x] 6.2 Implementar `platform/capture.py`: captura del área cliente con mss (una instancia por llamada) y errores tipados `WindowUnavailable` / `WindowMinimized`
- [x] 6.3 Implementar `platform/single_instance.py` (mutex con nombre) y `platform/hotkeys.py` (RegisterHotKey en un hilo con bucle de mensajes, parseo de "Ctrl+Alt+P", rechazo de teclas F sin modificador, aviso de los atajos que no se pudieron registrar, liberación al salir)
- [x] 6.4 Tests: parseo de atajos (válidos, inválidos, F sin modificador) y test `windows` que captura una ventana Qt propia de tamaño conocido y comprueba las dimensiones

## 7. Pipeline

- [x] 7.1 Implementar `pipeline.py`: captura → recorte → preprocesado → OCR → coincidencia → `RecognitionResult`; volcado de depuración (recorte, preprocesado, JSON con la misma marca de tiempo) si está activado; medir el tiempo de cada fase en el log
- [x] 7.2 Tests del pipeline con capturador y OCR simulados: éxito, no reconocido, ventana no disponible y archivos de depuración creados

## 8. Interfaz (battle-overlay)

- [x] 8.1 Implementar `ui/overlay.py` (D14): ficha completa (nombre, número, tipos con color, debilidades/resistencias/inmunidades, barras de estadísticas y total, habilidades con la oculta marcada), vista de "no reconocido", sin foco, sin barra de tareas, `WDA_EXCLUDEFROMCAPTURE`, arrastrable, recordar posición, ocultar al hacer clic o por tiempo, reemplazar el contenido
- [x] 8.2 Implementar `ui/calibrator.py`: ventana con la captura, dibujar un rectángulo con el ratón, Enter/Esc, validar el tamaño mínimo, pedir el nombre del perfil (crear o recalibrar)
- [x] 8.3 Implementar `ui/tray.py`: menú de ventana objetivo, perfil activo, calibrar, recalibrar, eliminar perfil, abrir carpeta de datos, salir; avisos con mensajes de la bandeja
- [x] 8.4 Implementar `app.py`: instancia única, carga de configuración, dataset y perfiles, reselección de la ventana, conexión de atajos → QThreadPool → overlay, ignorar reconocimientos simultáneos y salida limpia

## 9. Validación

- [x] 9.1 Ejecutar todos los tests (`uv run pytest`) y `openspec validate add-battle-overlay-mvp --strict` sin errores
- [ ] 9.2 Validación manual por parte del usuario con al menos un juego de GBA y uno de NDS: calibrar, reconocer 10 rivales distintos con el modo depuración activado, anotar la tasa de acierto y comprobar < 500 ms en el log
- [x] 9.3 Actualizar el README con el uso (calibración, atajos, depuración, instalación del paquete de OCR) y las limitaciones conocidas del diseño
