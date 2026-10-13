## Why

Al jugar a juegos de Pokémon en un emulador de PC, consultar la información del Pokémon rival (tipos, debilidades, estadísticas) obliga a salir del juego y buscarla a mano. Queremos una herramienta que lo resuelva **con cualquier emulador y cualquier juego**, sin depender de direcciones de memoria específicas, aprovechando que la pantalla de combate siempre muestra el nombre del rival.

## What Changes

Se crea la aplicación desde cero (MVP) como app de escritorio para Windows en Python:

- Selección de la ventana del emulador y captura de su área cliente.
- Perfiles de calibración por juego: el usuario marca una vez la región donde aparece el nombre del rival; las coordenadas se guardan relativas al tamaño de la ventana.
- Reconocimiento del nombre bajo demanda (atajo de teclado global): recorte → preprocesado → OCR → coincidencia aproximada contra los nombres de todas las especies en varios idiomas.
- Dataset local de Pokémon generado a partir de los CSV públicos de PokéAPI (funciona sin conexión en tiempo de ejecución).
- Ventana superpuesta (overlay) siempre visible, que no roba el foco, con tipos, debilidades/resistencias/inmunidades, estadísticas base y habilidades.
- Icono en la bandeja del sistema para elegir ventana y perfil, calibrar y salir.

**Fuera de alcance (cambios futuros):** detección automática de inicio de combate, fallback con modelo de visión (Claude API), combates dobles, tablas de tipos por generación, formas regionales.

## Capabilities

### New Capabilities
- `window-capture`: enumerar ventanas visibles, seleccionar la del emulador y capturar su área cliente.
- `game-profiles`: crear, guardar, cargar y seleccionar perfiles de calibración con regiones relativas.
- `name-recognition`: preprocesar el recorte, ejecutar OCR y resolver el texto a una especie mediante coincidencia aproximada multilingüe.
- `pokemon-data`: dataset local de especies (nombres, tipos, estadísticas base, habilidades) y cálculo de eficacia de tipos.
- `battle-overlay`: atajos globales, ventana superpuesta con la ficha del Pokémon e icono en la bandeja del sistema.

### Modified Capabilities
<!-- Ninguna: proyecto nuevo. -->

## Impact

- **Código nuevo**: paquete `src/pokemon_stats_live/`, script `tools/build_dataset.py`, tests en `tests/`.
- **Dependencias**: PyQt6, mss, opencv-python-headless, numpy, pillow, winrt (Windows.Media.Ocr), rapidfuzz; pytest como dependencia de desarrollo. Gestión con `uv`.
- **Sistema**: solo Windows 10/11. El OCR usa el motor nativo de Windows y requiere tener instalado al menos un paquete de idioma con OCR (inglés o español).
- **Datos de usuario**: perfiles y configuración en `%APPDATA%\pokemon-stats-live\`. No se envía nada a la red en tiempo de ejecución.
