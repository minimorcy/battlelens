# Pokémon Stats Live

Detecta el Pokémon rival cuando juegas en **cualquier emulador** de PC y muestra su ficha (tipos, debilidades, resistencias, inmunidades, estadísticas base y habilidades) en una ventana superpuesta.

No lee la memoria del emulador: lee **el nombre del rival en pantalla** con el OCR nativo de Windows. Por eso funciona con cualquier emulador y cualquier juego de cualquier generación, después de calibrar una vez por juego dónde aparece el nombre.

## Requisitos

- Windows 10 (2004 o posterior) u 11.
- [uv](https://docs.astral.sh/uv/). Descarga Python 3.12 automáticamente.
- Un paquete de idioma de Windows con **OCR** (español o inglés). Normalmente ya está instalado. Si no, la app lo indica al arrancar. Para instalarlo: *Configuración → Hora e idioma → Idioma y región → añadir idioma*, o en PowerShell como administrador:
  ```powershell
  Add-WindowsCapability -Online -Name "Language.OCR~~~es-ES~0.0.1.0"
  ```

## Arranque

```bash
uv sync
uv run pokemon-stats-live
```

Aparece un icono de Poké Ball en la bandeja del sistema.

## Uso

1. **Elige la ventana del emulador:** bandeja → *Ventana del emulador*. La app la recuerda para la próxima vez.
2. **Calibra el juego** (una sola vez por juego): entra en un combate y pulsa `Ctrl+Alt+C`. Dibuja un rectángulo que cubra **solo el nombre del rival**, sin el nivel ni el símbolo de género si puedes. Pulsa `Enter` y ponle nombre al perfil.
3. **En cada combate:** pulsa `Ctrl+Alt+P`. Aparece la ficha junto a la ventana del emulador.
   - Haz clic en la ficha o pulsa `Ctrl+Alt+H` para ocultarla.
   - Arrástrala para moverla; la posición se recuerda.

Desde la bandeja también puedes cambiar de perfil, recalibrar, eliminar perfiles y abrir la carpeta de datos.

## Configuración

`%APPDATA%\pokemon-stats-live\config.toml` (se crea en el primer arranque):

| Clave | Por defecto | Descripción |
|---|---|---|
| `hotkeys.recognize` / `calibrate` / `hide` | `Ctrl+Alt+P` / `C` / `H` | Atajos globales. Requieren al menos un modificador, porque las teclas F las usan los emuladores para los estados guardados |
| `recognition.threshold` | `80` | Puntuación mínima (0-100) para dar un nombre por reconocido |
| `recognition.debug` | `false` | Guarda en `debug/` cada recorte, la imagen preprocesada y un JSON con lo leído |
| `overlay.language` | `es` | Idioma de la ficha: `es`, `en`, `fr`, `de`, `it` |
| `overlay.auto_hide_seconds` | `0` | Ocultar la ficha automáticamente tras N segundos (0 = nunca) |

Otros archivos en la misma carpeta: `profiles/*.json` (perfiles), `state.json` (última ventana, perfil activo y posición de la ficha) y `app.log`.

## Si no reconoce bien

1. Activa `recognition.debug = true`, reinicia y reconoce varios rivales.
2. Mira `debug/*-recorte.png`: ¿contiene solo el nombre? Si no, recalibra.
3. Mira `debug/*.json`: `lecturas` muestra lo que leyó el OCR en cada variante.

## Desarrollo

```bash
uv run pytest                    # todos los tests (incluidos los que usan Win32/OCR/Qt)
uv run pytest -m "not windows"   # solo la lógica pura
uv run python tools/build_dataset.py   # regenera data/pokedex.json desde PokéAPI
```

Estructura: `core/` (lógica pura: dataset, normalización, coincidencia, perfiles, configuración), `vision/` (preprocesado), `platform/` (Win32, captura, OCR, atajos), `ui/` (ficha, calibrador, bandeja), `pipeline.py` y `app.py`.

El proyecto sigue un desarrollo guiado por especificaciones con [OpenSpec](https://github.com/Fission-AI/OpenSpec): ver `openspec/`.

## Limitaciones conocidas

- **Tabla de tipos moderna (Gen 6+).** En juegos antiguos difiere: no existe el tipo Hada, Clefairy era de tipo Normal, etc.
- **Formas regionales** (Vulpix de Alola, etc.): se muestra la forma original.
- **Combates dobles:** solo se lee una región.
- **Ventana tapada:** la captura toma lo que hay en pantalla. Si otra ventana tapa el nombre, no se leerá. La propia ficha está excluida de la captura.
- **Bandas negras:** si el emulador las añade al cambiar la proporción, la región puede descuadrarse. Recalibra.
- **Datos de Pokémon:** de [PokéAPI](https://pokeapi.co/) (CSV públicos), incluidos en `src/pokemon_stats_live/data/pokedex.json`.
