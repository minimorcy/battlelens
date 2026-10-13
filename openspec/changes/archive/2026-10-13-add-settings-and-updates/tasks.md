## 1. Configuración y actualizaciones (lógica)

- [x] 1.1 `core/config.py`: sección `[updates] check`, `render_config()` con la plantilla comentada (D1), `save_config()` atómico y `AppState.last_update_check`
- [x] 1.2 `core/updates.py`: `parse_version`, `is_newer`, `check_latest(fetch)` con la petición inyectable, `due(last, now)` de 24 h (D4)
- [x] 1.3 Tests: ida y vuelta de la configuración, valores por defecto de `[updates]`, comparación de versiones, respuesta 404, error de red, JSON inesperado y comprobación reciente

## 2. Interfaz

- [x] 2.1 `ui/settings.py`: ventana con todos los campos, validación por campo (D2) y aviso sobre los comentarios propios
- [x] 2.2 `ui/tray.py`: «Ajustes…» y la acción de descarga (oculta salvo que haya versión nueva)
- [x] 2.3 `app.py`: `apply_config()` en caliente (D3), comprobación de actualizaciones al arrancar en segundo plano, aviso y apertura de la Release en el navegador
- [x] 2.4 Tests de UI y de controlador: valores actuales en la ventana, error con «F8», guardar y aplicar el idioma y el atajo, aviso de versión nueva con la petición simulada

## 3. Empaquetado y repositorio

- [x] 3.1 Volver a incluir `ssl` en el `.spec` (D5) y añadir `ssl` a la autocomprobación; recompilar y comprobar el tamaño
- [x] 3.2 `.github/ISSUE_TEMPLATE/` (D6)

## 4. Cierre

- [x] 4.1 README (ajustes, actualizaciones, cómo informar de fallos), CHANGELOG y `docs/manual-validation.md`; todos los tests y `openspec validate --all --strict`
