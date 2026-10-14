"""Catálogo inglés: app (add-english-ui D2). Clave: texto en español; valor: inglés."""

EN: dict[str, str] = {
    # ---- app.py: avisos de arranque ----
    "reconocer": "recognize",
    "calibrar": "calibrate",
    "ocultar": "hide",
    "cambiar de modo": "switch mode",
    "cambiar de forma": "switch form",
    "ficha del stream": "stream card",
    "inválido": "invalid",
    "No se pudieron registrar los atajos: {detail}. Cámbialos en config.toml.":
        "Couldn't register the shortcuts: {detail}. Change them in config.toml.",
    "Falta el OCR de Windows. Instálalo desde el menú de la bandeja: «Instalar OCR de Windows…».":
        'Windows OCR is missing. Install it from the tray menu: "Install Windows OCR…".',
    "Selecciona la ventana del emulador en el menú de la bandeja.": "Select the emulator window in the tray menu.",
    "Calibra un perfil para este juego (menú de la bandeja o atajo de calibrar).":
        "Calibrate a profile for this game (tray menu or the calibrate shortcut).",
    "Listo. Pulsa {hotkey} en un combate.": "Ready. Press {hotkey} during a battle.",
    # ---- app.py: OCR ----
    "Instalar OCR de Windows": "Install Windows OCR",
    "Se instalará el reconocimiento de texto de Windows ({tag}).\n\n"
    "Windows pedirá permiso de administrador y la descarga puede tardar unos minutos.":
        "Windows text recognition ({tag}) will be installed.\n\n"
        "Windows will ask for administrator permission and the download may take a few minutes.",
    "Instalando el OCR de Windows… Te aviso al terminar.": "Installing Windows OCR… You'll be notified when it's done.",
    "Instalación cancelada.": "Installation cancelled.",
    "OCR de Windows": "Windows OCR",
    "No se pudo instalar el OCR ({tag}).\n\n{instructions}": "Couldn't install the OCR ({tag}).\n\n{instructions}",
    "OCR instalado. Ya puedes reconocer con {hotkey}.": "OCR installed. You can now recognize with {hotkey}.",
    "OCR instalado. Reinicia BattleLens para empezar a usarlo.": "OCR installed. Restart BattleLens to start using it.",
    # ---- app.py: ajustes, stream y actualizaciones ----
    "No se pudieron registrar los atajos: {names}.": "Couldn't register the shortcuts: {names}.",
    "Ajustes guardados.": "Settings saved.",
    "El puerto {port} está ocupado: cámbialo en Ajustes.": "Port {port} is in use: change it in Settings.",
    "Modo stream activo. Añade en OBS una fuente de navegador con {url}":
        "Stream mode on. In OBS, add a browser source with {url}",
    "URL copiada: {url}": "URL copied: {url}",
    "BattleLens {version} disponible. Descárgala desde el menú de la bandeja.":
        "BattleLens {version} is available. Download it from the tray menu.",
    "Ficha: Competitivo": "Card: Competitive",
    "Ficha: Normal": "Card: Normal",
    # ---- app.py: reconocimiento y perfiles ----
    "Selecciona primero la ventana del emulador.": "Select the emulator window first.",
    "No hay perfiles: calibra primero la región del nombre.": "No profiles yet: calibrate the name region first.",
    "Error inesperado: {error}": "Unexpected error: {error}",
    "Perfil «{name}» activado ({game}).": 'Profile "{name}" activated ({game}).',
    "sin especificar": "not specified",
    "Juego de «{name}»: {game}.": 'Game for "{name}": {game}.',
    "Calibrar nuevo perfil": "Calibrate new profile",
    "Mi juego": "My game",
    "Perfil «{name}» creado y activo.": 'Profile "{name}" created and active.',
    "nombre del Pokémon rival": "opponent Pokémon's name",
    "nombre del 2.º Pokémon rival": "2nd opponent Pokémon's name",
    "nombre de tu Pokémon": "your Pokémon's name",
    "menú de ataques (los 4 movimientos)": "move menu (the 4 moves)",
    "«{name}»: {target}": '"{name}": {target}',
    "«{name}»: región del {target} guardada.": '"{name}": {target} region saved.',
    "«{name}»: región del {target} quitada.": '"{name}": {target} region removed.',
    "Eliminar perfil": "Delete profile",
    "¿Eliminar el perfil «{name}»?": 'Delete the profile "{name}"?',
    "La aplicación ya se está ejecutando (mira la bandeja).": "The app is already running (check the system tray).",
    # ---- core/profiles.py ----
    "La región mide {width}×{height} px; el mínimo es {min} px de ancho y de alto.":
        "The region is {width}×{height} px; the minimum is {min} px wide and high.",
    "La región debe contener números": "The region must contain numbers",
    "Las coordenadas de la región deben estar en [0, 1]": "The region coordinates must be within [0, 1]",
    "La región debe tener ancho y alto positivos": "The region must have a positive width and height",
    "La región se sale del área cliente": "The region extends beyond the client area",
    "El perfil necesita un nombre": "The profile needs a name",
    "El perfil necesita al menos un idioma de OCR": "The profile needs at least one OCR language",
    "La región del rival es obligatoria": "The opponent region is required",
    "Perfil con formato inválido: {error}": "Invalid profile format: {error}",
    # ---- core/config.py ----
    "config.toml no es TOML válido: {error}": "config.toml is not valid TOML: {error}",
    "{name} debe ser un texto": "{name} must be a string",
    "{key} debe estar entre {low} y {high}": "{key} must be between {low} and {high}",
    "{key} debe ser uno de: {values}": "{key} must be one of: {values}",
    "{key} debe ser true o false": "{key} must be true or false",
    "{key} debe ser un entero entre {low} y {high}": "{key} must be an integer between {low} and {high}",
    "{key} debe ser un número >= 0": "{key} must be a number >= 0",
    # ---- platform ----
    "La ventana del emulador ya no está disponible. Selecciónala de nuevo.":
        "The emulator window is no longer available. Select it again.",
    "La ventana del emulador está minimizada.": "The emulator window is minimized.",
    "Atajo vacío": "Empty shortcut",
    "Modificador desconocido «{modifier}» en «{shortcut}»": 'Unknown modifier "{modifier}" in "{shortcut}"',
    "Tecla desconocida «{key}» en «{shortcut}»": 'Unknown key "{key}" in "{shortcut}"',
    "«{shortcut}» necesita al menos un modificador (Ctrl, Alt, Shift o Win); "
    "las teclas solas, como las F, las usa el emulador.":
        '"{shortcut}" needs at least one modifier (Ctrl, Alt, Shift or Win); '
        "keys on their own, like the F keys, are used by the emulator.",
    "No hay OCR de Windows para los idiomas {requested} (instalados: {installed}). "
    "Instala el paquete en Configuración > Hora e idioma > Idioma y región > añadir idioma, "
    "o en PowerShell como administrador: "
    'Add-WindowsCapability -Online -Name "Language.OCR~~~{tag}~0.0.1.0"':
        "No Windows OCR for the languages {requested} (installed: {installed}). "
        "Install the package in Settings > Time & language > Language & region > Add a language, "
        "or in PowerShell as administrator: "
        'Add-WindowsCapability -Online -Name "Language.OCR~~~{tag}~0.0.1.0"',
    "ninguno": "none",
    "Instálalo a mano en Configuración > Hora e idioma > Idioma y región: añade (o abre las opciones de) "
    "tu idioma y marca «Reconocimiento óptico de caracteres».":
        "Install it manually in Settings > Time & language > Language & region: add (or open the options of) "
        'your language and check "Optical character recognition".',
    "Los menús cambiarán de idioma al reiniciar BattleLens.": "Menus will switch language when BattleLens restarts.",
    'Creando el informe…': 'Creating the report…',
    'No se pudo crear el informe: {error}': 'Could not create the report: {error}',
    'Informe creado: {path}': 'Report created: {path}',
}
