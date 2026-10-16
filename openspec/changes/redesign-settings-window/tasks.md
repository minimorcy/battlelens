## 1. Base visual

- [x] 1.1 `ui/theme.py`: `SETTINGS_QSS` con la paleta de la ficha (D2)
- [x] 1.2 `ui/about.py`: `AboutPanel(QWidget)` con el mismo contenido y `text()`; quitar `AboutDialog` (D6)

## 2. Ventana de Ajustes

- [x] 2.1 `ui/settings.py`: `SettingsWindow` con barra lateral, páginas con tarjetas y `show_section()` (D1), manteniendo los atributos de los controles y `collect()`
- [x] 2.2 Guardar sin cerrar: instantánea de valores, «Guardar» solo con cambios, salto a la sección del primer error, pregunta al cerrar con cambios (D3) y `set_base_values()` para cambios externos
- [x] 2.3 Sección Perfiles con ventana, lista, juego, regiones y acciones; `refresh()` y estado sin perfiles (D4)
- [x] 2.4 General y Modo stream: carpeta de datos, informe, OCR, descarga de versión, URL con «Copiar» (D6)

## 3. Bandeja y controlador

- [x] 3.1 `ui/tray.py`: menú reducido, «Gestionar perfiles…», «Ajustes…» por defecto y doble clic (D7)
- [x] 3.2 `app.py`: ventana única no modal `show_settings(section)`, conexión de señales, `_refresh_ui()` y sincronización de modo, detección, stream, OCR y versión nueva (D5)
- [x] 3.3 `i18n/en_menus.py`: textos nuevos y retirada de los que ya no se usan

## 4. Tests y cierre

- [x] 4.1 Adaptar los tests de Ajustes, bandeja, inglés y «Acerca de»; nuevos de navegación, «Guardar» con cambios, sección del error, perfiles (estado de regiones, sin perfiles, señales) y menú corto
- [x] 4.2 Probar la ventana real (`uv run battlelens`) y capturarla
- [x] 4.3 CHANGELOG, README (es/en) si mencionan los menús, todos los tests y `openspec validate --all --strict`

## 5. Ficha a medida (D8) y arreglos de la ficha

- [x] 5.1 `core/config.py`: `CARD_SECTIONS`, `hidden_sections_normal`/`hidden_sections_competitive` con validación y listas TOML
- [x] 5.2 `ui/overlay.py` (`Overlay.hidden`) y `stream/payload.py` (`hidden=`); `app.py` las aplica al arrancar y al guardar
- [x] 5.3 Ajustes › Ficha: tabla de secciones por modo con «Mostrar todas»; textos en inglés
- [x] 5.4 Bloque plegado: la tarjeta recalcula su altura tras procesar los `LayoutRequest` pendientes (antes conservaba la altura previa y repartía el hueco)
- [x] 5.5 Ficha del stream: la evolución usaba la clase `stage` del contenedor raíz y sus nombres salían arriba a la izquierda; pasa a `evo-stage`
- [x] 5.6 Tests (`tests/test_card_sections.py`)
- [x] 5.7 Ficha mínima por defecto (Normal: eficacias; Competitivo: eficacias y estadísticas)
- [x] 5.8 Botón ✕ en la cabecera (D9); el clic en el resto de la ficha ya no la oculta

