# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/); versionado [SemVer](https://semver.org/lang/es/).

## [Unreleased]

## [0.7.0] - 2026-11-13

### Añadido
- Flechas ◀ ▶ junto al nombre de la ficha para cambiar de forma con el ratón (Rotom, megaevoluciones…), útiles cuando el juego solo muestra el nombre de la especie. En combates dobles cambian la forma de esa tarjeta. `Ctrl+Alt+F` sigue funcionando.
- Modo panel para jugar con dos pantallas: en Ajustes › Ficha → «Mostrar la ficha en: Panel», la ficha y la tabla de tipos pasan a una ventana normal (con marco, redimensionable, sin estar siempre encima) que puedes llevar al otro monitor. A la izquierda la ficha, a la derecha la tabla de tipos resaltada y ajustada al espacio; fuera del combate muestra «Esperando combate…». Recuerda su sitio y tamaño, y si la cierras vuelve con la siguiente ficha o con «Mostrar el panel» en la bandeja.

### English

**Added**
- ◀ ▶ arrows next to the card's name to switch form with the mouse (Rotom, Mega Evolutions…), handy when the game only shows the species name. In double battles they switch that card's form. `Ctrl+Alt+F` still works.
- Panel mode for two-screen setups: in Settings › Card → "Show the card in: Panel", the card and the type chart move into a regular window (framed, resizable, not always on top) you can put on your other monitor. The card is on the left and the highlighted type chart on the right, sized to fit; outside battles it shows "Waiting for a battle…". It remembers its position and size, and if you close it, it comes back with the next card or from "Show the panel" in the tray.

## [0.6.1] - 2026-11-13

### Corregido
- La ficha ya no se oculta y vuelve a aparecer en mitad del combate cuando la cámara mueve el fondo detrás del nombre del rival: antes de ocultarla, la detección vuelve a leer el nombre y solo la oculta si el rival ya no está.

### English

**Fixed**
- The card no longer hides and reappears mid-battle when the camera moves the background behind the opponent's name: before hiding it, detection reads the name again and only hides it if the opponent is gone.

## [0.6.0] - 2026-11-12

### Añadido
- Buscador de Pokémon: pulsa `Ctrl+Alt+B` (o bandeja → «Buscar Pokémon…») en cualquier momento, escribe un nombre y verás su ficha con el juego del perfil activo. Sugiere nombres mientras escribes, con sus tipos en píldoras y una entrada por forma (Rapidash y Rapidash de Galar, megaevoluciones…) según el juego, y acepta nombres en otros idiomas, sin tildes o con erratas pequeñas. La búsqueda no cambia la ficha del stream. El atajo se cambia en Ajustes › Atajos.
- Tabla de tipos: `Ctrl+Alt+T` (o bandeja → «Tabla de tipos») muestra una chuleta flotante con la tabla de la generación del juego del perfil activo (15, 17 o 18 tipos y sus excepciones). Con una ficha en pantalla, resalta las columnas de los tipos del rival (de los dos en dobles) y, si el perfil lee tu Pokémon, sus tipos como filas en amarillo, con las casillas de cruce marcadas. Se reescala con el tirador de su esquina o con `Ctrl` + rueda y recuerda su sitio y tamaño. El OCR no la ve.

### Cambiado
- Modificar un perfil en vez de crear otro: con un perfil activo, `Ctrl+Alt+C` pregunta qué región recalibrar (Rival, 2.º rival, Tu Pokémon o Menú de ataques) o si crear un perfil nuevo. En Ajustes › Perfiles → Perfil activo se puede cambiar el nombre y reaplicar un preset («Aplicar un preset…») conservando el perfil. La bandeja tiene «Modificar o crear perfil…», que hace lo mismo que el atajo.

### Quitado
- La comparación de velocidad («Eres más rápido», «Depende de IVs/EVs»…) de la sección «Contra tu…» de la ficha competitiva: sin conocer los IVs ni los EVs del rival podía equivocarse. Sus estadísticas reales a su nivel siguen en la ficha.

### English

**Added**
- Pokémon search: press `Ctrl+Alt+B` (or tray → "Search Pokémon…") at any time, type a name and see its card for the active profile's game. It suggests names as you type, with their types as pills and one entry per form (Rapidash and Galarian Rapidash, Mega Evolutions…) for the game, and accepts names in other languages, without accents or with small typos. Searches don't change the stream card. Change the shortcut in Settings → Shortcuts.
- Type chart: `Ctrl+Alt+T` (or tray → "Type chart") shows a floating cheat sheet with the chart for the active profile's game generation (15, 17 or 18 types and their exceptions). With a card on screen, it highlights the opponent's type columns (both opponents' in doubles) and, if the profile reads your Pokémon, its types as yellow rows, with the crossing cells marked. Resize it with its corner grip or `Ctrl` + mouse wheel; it remembers its place and size. The OCR can't see it.

**Changed**
- Edit a profile instead of creating another: with an active profile, `Ctrl+Alt+C` asks which region to recalibrate (Opponent, 2nd opponent, Your Pokémon or Moves menu) or whether to create a new profile. In Settings → Profiles → Active profile you can rename it and re-apply a preset ("Apply a preset…") keeping the profile. The tray has "Edit or create profile…", which does the same as the shortcut.

**Removed**
- The speed comparison ("You are faster", "Depends on IVs/EVs"…) from the competitive card's "Against your…" section: without knowing the opponent's IVs and EVs it could be wrong. Its actual stats at its level are still on the card.

## [0.5.0] - 2026-11-12

### Añadido
- Pantalla de inicio al abrir la app: eliges la ventana del emulador, el perfil (o creas uno con un preset), el modo de la ficha y la detección automática, y pulsas «Empezar». Se puede quitar en Ajustes › General.
- «Fuerte contra» en las eficacias de la ficha (también la del stream): los tipos a los que el rival hace ×2 con los ataques de su propio tipo, según la generación del juego.

### Cambiado
- La detección automática solo muestra la ficha si lee el nivel junto al nombre del rival, como en la pantalla de combate: ya no salta en la Pokédex ni en los datos de tus Pokémon. Se desactiva en Ajustes › Reconocimiento → «Solo en la pantalla de combate» (para regiones sin el nivel).

### Corregido
- A veces la ficha no salía sola porque dos lecturas de OCR coincidían (la del rival y la del menú de ataques) y una fallaba con «Another RecognizeAsync operation is already running». Ahora se hacen por turnos.
- En los combates dobles, las fichas salían al revés que los Pokémon en el campo si el recuadro del 2.º rival estaba a la izquierda del primero. Ahora siguen el orden de los recuadros en la pantalla.

### English

**Added**
- Start screen when the app opens: pick the emulator window, the profile (or create one from a preset), the card mode and automatic detection, then click "Start". It can be turned off in Settings → General.
- "Strong against" in the card's type matchups (the stream card too): the types the opponent hits ×2 with its own-type attacks, using the game's generation.

**Changed**
- Automatic detection only shows the card when it reads the level next to the opponent's name, as on the battle screen: it no longer pops up in the Pokédex or on your Pokémon's summary. Turn it off in Settings → Recognition → "Only on the battle screen" (for regions without the level).

**Fixed**
- Sometimes the card didn't show up by itself because two OCR reads overlapped (the opponent's and the moves menu's) and one failed with "Another RecognizeAsync operation is already running". They now take turns.
- In double battles, the cards were swapped compared with the Pokémon on the field when the 2nd opponent's box was left of the first one. They now follow the order of the boxes on screen.

## [0.4.0] - 2026-10-16

### Añadido
- Guía de uso en la web (`guide.html`), en español e inglés y con capturas de la app: instalación, cómo preparar el emulador (qué captura y pantalla completa sin bordes), presets, calibración, la ficha y sus modos, dobles, formas, ajustes, OBS y solución de problemas. «Leer la guía» lleva ahí.

### Cambiado
- Ficha rediseñada (también la del stream): cabecera con el nombre y los tipos en color pleno, secciones en bloques, tipos en pastillas suaves y multiplicadores en verde, rojo o gris según lo que suponen para ti. La captura se muestra con un medidor y las estadísticas, en una sola gama con la más alta y la más baja resaltadas.
- Las secciones de la ficha se pliegan con un clic en su título (lo plegado se recuerda en cada modo).
- Ficha a medida: en Ajustes › Ficha eliges qué secciones ves en el modo Normal y en el Competitivo (contra tu Pokémon, eficacias, estadísticas, movimientos, evolución…); la ficha del stream sigue la misma elección. Por defecto la ficha es mínima: Normal solo con las eficacias y Competitivo con eficacias y estadísticas.
- La ficha se cierra con el botón ✕ de su esquina superior derecha; un clic en el resto ya no la oculta.
- Ajustes rediseñados: ventana con barra lateral (General, Ficha, Reconocimiento, Atajos, Modo stream, Perfiles y Acerca de) y tema oscuro como el de la ficha. «Guardar» no cierra la ventana y solo se activa si hay cambios; al cerrar con cambios pendientes se pregunta. La ventana no es modal: la detección sigue funcionando mientras está abierta.
- Los perfiles se gestionan en Ajustes › Perfiles: ventana del emulador, perfil activo, juego, estado de cada región con sus botones para calibrar o quitar, perfil nuevo (con preset o a mano) y eliminar.
- Bandeja más corta, con las opciones rápidas: el juego del perfil, las regiones, «Calibrar nuevo perfil…», «Eliminar perfil activo…», «Abrir carpeta de datos» y «Acerca de…» pasan a Ajustes. Nuevo «Gestionar perfiles…» en el submenú «Perfil activo»; el doble clic en el icono abre Ajustes.
- Logo nuevo: una lupa con un rayo, dibujado en vectorial (`packaging/logo.svg`); de él salen el icono de la app, el del instalador y los de la web.
- Web rediseñada: captura anotada, comparativa, sección para streamers, preguntas frecuentes y novedades de la 0.3.
- Web preparada para buscadores y redes: imagen propia al compartir el enlace (X, Discord, WhatsApp…), título y descripción con palabras clave, datos estructurados, `robots.txt` y `sitemap.xml`.

### Corregido
- La app se cerraba al cambiar de perfil (desde la bandeja, Ajustes o al cambiar de juego) con la detección automática activa, si los perfiles tenían distinto número de regiones. Los errores inesperados ahora quedan en `app.log` en lugar de cerrar la app sin aviso.
- Con el emulador a pantalla completa, la ficha quedaba detrás de él. Con pantalla completa exclusiva no se puede mostrar nada encima: la guía explica cómo cambiar a ventana sin bordes.
- Ctrl+C en la consola vuelve a cerrar la app.
- «Calibrar a mano» solo pedía la región del rival: ahora pide también, opcionales, la de tu Pokémon y la del menú de ataques, con «Volver a capturar» para abrir antes el menú de Luchar (también al recalibrar una región).
- Al pasar el emulador de pantalla completa a maximizado (o al revés), las regiones dejaban de caer sobre los nombres. Los perfiles creados con un preset recuerdan dónde estaba la imagen del juego y las regiones la siguen; los anteriores hay que volver a crearlos con un preset.

### English

**Added**
- User guide on the website (`guide.html`), in English and Spanish with screenshots of the app: installing, setting up the emulator (what it captures and borderless fullscreen), presets, calibration, the card and its modes, doubles, forms, settings, OBS and troubleshooting. "Read the guide" now goes there.

**Changed**
- Redesigned card (the stream card too): header with the name and the types in solid color, sections in blocks, other types as soft pills and multipliers in green, red or grey depending on what they mean for you. The catch rate has a meter and the stats use a single color range with the highest and lowest highlighted.
- Card sections collapse with a click on their title (remembered per mode).
- Custom card: in Settings → Card you choose which sections you see in Normal and Competitive mode (against your Pokémon, effectiveness, stats, moves, evolution…); the stream card follows the same choice. By default the card is minimal: Normal shows only effectiveness and Competitive shows effectiveness and stats.
- The card closes with the ✕ button in its top-right corner; clicking anywhere else no longer hides it.
- Redesigned Settings: a window with a sidebar (General, Card, Recognition, Shortcuts, Stream mode, Profiles and About) and a dark theme matching the card. "Save" no longer closes the window and is only enabled when something changed; closing with pending changes asks first. The window is not modal: detection keeps working while it is open.
- Profiles are managed in Settings → Profiles: emulator window, active profile, game, the status of each region with buttons to calibrate or remove it, new profile (from a preset or manually) and delete.
- Shorter tray menu with the quick options: the profile's game, regions, "Calibrate new profile…", "Delete active profile…", "Open data folder" and "About…" move to Settings. New "Manage profiles…" in the "Active profile" submenu; double-clicking the icon opens Settings.
- New logo: a magnifying glass with a lightning bolt, drawn as a vector (`packaging/logo.svg`); the app, installer and website icons are generated from it.
- Redesigned website: annotated screenshot, comparison, streamer section, FAQ and what's new in 0.3.
- Website ready for search engines and social media: its own preview image when sharing the link (X, Discord, WhatsApp…), keyword-rich title and description, structured data, `robots.txt` and `sitemap.xml`.

**Fixed**
- The app closed when switching profiles (from the tray, Settings or by changing games) with automatic detection on, if the profiles had a different number of regions. Unexpected errors are now written to `app.log` instead of closing the app without notice.
- With the emulator in fullscreen, the card stayed behind it. Nothing can be shown over exclusive fullscreen: the guide explains how to switch to borderless windowed.
- Ctrl+C in the console closes the app again.
- "Calibrate manually" only asked for the opponent's region: it now also asks, optionally, for your Pokémon's and the moves menu, with "Capture again" so you can open the Fight menu first (also when recalibrating a region).
- Switching the emulator between fullscreen and maximized made the regions miss the names. Profiles created from a preset remember where the game image was and the regions follow it; older profiles need to be created again from a preset.

## [0.3.0] - 2026-10-14

### Añadido
- «Nuevo perfil con un preset…»: regiones ya medidas para los juegos de GB, GBA, DS y Espada/Escudo; BattleLens localiza la imagen del juego en la ventana del emulador y muestra los recuadros y lo que lee para confirmarlos antes de guardar. Es la propuesta del primer arranque.
- «Informar de un problema…» en la bandeja: crea un ZIP con la configuración, los perfiles, el registro y una captura del emulador con lo que lee BattleLens en cada región (sin datos personales en los textos y sin enviar nada) y abre el formulario de fallo de GitHub ya rellenado, ahora bilingüe.
- Interfaz en inglés: menús, avisos, diálogos y textos de la ficha (y de la del stream) en español o inglés, según el idioma de Windows o elegido en Ajustes; independiente del idioma de los datos Pokémon.
- Modo stream (opcional): fuente de navegador para OBS en `http://localhost:17320/` con la ficha sobre fondo transparente, que se actualiza con cada rival y se oculta al terminar el combate; atajo `Ctrl+Alt+S` para mostrarla u ocultarla, «Copiar URL para OBS» en la bandeja y sección en Ajustes.

### Cambiado
- Mejor reconocimiento con las fuentes pixeladas de GBA/DS: la «A» leída como «R» o la «D» como «O» ya no impiden reconocer el nombre.

### English

**Added**
- "New profile from a preset…": ready-made regions for GB, GBA, DS and Sword/Shield games. BattleLens finds the game image in the emulator window and shows the boxes and what it reads, so you can confirm them before saving. It's what the first run suggests.
- "Report a problem…" in the tray: creates a ZIP with your settings, profiles, log and a capture of the emulator with what BattleLens reads in each region (no personal data in the text files, nothing is sent) and opens the GitHub bug form already filled in, now bilingual.
- English interface: menus, notices, dialogs and card labels (also on the stream card) in English or Spanish, following the Windows language or chosen in Settings; independent of the Pokémon data language.
- Stream mode (optional): a browser source for OBS at `http://localhost:17320/` with the card on a transparent background, updated with every opponent and hidden when the battle ends; `Ctrl+Alt+S` shows/hides it, "Copy URL for OBS" in the tray and a section in Settings.

**Changed**
- Better recognition with the pixel fonts of GBA/DS: an "A" read as "R" or a "D" read as "O" no longer prevents recognizing the name.

## [0.2.1] - 2026-10-13

### Añadido
- Las habilidades que cambian la eficacia (Levitación, Absorbe Agua, Superguarda…) se aplican a las debilidades y a «Contra tu X» si son seguras, y se avisan si son solo posibles. Las habilidades son las de la generación del juego (Gengar con Levitación hasta la Gen 6).
- Estadísticas base de la generación del juego (la «Especial» única de la Gen 1, los valores anteriores a la Gen 6) y rangos a su nivel con la fórmula de cada juego (Gen 1-2, Let's Go y Leyendas: Arceus).
- Megaevoluciones, regresiones primigenias y formas alternativas (Rotom, Deoxys, Giratina, Necrozma…) según el juego, en «Otras formas», con el atajo `Ctrl+Alt+F` para elegir la forma del rival.
- «Tus movimientos»: con la nueva región del menú de ataques, BattleLens lee los movimientos de tu Pokémon, los recuerda por especie y muestra en cada ficha cuánto le hace cada uno al rival (o los probables según su nivel mientras no se han leído).

### Cambiado
- El nivel se lee con más fiabilidad: si el nombre se reconoce sin nivel, se reintenta con más variantes y con la mitad derecha ampliada, y se toleran dígitos leídos como letras («Nv. 1G»).

### Corregido
- Al cambiar de modo, de forma o al leerse tus movimientos con la ficha abierta, esta se quedaba en un rectángulo diminuto.

## [0.2.0] - 2026-10-13

### Añadido
- Instalador para Windows (sin permisos de administrador) y versión portable.
- Instalación guiada del paquete de OCR de Windows cuando falta.
- Ventana «Acerca de» con versión, licencia y avisos.
- Publicación automática de versiones con GitHub Actions.
- Formas regionales (Alola, Galar, Hisui, Paldea), tipos y tabla de eficacias según la generación del juego.
- Juego por perfil, detectado por el título de la ventana, y activación automática del perfil al cambiar de juego.
- Captura del emulador aunque esté tapado por otras ventanas.
- Detección automática del combate: la ficha aparece y se oculta sola, sin pulsar ninguna tecla.
- Combates dobles (dos fichas) y comparativa «Contra tu X» con veredicto de ventaja/desventaja.
- Ratio de captura con su dificultad, cadena evolutiva y descripción de las habilidades.
- Ventana de ajustes (sin editar archivos) y aviso de versión nueva.
- Web del proyecto (inglés/español) y README en inglés, con analítica opcional de Umami (sin cookies).
- Modos de ficha: **Normal** (compacta, aventura y captura) y **Competitivo** (nivel, estadísticas reales, movimientos probables, velocidad, habilidades y entrenamiento).

### Cambiado
- El proyecto pasa a llamarse **BattleLens**.
- Preprocesado sin OpenCV (descarga mucho más pequeña).
- Icono propio.
- Mejor reconocimiento en juegos 3D (Switch/3DS) y con regiones holgadas.

### Corregido
- En combates dobles con escalado de pantalla alto (150-200 %), los textos largos de la ficha se recortaban.
- La ficha competitiva no cabía en pantallas de 720-768 px de alto: ahora se ajusta a la pantalla y se desplaza con la rueda.

## [0.1.0] - 2026-10-13

### Añadido
- Primera versión: reconocimiento del Pokémon rival por OCR en cualquier emulador, perfiles de calibración por juego, ficha superpuesta con tipos, debilidades, estadísticas base y habilidades.
