## Context

`ui/settings.py` es un `QDialog` modal (`exec()`, con `_modal_open` que pausa la detección) con cuatro `QGroupBox` apilados y estilo nativo. Devuelve un `Config` en `result_config` y `Controller.apply_config()` lo guarda y lo aplica en caliente (spec `app-settings`). Los perfiles se gestionan solo desde submenús de `ui/tray.py`, que emite señales que `app.py` conecta a `select_window`, `select_profile`, `set_profile_game`, `calibrate_region`, `remove_region`, `new_profile_from_preset`, `calibrate_new` y `delete_profile`. «Acerca de» es otro diálogo (`ui/about.py`). La ficha usa una paleta oscura definida en `ui/theme.py` (`PANEL_BG`, `PANEL_BORDER`, `TEXT`, `TEXT_MUTED`, `ACCENT`). Toda cadena visible pasa por `_()` y un test exige su traducción y que no haya traducciones huérfanas.

## Goals / Non-Goals

**Goals:** un panel de ajustes completo y atractivo, con todo lo configurable en un solo sitio; separar con claridad lo que se guarda en `config.toml` de las acciones inmediatas sobre perfiles; bandeja corta con lo de uso diario; reutilizar las acciones existentes del controlador sin duplicar lógica.

**Non-Goals:** cambiar el formato de `config.toml` o de los perfiles; renombrar perfiles o editar regiones a mano (se siguen calibrando sobre una captura); tema claro; cambiar los menús de idioma en caliente (siguen cambiando al reiniciar).

## Decisions

### D1. `SettingsWindow`: ventana propia con navegación lateral
`SettingsWindow(QWidget)` con `Qt.WindowType.Window`, tamaño inicial ~820×560 y mínimo ~720×480. A la izquierda, un `QListWidget` (objectName `settings-nav`) con las secciones General, Ficha, Reconocimiento, Atajos, Modo stream, Perfiles y Acerca de, cada una con un símbolo Unicode monocromo (⚙ ▤ ◎ ⌨ ◉ ▣ ⓘ) para no añadir recursos; a la derecha, un `QStackedWidget` con una página por sección. Cada página tiene título, subtítulo de una línea y tarjetas (`QFrame` con objectName `settings-card`) que agrupan filas «etiqueta + descripción breve | control». `show_section(name)` permite abrirla en una sección concreta.
Los controles conservan los mismos atributos que hoy (`hotkey_edits`, `hotkey_errors`, `interface_language`, `language`, `mode`, `threshold`, `auto_hide`, `debug`, `detection_enabled`, `interval`, `hide_after`, `stream_enabled`, `stream_port`, `stream_mode`, `updates`) y el mismo `collect()`, para que la validación y los tests sigan siendo los mismos.
*Alternativa descartada:* `QTabWidget`. Con siete secciones las pestañas no caben bien y se ven menos cuidadas que una barra lateral.

### D2. Tema oscuro con una hoja de estilos única
`ui/theme.py` añade `SETTINGS_QSS`, construida con los colores de la ficha (fondo `#181a22`, tarjetas algo más claras, borde `PANEL_BORDER`, texto `TEXT`/`TEXT_MUTED`, acento `ACCENT` para la sección activa, el foco, las casillas marcadas y el botón principal, y `#e5484d` para errores y el botón de eliminar). Se aplica solo a la ventana (`setStyleSheet`), no a la aplicación, para no alterar la calibración ni los avisos.

### D3. Guardar sin cerrar, con cambios pendientes visibles
El pie tiene «Guardar» (principal) y «Cerrar». «Guardar» solo está activo si el formulario difiere de la configuración vigente (se compara una instantánea de los valores de los controles). Al pulsarlo se valida con `collect()`; si hay errores se muestran junto al campo y se salta a la sección del primero; si no, se emite `saved(Config)`, la ventana toma ese `Config` como nueva base y sigue abierta. Al cerrar con cambios sin guardar se pregunta «Guardar / Descartar / Cancelar». El aviso sobre los comentarios de `config.toml` pasa al pie, en texto secundario.

### D4. Sección Perfiles: acciones inmediatas mediante señales
La página no toca `ProfileStore`: recibe los mismos callables que la bandeja (`list_windows`, `get_target`, `get_profiles`, `get_games`) y emite señales con los mismos nombres que `Tray` (`window_selected`, `profile_selected`, `profile_game_selected`, `preset_requested`, `calibrate_requested`, `region_requested`, `region_remove_requested`, `delete_profile_requested`). `app.py` las conecta a los mismos métodos. Contenido:
- **Ventana del emulador:** combo con las ventanas (se rellena al abrir la sección y con el botón «Actualizar»).
- **Perfiles:** lista con el activo seleccionado; elegir otro lo activa al momento. Botones «Nuevo con un preset…», «Calibrar a mano…» y «Eliminar…».
- **Perfil activo:** combo «Juego» (con «Sin especificar») y una fila por región (rival, 2.º rival, tu Pokémon, menú de ataques) con su estado («Calibrada» / «Sin calibrar») y botones «Calibrar…»/«Recalibrar…» y «Quitar» (el rival no se puede quitar). Sin perfiles, el bloque se sustituye por una explicación y el botón del preset.
Un rótulo deja claro que estos cambios se aplican al momento. `refresh()` vuelve a leer los callables; el controlador lo llama tras cualquier cambio de perfiles, ventana, stream o actualizaciones mediante un único `_refresh_ui()`, que también actualiza el tooltip de la bandeja.

### D5. Ventana única y no modal
El controlador guarda una sola `SettingsWindow`; `show_settings(section=None)` la crea si no existe, la muestra, la trae al frente (`raise_()`/`activateWindow()`) y, si se indica, cambia de sección. Deja de ser `WindowStaysOnTopHint` para que los diálogos de calibración y el asistente de presets aparezcan por encima, y deja de poner `_modal_open`: la detección sigue funcionando (las calibraciones siguen pausándola como hasta ahora). Se reconstruye tras cambiar el idioma de la interfaz solo al reiniciar, como el resto de menús.

### D6. Acciones de mantenimiento y «Acerca de» dentro del panel
General incluye «Abrir carpeta de datos», «Informar de un problema…», «Instalar OCR de Windows…» (visible solo si falta) y, si hay versión nueva, «Descargar BattleLens X…»; emiten `open_data_requested`, `report_requested`, `install_ocr_requested` y `update_requested`. Modo stream muestra la URL actual y «Copiar URL» (`copy_stream_url_requested`), activo solo con el servidor en marcha. `ui/about.py` pasa a `AboutPanel(QWidget)` con el mismo contenido y `text()`; `AboutDialog` desaparece.

### D7. Bandeja reducida
Queda: Reconocer ahora · Detección automática · Modo de la ficha ▸ · Modo stream (OBS) · Copiar URL para OBS · — · Ventana del emulador ▸ · Perfil activo ▸ (con «Gestionar perfiles…» al final) · Nuevo perfil con un preset… · — · Instalar OCR (si falta) · Descargar versión (si hay) · Informar de un problema… · **Ajustes…** (acción por defecto, en negrita) · Salir. El doble clic en el icono abre Ajustes; el clic simple sigue abriendo el menú. `set_hotkey_hints` solo actualiza «Reconocer ahora». Se mantiene «Nuevo perfil con un preset…» porque el aviso de bienvenida lo propone (spec `game-presets`) e «Informar de un problema…» por la spec `problem-report`.

### D8. Ficha a medida: secciones ocultas por modo
`config.CARD_SECTIONS` enumera las secciones de cada modo con las mismas claves que los bloques de `ui/overlay.py` (Normal: `matchup`, `own_moves`, `eff`, `evo`, `forms`; Competitivo añade `stats`, `abilities`, `moves`, `training`). `Config` guarda `hidden_sections_normal` y `hidden_sections_competitive` (tuplas; listas en TOML) y `_validate` rechaza claves que no sean de su modo. La cabecera (nombre, tipos, nivel y captura) no se puede ocultar: sin ella la ficha no dice de quién es.
- **Ficha privada:** `Overlay.hidden` por modo; `_block()` construye el bloque igual pero lo oculta, así cada sección no necesita saber nada. Guardar Ajustes vuelve a dibujar la ficha visible.
- **Ficha del stream:** `build_cards(..., hidden=...)` vacía los campos de la tarjeta de cada sección oculta (`payload.HIDDEN_FIELDS`); el JS ya no dibuja lo que llega vacío. Usa las secciones del modo de la ficha del stream.
- **Ajustes:** tabla «Secciones de la ficha» en Ficha, con un interruptor por sección y modo («—» donde la sección no existe) y «Mostrar todas». Forma parte de lo que se guarda con «Guardar».
Por defecto (petición del usuario) la ficha es mínima: Normal oculta `matchup`, `own_moves`, `evo` y `forms` (solo quedan las eficacias); Competitivo oculta además `abilities`, `moves` y `training` (quedan eficacias y estadísticas). Los `config.toml` sin las claves toman ese valor por defecto.
Ocultar no es plegar: lo plegado (clic en el título, `state.json`) sigue en la ficha como una barra; lo oculto no aparece.

### D9. Cerrar la ficha solo con ✕
Un clic suelto en la ficha la cerraba, y es fácil hacerlo sin querer al ir a plegar un bloque o a moverla. `Overlay._close_button()` añade un ✕ (22 px, rojo al pasar el ratón) al final de la fila del nombre en la cabecera de la última tarjeta, y a la ficha «No reconocido». Su `clicked` llama a `close_by_user()`, que oculta y emite `dismissed` (la detección no la vuelve a abrir con el mismo rival). `mouseReleaseEvent` ya no oculta: arrastrar mueve y el título pliega.

## Risks / Trade-offs

- [Usuarios acostumbrados a los submenús de regiones] → «Gestionar perfiles…» en el submenú «Perfil activo» lleva directo a la sección; se explica en el CHANGELOG.
- [Ventana no modal: el usuario cambia algo en la bandeja con Ajustes abierto] → La parte inmediata se refresca con `_refresh_ui()`; la de `config.toml` solo cambia en la bandeja para modo de ficha, detección y stream: `set_mode`, `set_auto_detect` y `set_stream` del controlador actualizan también el control equivalente de la ventana sin marcarlo como cambio pendiente (se actualiza la base).
- [Símbolos Unicode con aspecto distinto según la fuente] → Se eligen símbolos presentes en Segoe UI Symbol (Windows 10/11); son decorativos y el texto de la sección siempre se ve.

## Migration Plan

Sin migración de datos: `config.toml` y los perfiles no cambian.

## Open Questions

Ninguna.
