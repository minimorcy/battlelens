## 1. Base

- [x] 1.1 Tokens en `theme.py` y `soft_type_style()` (D1), con test de contraste AA de los 18 tipos
- [x] 1.2 `_pill(..., solid=False)` y helper `_block()` (D2, D3)
- [x] 1.3 Maqueta HTML estática de la ficha Normal, Competitiva y doble para cerrar P1-P3 antes de tocar Qt

## 2. Ficha privada (`ui/overlay.py`)

- [x] 2.1 Cabecera: nombre, número, nivel y tipos sólidos
- [x] 2.2 «Contra tu X» y «Tus movimientos» (D4, D5)
- [x] 2.3 Eficacias con multiplicadores semánticos (D4)
- [x] 2.4 Captura con medidor en modo Normal (D6)
- [x] 2.5 Estadísticas (D7)
- [x] 2.6 Habilidades, movimientos, evolución, otras formas y entrenamiento (D8)
- [x] 2.7 Ajustar los tests de UI (D10) y comprobar los de escala ×2 y de ficha más alta que la pantalla

## 3. Bloques plegables

- [x] 3.1 Títulos con flecha, plegado de bloques y reajuste de tamaño sin mover la ficha (D11)
- [x] 3.2a `collapsed_sections` en `state.json` y `Controller.expand_all_sections()`
- [x] 3.2b Botón «Desplegar todas las secciones» en Ajustes › Ficha
- [x] 3.3 Tests: clic en el título pliega y no oculta, clic fuera oculta, lo plegado persiste y se aplica a las dos tarjetas de un combate doble
- [x] 3.4 Textos nuevos en el catálogo de inglés (D12)

## 4. Ficha del stream

- [x] 4.1 Variables y estilos en `card.css`, variantes en `card.js` (D9)
- [x] 4.2 Datos extra en `payload.py` si hacen falta, y tests de stream

## 5. Cierre

- [x] 5.1 Regenerar las capturas de la web y `og-image.png` con `tools/make_site_screenshots.py`
- [ ] 5.2 Validación manual (`docs/manual-validation.md`): Normal, Competitivo, doble, inglés, escala 150 % y plegar con el emulador en primer plano
- [x] 5.3 Entrada en el CHANGELOG (es/en)
