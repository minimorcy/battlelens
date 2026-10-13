# BattleLens

**Ficha instantánea del Pokémon rival para juegos de Pokémon en cualquier emulador de PC.**

Pulsa una tecla durante un combate y BattleLens muestra junto al emulador los tipos del rival, sus debilidades, resistencias e inmunidades, sus estadísticas base y sus habilidades.

No lee la memoria del emulador: lee **el nombre del rival en pantalla** con el OCR de Windows. Por eso funciona con cualquier emulador (mGBA, DeSmuME, melonDS, Citra…) y con cualquier generación, después de calibrar una vez por juego.

> BattleLens es un proyecto de fans no oficial. No está afiliado ni respaldado por Nintendo, The Pokémon Company, Creatures Inc. ni GAME FREAK inc. Pokémon y los nombres de los Pokémon son marcas registradas de sus respectivos titulares.

---

## Para jugadores

### Instalación

1. Ve a [**Releases**](https://github.com/minimorcy/battlelens/releases/latest) y descarga `BattleLens-Setup-x.y.z.exe`.
   - ¿Prefieres no instalar nada? Descarga `BattleLens-x.y.z-portable.zip`, descomprímelo y ejecuta `BattleLens.exe`.
2. Ejecuta el instalador. **No pide permisos de administrador.**
3. **Aviso de SmartScreen.** Si Windows muestra «Windows protegió su PC», pulsa **Más información → Ejecutar de todas formas**. Aparece porque el ejecutable no está firmado con un certificado de pago. Si quieres comprobar la descarga, compárala con `SHA256SUMS.txt`:
   ```powershell
   Get-FileHash .\BattleLens-Setup-x.y.z.exe -Algorithm SHA256
   ```

Requisitos: Windows 10 (versión 2004 o posterior) u 11, de 64 bits.

### OCR de Windows

BattleLens usa el reconocimiento de texto que trae Windows. Casi todos los equipos lo tienen ya en su idioma. Si falta, la app avisa al arrancar y ofrece **«Instalar OCR de Windows…»** en su menú; Windows te pedirá permiso para instalarlo.

### Uso

1. Busca el icono de BattleLens en la bandeja del sistema (junto al reloj) y elige **Ventana del emulador**.
2. **Calibra el juego** (una sola vez por juego): en un combate, pulsa `Ctrl+Alt+C`, dibuja un rectángulo que cubra el **nombre del rival** (cuanto más ajustado, mejor) y pulsa `Enter`.
3. **En cada combate:** pulsa `Ctrl+Alt+P`. La ficha aparece junto al emulador.
   - Haz clic en ella o pulsa `Ctrl+Alt+H` para ocultarla. Arrástrala para moverla.

### Configuración

`%APPDATA%\BattleLens\config.toml` (se crea en el primer arranque):

| Clave | Por defecto | Descripción |
|---|---|---|
| `hotkeys.recognize` / `calibrate` / `hide` | `Ctrl+Alt+P` / `C` / `H` | Atajos globales. Necesitan un modificador, porque las teclas F las usan los emuladores para los estados guardados |
| `recognition.threshold` | `80` | Puntuación mínima (0-100) para dar un nombre por reconocido |
| `recognition.debug` | `false` | Guarda en `debug/` cada recorte y lo que leyó el OCR |
| `overlay.language` | `es` | Idioma de la ficha: `es`, `en`, `fr`, `de`, `it` |
| `overlay.auto_hide_seconds` | `0` | Ocultar la ficha tras N segundos (0 = nunca) |

### Si no reconoce bien

1. Pon `recognition.debug = true`, reinicia BattleLens y reconoce varios rivales.
2. En `%APPDATA%\BattleLens\debug\`, el archivo `*-recorte.png` debe contener solo el nombre. Si no, usa **Recalibrar perfil activo**.
3. Si el recorte es correcto y aun así falla, abre un [issue](https://github.com/minimorcy/battlelens/issues) adjuntando esos archivos.

### Limitaciones conocidas

- **Tabla de tipos moderna (Gen 6+).** En juegos antiguos difiere: no existe el tipo Hada, Clefairy era de tipo Normal, etc.
- **Formas regionales:** se muestra la forma original.
- **Combates dobles:** todavía no se admiten.

### Desinstalar

Desde *Configuración → Aplicaciones → Aplicaciones instaladas → BattleLens*. Al desinstalar, se te pregunta si quieres borrar también tus perfiles.

---

## Para desarrolladores

Requisitos: Windows 10/11 y [uv](https://docs.astral.sh/uv/), que descarga Python 3.12 automáticamente.

```bash
uv sync
uv run battlelens                         # ejecutar desde el código
uv run pytest                             # tests (los de OCR se omiten si no hay paquete de OCR)
uv run python tools/build_dataset.py      # regenerar data/pokedex.json desde PokéAPI
uv run python packaging/make_icon.py      # regenerar el icono
uv run python packaging/build.py --self-test   # .exe + instalador (requiere Inno Setup 6) + ZIP
```

Estructura: `core/` (lógica pura), `vision/` (preprocesado), `platform/` (Win32, captura, OCR, atajos), `ui/`, `pipeline.py`, `app.py`. Empaquetado en `packaging/`; CI y publicación en `.github/workflows/`.

### Publicar una versión

1. Actualiza `version` en `pyproject.toml` y añade su sección en `CHANGELOG.md` con fecha.
2. Haz commit, crea la etiqueta y súbela:
   ```bash
   git tag v0.2.0 && git push origin main v0.2.0
   ```
3. GitHub Actions ejecuta los tests, compila, hace la autocomprobación del `.exe` y publica la Release con el instalador, el ZIP y `SHA256SUMS.txt`.

El proyecto sigue un desarrollo guiado por especificaciones con [OpenSpec](https://github.com/Fission-AI/OpenSpec): cada cambio tiene su propuesta, especificaciones, diseño y tareas en `openspec/`.

## Licencia y créditos

- Código: [MIT](LICENSE).
- Datos de Pokémon: [PokéAPI](https://github.com/PokeAPI/pokeapi) (BSD-3-Clause).
