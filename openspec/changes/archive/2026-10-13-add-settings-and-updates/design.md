## Context

`config.toml` se lee al arrancar (`core/config.py`) y su plantilla incluye comentarios explicativos. Los atajos se registran con `RegisterHotKey` en un hilo propio (`HotkeyManager`). El ejecutable excluye `ssl` para reducir tamaño, y PokéAPI no se consulta en tiempo de ejecución.

## Goals / Non-Goals

**Goals:** configurar todo sin editar archivos; aplicar los cambios al momento; enterarse de las actualizaciones; buenos informes de fallos.

**Non-Goals:** actualización automática (descargar e instalar sola); telemetría; editar perfiles desde los ajustes (ya se gestionan en la bandeja).

## Decisions

### D1. `config.toml` se regenera desde la plantilla
`render_config(cfg)` rellena la plantilla comentada con los valores (con escape TOML de las cadenas), así que guardar conserva las explicaciones. Los comentarios que haya escrito el propio usuario se pierden, y la ventana lo indica. Se escribe de forma atómica. Una prueba de ida y vuelta garantiza `load(render(cfg)) == cfg`.
*Alternativa descartada:* `tomlkit`, para conservar los comentarios del usuario. Sería otra dependencia para un archivo que la mayoría ya no editará a mano.

### D2. Atajos editables como texto, validados con `parse_hotkey`
`QKeySequenceEdit` genera textos como «Meta+…» y admite secuencias de varias teclas que `RegisterHotKey` no soporta. Un campo de texto validado con el mismo `parse_hotkey` del arranque es más predecible y da mensajes de error coherentes.

### D3. Aplicación en caliente con `Controller.apply_config(cfg)`
- Atajos: se detiene `HotkeyManager`, se crea otro con las nuevas combinaciones y se avisa de los que no se pudieron registrar.
- Resto: `matcher.threshold`, `pipeline.debug_dir`, `overlay.language`, `overlay.auto_hide_seconds`, intervalo del temporizador, `battle.hide_after_seconds`, y activar o desactivar la detección. Si se cambia `detection.enabled`, también se actualiza `state.auto_detect`, que tiene prioridad (spec `battle-detection`).

### D4. Comprobación de actualizaciones con `urllib` en un `QThreadPool`
`GET https://api.github.com/repos/minimorcy/battlelens/releases/latest`, con `Accept: application/vnd.github+json`, `User-Agent: BattleLens/<versión>` y un tiempo de espera de 5 s. Un 404 (todavía sin Releases), los errores de red o un JSON inesperado se registran en el log y no se muestran. `state.last_update_check` (ISO) limita la consulta a una vez cada 24 horas. La comparación usa tuplas de enteros; una etiqueta con formato no válido se considera no más nueva.
*Por qué no QtNetwork:* se quitó del paquete para ahorrar tamaño y obligaría a recuperar sus plugins; `urllib` + `ssl` es más pequeño.

### D5. `ssl` vuelve al ejecutable
Se elimina `ssl`/`_ssl` de las exclusiones del `.spec`. `libcrypto` ya estaba incluido (lo usa `hashlib`); se añaden `libssl` y `_ssl.pyd`, unos 2-3 MB. Se comprueba de nuevo el presupuesto de tamaño (≤ 150 MB la carpeta, ≤ 60 MB el instalador) y la autocomprobación añade la importación de `ssl`.

### D6. Formularios de issues de GitHub (YAML)
`bug_report.yml` (versión, emulador, juego e idioma, qué pasó, qué se esperaba, pasos, archivos de depuración), `feature_request.yml` y `config.yml` con `blank_issues_enabled: false`.

## Risks / Trade-offs

- [Se pierden los comentarios propios en `config.toml` al guardar desde la ventana] → Se avisa en la propia ventana. Es un caso poco habitual.
- [Límite de la API de GitHub (60 peticiones/hora por IP sin autenticar)] → Con una consulta al día como máximo no hay riesgo.
- [Proxies o cortafuegos que bloquean GitHub] → Fallo silencioso; la app funciona igual.

## Migration Plan

Los `config.toml` existentes sin `[updates]` usan `check = true`. El archivo se reescribe solo cuando el usuario guarda desde la ventana.

## Open Questions

Ninguna.
