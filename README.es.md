# BattleLens

[English](README.md) · **Español** · [Web](https://battlelens.minim-labs.app)

**Ficha instantánea del Pokémon rival para juegos de Pokémon en cualquier emulador de PC.**

Durante un combate, BattleLens muestra junto al emulador los tipos del rival, sus debilidades, resistencias e inmunidades, sus estadísticas base, sus habilidades (con su descripción al pasar el ratón), su ratio de captura y su cadena evolutiva, y cómo le va a tu Pokémon contra él.

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
2. **Calibra el juego** (una sola vez por juego): en un combate, pulsa `Ctrl+Alt+C`, dibuja un rectángulo que cubra el **nombre del rival** (cuanto más ajustado, mejor) y pulsa `Enter`. BattleLens propone el nombre del perfil y el juego a partir del título de la ventana.
   - Con el juego indicado, la ficha usa sus **formas regionales** (Alola, Galar, Hisui, Paldea) y los tipos y la tabla de eficacias de **su generación**.
   - Al cambiar de juego, el perfil correspondiente **se activa solo**.
   - Para cambiar el juego de un perfil: bandeja → **Juego del perfil activo**.
3. **En cada combate, la ficha aparece sola** junto al emulador en cuanto se ve el nombre del rival (**detección automática**) y se oculta unos segundos después de terminar el combate.
   - Si la desactivas desde la bandeja (**Detección automática**), pulsa `Ctrl+Alt+P` para reconocer a mano.
   - Haz clic en la ficha o pulsa `Ctrl+Alt+H` para ocultarla. Arrástrala para moverla.
4. **Elige el modo de la ficha** (bandeja → **Modo de la ficha**, `Ctrl+Alt+M` o Ajustes):
   - **Normal** (por defecto): ficha compacta para la aventura y la captura, con tipos, debilidades, **dificultad de captura** destacada, evolución y total de estadísticas.
   - **Competitivo**: todo lo anterior más el **nivel**, resistencias, **estadísticas reales a su nivel** (mínimo-máximo), **habilidades** con su descripción y su efecto («Levitación → Tierra ×0»), **movimientos probables** (los 4 últimos que aprende hasta su nivel en ese juego, marcando los que te hacen ×2), **quién es más rápido** y datos de **entrenamiento** (EVs, peso para Patada Baja, perfil). Para leer el nivel, calibra la región del rival **incluyendo el nivel**.
5. **Opcional: tu Pokémon y combates dobles.** En bandeja → **Regiones del perfil** puedes calibrar también el nombre de **tu Pokémon** y el del **2.º rival**:
   - Con tu Pokémon, cada ficha muestra **«Contra tu X»**: lo que le hacen tus tipos, lo que te hacen los suyos y un veredicto (**Ventaja / Neutral / Desventaja**). Si tu Pokémon tiene apodo, no se puede reconocer.
   - Con el 2.º rival, en los combates dobles aparecen dos fichas una al lado de la otra.

La interfaz de la app está en español; el contenido de la ficha (Pokémon, tipos, habilidades, movimientos) está disponible en español, inglés, francés, alemán e italiano (`overlay.language`).

### Configuración

Todo se puede cambiar desde bandeja → **Ajustes…** (los cambios se aplican al momento). Los mismos valores están en `%APPDATA%\BattleLens\config.toml`:

| Clave | Por defecto | Descripción |
|---|---|---|
| `hotkeys.recognize` / `calibrate` / `hide` | `Ctrl+Alt+P` / `C` / `H` | Atajos globales. Necesitan un modificador, porque las teclas F las usan los emuladores para los estados guardados |
| `recognition.threshold` | `80` | Puntuación mínima (0-100) para dar un nombre por reconocido |
| `recognition.debug` | `false` | Guarda en `debug/` cada recorte y lo que leyó el OCR |
| `detection.enabled` | `true` | Detección automática del combate (también desde la bandeja) |
| `detection.interval_ms` | `500` | Cada cuánto se vigila la región del nombre |
| `detection.hide_after_seconds` | `4` | Segundos sin ver al rival hasta ocultar la ficha (0 = nunca) |
| `overlay.mode` | `normal` | Ficha `normal` (compacta) o `competitive` (completa) |
| `hotkeys.toggle_mode` | `Ctrl+Alt+M` | Cambiar de modo |
| `overlay.language` | `es` | Idioma de la ficha: `es`, `en`, `fr`, `de`, `it` |
| `overlay.auto_hide_seconds` | `0` | Ocultar la ficha tras N segundos (0 = nunca) |
| `updates.check` | `true` | Avisar una vez al día si hay versión nueva en GitHub (única conexión de la app) |

### Si no reconoce bien

1. Pon `recognition.debug = true`, reinicia BattleLens y reconoce varios rivales.
2. En `%APPDATA%\BattleLens\debug\`, el archivo `*-recorte.png` debe contener solo el nombre. Si no, usa **Recalibrar perfil activo**.
3. Si el recorte es correcto y aun así falla, abre un [issue de tipo «Fallo»](https://github.com/minimorcy/battlelens/issues/new/choose): el formulario te pide la versión, el emulador y el juego, y te indica qué archivos adjuntar.

### Actualizaciones

BattleLens comprueba una vez al día si hay una versión nueva. Si la hay, te avisa y en la bandeja aparece **Descargar BattleLens X.Y.Z…**, que abre la página de descarga. Para instalarla, ejecuta el instalador nuevo: tus perfiles y ajustes se conservan. La comprobación se puede desactivar en **Ajustes**.

### Limitaciones conocidas

- **Formas no regionales** (megaevoluciones, Gigamax, formas de Rotom…): se muestra la forma original.
- **Lectura del nivel en juegos 3D:** en Pokémon Espada/Escudo el OCR no siempre lee el nivel (fuente grande), así que en modo Competitivo pueden faltar los movimientos probables y las estadísticas a su nivel. El modo Normal no lo necesita.
- **Movimientos probables:** son los que llevaría un Pokémon salvaje o de un entrenador corriente; los líderes, los rivales y los equipos competitivos pueden llevar otros.
- **Estadísticas a su nivel** con la fórmula de cada juego (Gen 1-2, Let's Go, Leyendas: Arceus y Gen 3 en adelante); Leyendas Z-A y Champions usan por ahora la de la Gen 3 en adelante.
- **La comparativa es por tipos** (ataques con STAB) y tiene en cuenta las habilidades que cambian la eficacia: si todas las que puede tener en ese juego hacen lo mismo (la Levitación de Flygon), se aplica; si solo alguna (Bronzong), la ficha avisa («si tiene Levitación»). No se tienen en cuenta los objetos ni las habilidades que ignoran otras (Rompemoldes).

### Desinstalar

Desde *Configuración → Aplicaciones → Aplicaciones instaladas → BattleLens*. Al desinstalar, se te pregunta si quieres borrar también tus perfiles.

---

## Para desarrolladores

Requisitos: Windows 10/11 y [uv](https://docs.astral.sh/uv/), que descarga Python 3.12 automáticamente.

```bash
uv sync
uv run battlelens                         # ejecutar desde el código
uv run pytest                             # tests (los de OCR se omiten si no hay paquete de OCR)
uv run python tools/build_dataset.py      # regenerar data/pokedex.json y learnsets.json desde PokéAPI
uv run python packaging/make_icon.py      # regenerar el icono
uv run python tools/make_site_screenshots.py   # regenerar las capturas de la web
uv run python packaging/build.py --self-test   # .exe + instalador (requiere Inno Setup 6) + ZIP
```

Estructura: `core/` (lógica pura), `vision/` (preprocesado), `platform/` (Win32, captura, OCR, atajos), `ui/`, `pipeline.py`, `app.py`. Empaquetado en `packaging/`; CI y publicación en `.github/workflows/`; web en `site/` (ver [docs/deploy-website.md](docs/deploy-website.md)).

### Publicar una versión

1. Actualiza `version` en `pyproject.toml` y añade su sección en `CHANGELOG.md` con fecha.
2. Haz commit, crea la etiqueta y súbela:
   ```bash
   git tag v0.2.0 && git push origin main v0.2.0
   ```
3. GitHub Actions ejecuta los tests, compila, hace la autocomprobación del `.exe` y publica la Release con el instalador, el ZIP y `SHA256SUMS.txt`.

El proyecto sigue un desarrollo guiado por especificaciones con [OpenSpec](https://github.com/Fission-AI/OpenSpec): cada cambio tiene su propuesta, especificaciones, diseño y tareas en `openspec/` (en español).

## Licencia y créditos

- Código: [MIT](LICENSE).
- Datos de Pokémon: [PokéAPI](https://github.com/PokeAPI/pokeapi) (BSD-3-Clause).
