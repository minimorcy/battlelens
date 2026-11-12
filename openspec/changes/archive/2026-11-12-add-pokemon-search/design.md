## Context

La ficha se dibuja con `Controller._show_battle(key, game, rect)`, que ya resuelve la vista por juego, coloca la ficha (`rect=None` → pantalla principal), gestiona formas y modos y publica en el stream. Los atajos se declaran en `Config`, `_parse_hotkeys`, `_on_hotkey`, `HOTKEY_FIELDS` de Ajustes y la bandeja. `NameMatcher` resuelve texto libre a especie en cinco idiomas con tolerancia a erratas.

## Goals / Non-Goals

**Goals:** abrir un buscador desde cualquier sitio y mostrar la ficha de cualquier especie reutilizando la ficha de combate.

**Non-Goals:** buscar movimientos, habilidades o tipos; historial de búsquedas; elegir el juego en el buscador (se usa el del perfil activo); mostrar la ficha buscada en el stream.

## Decisions

- **D1 · Reutilizar `_show_battle` con la clave `(sid, None, None)`.** Así la ficha buscada hereda colocación, formas (`cycle_form`) y modos (`_redraw_last_battle`) sin código nuevo. La alternativa, una vista de ficha aparte, duplicaría la ficha.
- **D2 · `searched` en `_last_battle`.** `_show_battle` recibe `searched=False`. Se guarda en `self._searched`, y cuando es `True` se omite `_publish_stream`. El redibujado al cambiar de forma o de modo conserva el valor, así que la consulta nunca llega a OBS. La alternativa, publicar y ocultar, provocaría un parpadeo en el stream.
- **D3 · Resolver con `NameMatcher`.** Se usa el `self.pipeline.matcher` existente (su umbral es el del OCR). El `QCompleter` (modo `MatchContains`, insensible a mayúsculas) solo sugiere los nombres en el idioma de la interfaz. Se acepta la entrada en cualquier idioma.
- **D4 · Diálogo modal (`exec`) con `_modal_open`.** Es el mismo patrón que el informe de problemas: pausa la detección automática mientras se escribe. `WindowStaysOnTopHint` y `activateWindow()` lo ponen delante del emulador. El diálogo devuelve el `species_id` y la app decide qué hacer con él, así que la UI no depende de `Controller`.
- **D5 · `Ctrl+Alt+B`** («Buscar»), libre entre los atajos actuales.

## Risks / Trade-offs

- [Un emulador a pantalla completa exclusiva no cede el foco] → la guía ya recomienda pantalla completa sin bordes; se menciona en la guía.
- [La detección automática puede sustituir la ficha buscada en pleno combate] → es el comportamiento esperado (spec); la búsqueda pausa la detección solo mientras el diálogo está abierto.
- [El umbral del OCR podría rechazar erratas grandes] → el completer ofrece el nombre exacto; si no, se avisa y el diálogo sigue abierto.
