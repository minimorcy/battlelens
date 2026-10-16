# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/); versionado [SemVer](https://semver.org/lang/es/).

## [0.4.0] - 2026-10-16

### Añadido
- Guía de uso en la web (`guide.html`), en español e inglés y con capturas de la app: instalación, presets, calibración, la ficha y sus modos, dobles, formas, ajustes, OBS y solución de problemas. «Leer la guía» lleva ahí.

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

### English

**Added**
- User guide on the website (`guide.html`), in English and Spanish with screenshots of the app: installing, presets, calibration, the card and its modes, doubles, forms, settings, OBS and troubleshooting. "Read the guide" now goes there.

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
