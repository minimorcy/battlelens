## Context

> Nota: el proyecto se renombró a **BattleLens** en el cambio `add-windows-packaging` (paquete `battlelens`, datos en `%APPDATA%\BattleLens`). Este documento ya usa los nombres nuevos.

Proyecto nuevo. El objetivo es identificar al Pokémon rival en **cualquier emulador y cualquier juego** sin leer la memoria del emulador. La única señal común a todos los juegos es visual: el recuadro con el nombre del rival que aparece durante el combate. Restricciones:

- Solo Windows 10/11 (versión 2004 o posterior) en esta fase.
- Debe funcionar sin conexión mientras se juega.
- Debe interferir lo mínimo con el emulador: no robar el foco ni usar las teclas F que los emuladores reservan para los estados guardados.
- Un único usuario (el propio desarrollador), sin despliegue en servidor.

## Goals / Non-Goals

**Goals:**
- Recorrido completo y fiable: atajo → captura → OCR → especie → overlay en menos de 500 ms.
- Funcionar con cualquier emulador gracias a la calibración manual de una región por juego.
- Separar la lógica pura (normalización, coincidencia, eficacia de tipos, modelo de perfiles) de la parte de Windows y Qt para poder probarla con pytest sin pantalla.

**Non-Goals:**
- Detectar automáticamente el inicio de un combate (se hará en otro cambio, vigilando la barra de PS).
- Fallback con modelo de visión, combates dobles, formas regionales y tablas de tipos de generaciones antiguas.
- Soporte para macOS o Linux, instalador y actualizaciones automáticas.

## Decisions

### D1. Python 3.12 gestionado con `uv`
Se fija Python 3.12 en `.python-version` y las dependencias en `pyproject.toml`/`uv.lock`. Hay ruedas precompiladas de PyQt6, winrt, opencv y rapidfuzz para 3.12. Las llamadas a Win32 se hacen con `ctypes` (sin `pywin32`): son pocas funciones y así sobra una dependencia. En el equipo está instalado Python 3.14, pero algunas dependencias de Windows pueden no tener todavía ruedas para él. `uv` descarga el intérprete correcto sin tocar el del sistema.
*Alternativa descartada:* Electron o Tauri para la interfaz con un proceso Python aparte. Supone dos lenguajes y comunicación entre procesos, sin ventaja para una ventana sencilla.

### D2. Estructura en módulos con un núcleo puro
```
src/battlelens/
  core/           # sin dependencias de Windows ni Qt → probado con pytest
    normalize.py  # normalización de texto
    matcher.py    # índice de nombres + rapidfuzz
    pokedex.py    # carga del dataset, ficha de especie, eficacia de tipos
    profiles.py   # modelo Profile, región relativa↔píxeles, serialización
    config.py     # config.toml (usuario) + state.json (estado de la app)
  platform/       # integración con Windows
    windows.py    # listado de ventanas, área cliente, DPI
    capture.py    # captura con mss
    ocr.py        # winocr + comprobación de idiomas instalados
    hotkeys.py    # RegisterHotKey en un hilo propio
    single_instance.py
  vision/
    preprocess.py # OpenCV (puro, con tests)
  ui/
    overlay.py, calibrator.py, tray.py
  pipeline.py     # une las piezas: captura → recorte → preprocesado → OCR → coincidencia
  app.py          # punto de entrada
  data/pokedex.json
tools/build_dataset.py
tests/
```

### D3. Captura con `mss` sobre el rectángulo del área cliente
Con `GetClientRect` + `ClientToScreen` (ctypes) se obtiene el rectángulo en píxeles físicos y `mss` captura esa zona de la pantalla. Qt 6 ya hace que el proceso sea consciente del DPI de cada monitor, así que las coordenadas de Win32 son físicas.
*Alternativa descartada:* Windows Graphics Capture (`windows-capture`). Captura aunque la ventana esté tapada, pero es asíncrona y basada en sesiones, lo que complica una captura puntual. El caso de uso (estás jugando) garantiza que la ventana está visible. Se puede cambiar más adelante gracias a la interfaz de `capture.py`.
*Alternativa descartada:* `PrintWindow`. Devuelve una imagen en negro en emuladores que dibujan con la GPU (OpenGL o Vulkan).

### D3b. Revisión tras probar con juegos reales (tarea 9.2): PrintWindow primero
Al probar con Pokémon Espada en Eden (Vulkan) se vio que, con el emulador tapado por otra ventana, `mss` capturaba la ventana de encima. `PrintWindow(hwnd, PW_CLIENTONLY | PW_RENDERFULLCONTENT)` obtiene el contenido real a través de DWM aunque la ventana esté tapada, también con Vulkan. Se usa primero y, si devuelve una imagen negra (algunas aplicaciones no lo admiten), se recurre a `mss`.

### D4. Excluir el overlay de las capturas
Al overlay se le aplica `SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)`. Así, aunque quede encima del juego, nunca aparece en el recorte. Se evita tener que ocultarlo y volver a mostrarlo antes de cada captura, que provocaría parpadeos.

### D5. Regiones relativas al área cliente
La región se guarda como fracciones (x, y, ancho, alto) en [0, 1]. Así resiste los cambios de tamaño de la ventana y del escalado del emulador, que mantienen la proporción. Si el emulador añade bandas negras al cambiar de proporción, la región deja de coincidir; el overlay de "no reconocido" con el texto leído invita a recalibrar.

### D6. Preprocesado: binarizar y normalizar la altura en varias variantes
Pasos: escala de grises → Otsu → si predomina el negro, se invierte (texto oscuro sobre claro) → altura normalizada a 20/24/28/32/40 px, con y sin desenfoque gaussiano σ=1 → margen blanco de 10 px. Se prueban las 10 variantes con el OCR y se queda la de mayor puntuación de coincidencia, con parada temprana al llegar a 100.
*Por qué (medido durante la implementación):* con texto pixelado sintético de estilo GBA, la propuesta inicial (ampliar a ≥ 64 px) acertaba un 30-60 %. La mejor variante única (altura de 24 px) llegaba al 78 %. Combinar varias variantes llegó al 97 % (35 de 36) con unos 23 ms por reconocimiento, porque cada OCR cuesta 3-5 ms. El OCR de Windows lee mejor el texto pequeño y nítido que el muy ampliado.

### D7. OCR nativo de Windows (`winrt`, Windows.Media.Ocr)
Se usa directamente a través de los paquetes `winrt-*` (al principio se pensó en el envoltorio `winocr`, pero no aporta nada). Es rápido (3-5 ms por imagen pequeña), no requiere instalar nada más que el paquete de idioma, que suele estar ya presente, y reconoce bien el texto impreso. Se ejecuta con `asyncio.run` dentro del hilo de trabajo.
*Alternativa descartada:* Tesseract. Requiere un binario externo y es más lento. PaddleOCR o EasyOCR: dependencias de cientos de MB. Si la precisión no es suficiente, `ocr.py` permite cambiar de motor.

### D8. Coincidencia: `rapidfuzz.fuzz.ratio` contra un índice multilingüe
El índice es un diccionario `nombre_normalizado → id_especie` con los nombres en en/es/fr/de/it. Las duplicidades entre idiomas apuntan a la misma especie. Se usa `process.extractOne(..., scorer=fuzz.ratio, score_cutoff=umbral)`.
*Por qué `ratio` y no `WRatio`/`partial_ratio`:* las variantes parciales puntúan 100 cuando un nombre está contenido en otro ("MEW" dentro de "MEWTWO"). `ratio` penaliza la diferencia de longitud.

### D9. Dataset desde los CSV del repositorio de PokéAPI
`tools/build_dataset.py` descarga de `raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/` los archivos `pokemon_species`, `pokemon_species_names`, `pokemon`, `pokemon_types`, `pokemon_stats`, `pokemon_abilities`, `ability_names`, `types`, `type_names`, `type_efficacy` y `languages`. Genera `pokedex.json`, que se incluye en el repositorio para que la app funcione sin ejecutar el script. Son unos 11 archivos frente a más de 3000 llamadas a la API REST. Se escribe en un archivo temporal y se renombra al terminar, para no dejar nunca un JSON a medias.
*Alternativa descartada:* el endpoint GraphQL beta de PokéAPI, porque es menos estable.

### D10. Atajos globales con `RegisterHotKey` (Win32)
Se ejecutan en un hilo propio con su bucle de mensajes (`GetMessage`), que emite señales de Qt hacia el hilo de la interfaz. Ventajas frente a `pynput` o `keyboard`: Windows se queda la combinación (el emulador no la recibe), avisa si ya la tiene otra aplicación (lo que permite el escenario "atajo ocupado") y no instala un hook de teclado, que los antivirus suelen marcar.
*Esto sustituye a `pynput`, mencionado en la propuesta.*

### D11. Hilos
El hilo de la interfaz (Qt) nunca hace trabajo pesado. Cada reconocimiento es una tarea de `QThreadPool`. Como `mss` no es seguro entre hilos, se crea una instancia por captura. Si llega un reconocimiento con otro en curso, se ignora (se pierde la pulsación, no se encola).

### D12. Configuración en dos archivos
- `config.toml`: lo edita el usuario (atajos, umbral, idioma de la interfaz, depuración, tiempo de ocultación). Se lee con `tomllib` y, si no existe, se crea con los valores por defecto.
- `state.json`: lo escribe la app (última ventana, perfil activo, posición del overlay). Separarlos evita reescribir el archivo del usuario y perder sus comentarios.

### D13. Instancia única con un mutex con nombre de Win32
`CreateMutex("Local\\pokemon-stats-live")`. Si devuelve `ERROR_ALREADY_EXISTS`, ya hay otra instancia en marcha. (El nombre pasa a `BattleLens` en `add-windows-packaging`, D6, para que el instalador pueda detectar la app abierta.)

### D14. Overlay
Un `QWidget` con las opciones `FramelessWindowHint | WindowStaysOnTopHint | Tool | WindowDoesNotAcceptFocus` y el atributo `WA_ShowWithoutActivating`. Se dibuja con widgets de Qt y una hoja de estilos con los colores oficiales de cada tipo. La posición se calcula en píxeles físicos (Win32) y se convierte a coordenadas lógicas de Qt dividiendo por el `devicePixelRatio` de la pantalla correspondiente.

## Risks / Trade-offs

- [Juegos 3D (Switch, 3DS) con texto suavizado y regiones holgadas] → Descubierto en la tarea 9.2: las variantes binarizadas fallaban con fondos mezclados (hierba + caja blanca). Se añaden el recorte original y variantes en gris al principio de la lista, y la búsqueda por palabras y con recorte del final. Caso real: con la región del usuario, Stufful pasó de «no reconocido» a 84 puntos.

- [Los nombres en mayúsculas con fuente de 8×8 de las Gen 1-3 pueden leerse mal] → El preprocesado de D6, la coincidencia aproximada y el volcado de depuración permiten ajustar con capturas reales. Si no basta, se cambia de motor de OCR (la interfaz de D7 lo permite) o se reconocen plantillas de letras por juego.
- [Al usuario le falta el paquete de OCR de su idioma] → Error explícito al arrancar con instrucciones (Configuración → Hora e idioma → Idioma → Opciones → Reconocimiento óptico de caracteres).
- [La ventana del emulador tapada o en otro escritorio virtual da una captura incorrecta] → Mientras se juega es poco probable. Documentado; posible migración a Windows Graphics Capture (D3).
- [Las bandas negras o el cambio de proporción del emulador descuadran la región] → Recalibrar en un clic; el overlay de "no reconocido" lo sugiere.
- [Tabla de tipos moderna (Gen 6+) en juegos antiguos: el Hada no existe, Clefairy era Normal, en Gen 1 Fantasma no afectaba a Psíquico] → Se acepta en el MVP y se documenta. Un cambio futuro añadirá `generation` al perfil y usará `pokemon_types_past.csv`.
- [El dataset de nombres en japonés o coreano no está incluido] → Fuera de alcance; el OCR de Windows también necesitaría ese paquete de idioma.
- [Nombres casi idénticos (Porygon/Porygon2, Nidoran♂/♀)] → La normalización conserva los dígitos y el sufijo M/F; si se pierde el símbolo, puede salir el Nidoran equivocado (ambos tienen tipo Veneno, así que el impacto es bajo).

## Migration Plan

No aplica (proyecto nuevo). Para desinstalar basta con borrar la carpeta del proyecto y `%APPDATA%\BattleLens\`.

## Open Questions

- ¿Hace falta un modo "mostrar a la vez la ficha de los dos idiomas"? Por defecto se usa el idioma de la interfaz (`es`) y los nombres de habilidades en ese idioma.
- La precisión real del OCR en cada generación se validará con capturas del usuario (tarea de validación manual). Según el resultado se decidirá si hace falta una alternativa por plantillas.
