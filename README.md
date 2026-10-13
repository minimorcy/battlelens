# BattleLens

**English** · [Español](README.es.md) · [Website](https://battlelens.minim-labs.app)

**Instant info card for your opponent in Pokémon games, on any PC emulator.**

During a battle, BattleLens shows next to the emulator your opponent's types, weaknesses, resistances and immunities, base stats, abilities (with their description on hover), catch rate and evolution chain, plus how your own Pokémon fares against it.

It doesn't read the emulator's memory: it reads **the opponent's name on screen** with Windows' built-in OCR. That's why it works with any emulator (mGBA, DeSmuME, melonDS, Citra…) and any generation, after a one-time calibration per game.

> BattleLens is an unofficial fan project. It is not affiliated with, endorsed, sponsored or approved by Nintendo, The Pokémon Company, Creatures Inc. or GAME FREAK inc. Pokémon and Pokémon character names are trademarks of their respective owners.

---

## For players

### Installation

1. Go to [**Releases**](https://github.com/minimorcy/battlelens/releases/latest) and download `BattleLens-Setup-x.y.z.exe`.
   - Rather not install anything? Download `BattleLens-x.y.z-portable.zip`, unzip it and run `BattleLens.exe`.
2. Run the installer. **No administrator rights needed.**
3. **SmartScreen warning.** If Windows shows "Windows protected your PC", click **More info → Run anyway**. It appears because the executable isn't signed with a paid certificate. To verify the download, compare it with `SHA256SUMS.txt`:
   ```powershell
   Get-FileHash .\BattleLens-Setup-x.y.z.exe -Algorithm SHA256
   ```

Requirements: 64-bit Windows 10 (version 2004 or later) or 11.

### Windows OCR

BattleLens uses the text recognition that ships with Windows. Almost every PC already has it for its language. If it's missing, the app tells you on startup and offers **"Install Windows OCR…"** (*Instalar OCR de Windows…*) in its menu; Windows will ask for permission to install it.

### Usage

1. Find the BattleLens icon in the system tray (next to the clock) and choose **Emulator window** (*Ventana del emulador*).
2. **Calibrate the game** (once per game): during a battle, press `Ctrl+Alt+C`, draw a rectangle around the **opponent's name** (the tighter, the better) and press `Enter`. BattleLens suggests the profile name and the game from the window title.
   - With the game set, the card uses its **regional forms** (Alola, Galar, Hisui, Paldea) and the types and type chart of **its generation**.
   - When you switch games, the matching profile **is activated automatically**.
   - To change a profile's game: tray → **Active profile's game** (*Juego del perfil activo*).
3. **In every battle the card appears by itself** next to the emulator as soon as the opponent's name is visible (**automatic detection**), and hides a few seconds after the battle ends.
   - If you turn it off from the tray (**Automatic detection** / *Detección automática*), press `Ctrl+Alt+P` to recognise manually.
   - Click the card or press `Ctrl+Alt+H` to hide it. Drag it to move it.
   - **Mega Evolutions and other forms** (Rotom, Deoxys, Giratina…) show the same name on screen, so press `Ctrl+Alt+F` to cycle through the forms available in that game; the card is recalculated and keeps that form while the Pokémon stays in battle.
4. **Choose the card mode** (tray → **Card mode** / *Modo de la ficha*, `Ctrl+Alt+M` or *Ajustes*):
   - **Normal** (default): a compact card for adventuring and catching, with types, weaknesses, highlighted **catch difficulty**, evolution and stat total.
   - **Competitive**: everything above plus the **level**, resistances, **actual stats at its level** (min–max), **abilities** with their description and effect ("Levitate → Ground ×0"), **likely moves** (the last 4 it learns up to its level in that game, flagging the ones that hit you ×2), **who's faster** and **training** data (EVs, weight for Low Kick, stat profile). To read the level, calibrate the opponent's region **including the level**.
5. **Optional: your Pokémon and double battles.** In tray → **Profile regions** (*Regiones del perfil*) you can also calibrate the name of **your Pokémon** and of the **2nd opponent**:
   - With your Pokémon, each card shows **"Against your X"** (*Contra tu X*): what your types do to it, what its types do to you, and a verdict (**Advantage / Neutral / Disadvantage** — *Ventaja / Neutral / Desventaja*). Nicknamed Pokémon can't be recognised.
   - With the 2nd opponent, double battles show two cards side by side.

The app's interface is currently in Spanish (menu names are given in *italics* above); the card content (Pokémon, types, abilities, moves) is available in English, Spanish, French, German and Italian (`overlay.language`).

### Configuration

Everything can be changed from tray → **Settings…** (*Ajustes…*) (changes apply immediately). The same values live in `%APPDATA%\BattleLens\config.toml`:

| Key | Default | Description |
|---|---|---|
| `hotkeys.recognize` / `calibrate` / `hide` | `Ctrl+Alt+P` / `C` / `H` | Global hotkeys. They need a modifier, because emulators use the F keys for save states |
| `recognition.threshold` | `80` | Minimum score (0-100) to accept a recognised name |
| `recognition.debug` | `false` | Saves every crop and what the OCR read into `debug/` |
| `detection.enabled` | `true` | Automatic battle detection (also from the tray) |
| `detection.interval_ms` | `500` | How often the name region is checked |
| `detection.hide_after_seconds` | `4` | Seconds without seeing the opponent before hiding the card (0 = never) |
| `overlay.mode` | `normal` | `normal` (compact) or `competitive` (full) card |
| `hotkeys.toggle_mode` | `Ctrl+Alt+M` | Switch mode |
| `hotkeys.cycle_form` | `Ctrl+Alt+F` | Cycle the opponent's form (Mega Evolutions, Rotom…) |
| `overlay.language` | `es` | Card language: `es`, `en`, `fr`, `de`, `it` |
| `overlay.auto_hide_seconds` | `0` | Hide the card after N seconds (0 = never) |
| `updates.check` | `true` | Check once a day for a new version on GitHub (the app's only network connection) |

### If recognition fails

1. Set `recognition.debug = true`, restart BattleLens and recognise a few opponents.
2. In `%APPDATA%\BattleLens\debug\`, the `*-recorte.png` file should contain only the name. If not, use **Recalibrate opponent** (*Regiones del perfil → Recalibrar rival*).
3. If the crop looks right and it still fails, open a ["Bug" issue](https://github.com/minimorcy/battlelens/issues/new/choose): the form asks for the version, emulator and game, and tells you which files to attach.

### Updates

BattleLens checks once a day whether there's a new version. If there is, it lets you know and the tray shows **Download BattleLens X.Y.Z…** (*Descargar BattleLens X.Y.Z…*), which opens the download page. To install it, run the new installer: your profiles and settings are kept. The check can be turned off in **Settings**.

### Known limitations

- **Non-regional forms** (Mega Evolutions, Rotom forms…) can't be told apart by name: choose them with `Ctrl+Alt+F`. Gigantamax isn't listed because it doesn't change types or stats.
- **Level reading:** the level is only read if the calibrated region includes it. BattleLens retries with extra variants and a zoomed-in read of the right half, and tolerates digits misread as letters ("Nv. 1G"), but if it still can't read it, Competitive mode shows the card without likely moves or stats at its level. Normal mode doesn't need it.
- **Likely moves** are what a wild Pokémon or an ordinary trainer's Pokémon would know; gym leaders, rivals and competitive teams may carry others.
- **Stats at its level** use each game's formula (Gen 1-2, Let's Go, Legends: Arceus and Gen 3+); Legends Z-A and Champions use the Gen 3+ one for now.
- **The matchup is type-based** (STAB attacks) and accounts for abilities that change effectiveness: when every ability the Pokémon can have in that game does the same thing (Flygon's Levitate), it's applied; when only some do (Bronzong), the card warns you ("if it has Levitate"). Held items and abilities that ignore others (Mold Breaker) aren't considered.

### Uninstall

From *Settings → Apps → Installed apps → BattleLens*. When uninstalling, you're asked whether to delete your profiles too.

---

## For developers

Requirements: Windows 10/11 and [uv](https://docs.astral.sh/uv/), which downloads Python 3.12 automatically.

```bash
uv sync
uv run battlelens                         # run from source
uv run pytest                             # tests (OCR tests are skipped without an OCR language pack)
uv run python tools/build_dataset.py      # regenerate data/pokedex.json and learnsets.json from PokéAPI
uv run python packaging/make_icon.py      # regenerate the icon
uv run python tools/make_site_screenshots.py   # regenerate the website screenshots
uv run python packaging/build.py --self-test   # .exe + installer (needs Inno Setup 6) + ZIP
```

Layout: `core/` (pure logic), `vision/` (preprocessing), `platform/` (Win32, capture, OCR, hotkeys), `ui/`, `pipeline.py`, `app.py`. Packaging in `packaging/`; CI and releases in `.github/workflows/`; website in `site/` (see [docs/deploy-website.md](docs/deploy-website.md)).

### Publishing a release

1. Bump `version` in `pyproject.toml` and add its dated section to `CHANGELOG.md`.
2. Commit, create the tag and push it:
   ```bash
   git tag v0.2.0 && git push origin main v0.2.0
   ```
3. GitHub Actions runs the tests, builds, self-tests the `.exe` and publishes the Release with the installer, the ZIP and `SHA256SUMS.txt`.

The project follows spec-driven development with [OpenSpec](https://github.com/Fission-AI/OpenSpec): every change has its proposal, specs, design and tasks in `openspec/` (written in Spanish).

## License and credits

- Code: [MIT](LICENSE).
- Pokémon data: [PokéAPI](https://github.com/PokeAPI/pokeapi) (BSD-3-Clause).
