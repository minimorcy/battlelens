## 1. Datos

- [x] 1.1 `sprite_id` por especie y forma en `build_dataset.py` y en `SpeciesView` (D1); regenerar `pokedex.json`
- [x] 1.2 Tests: Stufful = 759, Zigzagoon de Galar = 10174, Rotom Lavado y Mega Charizard X con su número

## 2. Caché

- [x] 2.1 `core/sprites.py`: descarga en segundo plano, validación, recorte y escritura atómica (D2)
- [x] 2.2 Tests con `fetch` simulado: recorte centrado, PNG no válido, tamaño excesivo, fallo de red recordado en la sesión

## 3. Ficha

- [x] 3.1 Recuadro de imagen en la cabecera, escalado nítido y llegada en diferido sin mover la ficha (D3)
- [x] 3.2 `overlay.sprites` en `config.toml` y casilla en Ajustes (D4)
- [x] 3.3 Tests de UI: con imagen en caché, sin imagen y opción desactivada (sin peticiones)

## 4. Stream

- [x] 4.1 Ruta `/sprite/<id>.png` y campo `sprite` en el payload (D5)
- [x] 4.2 Tests: id válido en caché, id fuera de caché (404), id no numérico o con `..` (404)

## 5. Cierre

- [x] 5.1 Aviso en el README es/en (D6) y CHANGELOG
- [ ] 5.2 Validación manual: primer reconocimiento con conexión, sin conexión y cambio de forma
