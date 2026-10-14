"""Catálogo inglés: menus (add-english-ui D2). Clave: texto en español; valor: inglés."""

EN: dict[str, str] = {
    # ---- bandeja (ui/tray.py) ----
    "Reconocer ahora": "Recognize now",
    "Calibrar nuevo perfil…": "Calibrate new profile…",
    "Descargar BattleLens {version}…": "Download BattleLens {version}…",
    "Copiar URL para OBS ({url})": "Copy URL for OBS ({url})",
    "Copiar URL para OBS": "Copy URL for OBS",
    "Ventana: {window}": "Window: {window}",
    "— selecciona una —": "— select one —",
    "Perfil: {profile}": "Profile: {profile}",
    "— calibra uno —": "— calibrate one —",
    "Detección automática": "Automatic detection",
    "Modo de la ficha": "Card mode",
    "Normal (aventura y captura)": "Normal (adventure and catching)",
    "Competitivo (combate)": "Competitive (battle)",
    "Modo stream (OBS)": "Stream mode (OBS)",
    "Ventana del emulador": "Emulator window",
    "Perfil activo": "Active profile",
    "Juego del perfil activo": "Active profile's game",
    "Regiones del perfil": "Profile regions",
    "Eliminar perfil activo…": "Delete active profile…",
    "Instalar OCR de Windows…": "Install Windows OCR…",
    "Ajustes…": "Settings…",
    "Abrir carpeta de datos": "Open data folder",
    "Descargar versión nueva…": "Download new version…",
    "Acerca de…": "About…",
    "Salir": "Quit",
    "(no hay ventanas)": "(no windows)",
    "(ninguno: calibra uno)": "(none: calibrate one)",
    "Recalibrar rival": "Recalibrate opponent",
    "2.º rival (combates dobles)": "2nd opponent (double battles)",
    "tu Pokémon": "your Pokémon",
    "menú de ataques": "moves menu",
    "Recalibrar {label}…": "Recalibrate {label}…",
    "Calibrar {label}…": "Calibrate {label}…",
    "Quitar {label}": "Remove {label}",
    "Sin especificar": "Unspecified",
    # ---- Ajustes (ui/settings.py) ----
    "Reconocer": "Recognize",
    "Calibrar": "Calibrate",
    "Ocultar ficha": "Hide card",
    "Cambiar de modo": "Switch mode",
    "Cambiar de forma": "Switch form",
    "Ficha del stream": "Stream card",
    "Automático (idioma de Windows)": "Automatic (Windows language)",
    "Ajustes de BattleLens": "BattleLens Settings",
    "p. ej. Ctrl+Alt+P": "e.g. Ctrl+Alt+P",
    "Guardar recortes de depuración": "Save debug crops",
    "Idioma de la interfaz:": "Interface language:",
    "Modo de la ficha:": "Card mode:",
    "Idioma de los datos Pokémon:": "Pokémon data language:",
    "Umbral de reconocimiento:": "Recognition threshold:",
    "Ocultar la ficha tras (0 = nunca):": "Hide the card after (0 = never):",
    "Reconocer al rival automáticamente": "Recognize the opponent automatically",
    "Intervalo de vigilancia:": "Polling interval:",
    "Ocultar al terminar el combate tras:": "Hide when the battle ends, after:",
    "Fuente de navegador para OBS": "Browser source for OBS",
    "Puerto (http://localhost:…/):": "Port (http://localhost:…/):",
    "Ficha del stream:": "Stream card:",
    "Comprobar una vez al día si hay versión nueva": "Check once a day for a new version",
    "Guardar reescribe config.toml con sus comentarios explicativos; "
    "los comentarios que hayas añadido a mano se perderán.":
        "Saving rewrites config.toml with its explanatory comments; "
        "any comments you added by hand will be lost.",
    "Atajos de teclado": "Keyboard shortcuts",
    "Ficha y reconocimiento": "Card and recognition",
    "Modo stream": "Stream mode",
    "Hay dos acciones con el mismo atajo.": "Two actions have the same shortcut.",
    # ---- calibración (ui/calibrator.py) ----
    "Dibuja un rectángulo que cubra el <b>{target}</b>; cuanto más ajustado, mejor "
    "(no pasa nada si incluye el nivel). "
    "<b>Enter</b> confirma · <b>Esc</b> cancela.":
        "Draw a rectangle over the <b>{target}</b>; the tighter, the better "
        "(it's fine if it includes the level). "
        "<b>Enter</b> confirms · <b>Esc</b> cancels.",
    "Primero dibuja un rectángulo sobre el nombre.": "First draw a rectangle over the name.",
    "Nuevo perfil": "New profile",
    "Sin especificar (formas originales, tabla actual)": "Unspecified (original forms, current type chart)",
    "Nombre del perfil:": "Profile name:",
    "Juego:": "Game:",
    # ---- Acerca de (ui/about.py) ----
    "Acerca de {app}": "About {app}",
    "Ficha instantánea del Pokémon rival en cualquier emulador.":
        "Instant card for the opposing Pokémon in any emulator.",
    "Licencia {license}. {attribution}.": "{license} License. {attribution}.",
    "Datos de Pokémon: PokéAPI (BSD-3-Clause)": "Pokémon data: PokéAPI (BSD-3-Clause)",
    "BattleLens es un proyecto de fans no oficial. No está afiliado ni respaldado por Nintendo, "
    "The Pokémon Company, Creatures Inc. ni GAME FREAK inc. Pokémon y los nombres de los Pokémon "
    "son marcas registradas de sus respectivos titulares.":
        "BattleLens is an unofficial fan project. It is not affiliated with or endorsed by Nintendo, "
        "The Pokémon Company, Creatures Inc. or GAME FREAK inc. Pokémon and Pokémon character names "
        "are trademarks of their respective owners.",
}
