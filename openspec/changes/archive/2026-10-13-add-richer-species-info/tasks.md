## 1. Dataset

- [x] 1.1 `tools/build_dataset.py`: ratio de captura, evoluciones (D2), mapa `items`, mapa `ability_descriptions` (D1); regenerar `pokedex.json`
- [x] 1.2 Tests del script con CSV mínimos (evolución por nivel y por objeto, descripción con saltos de línea)

## 2. Dominio

- [x] 2.1 `core/pokedex.py`: `capture_rate`, `evolution_stages()` (D3), etiquetas de condición (D4), `capture_difficulty()`, descripciones en `Ability`, y nuevos campos en `SpeciesView`
- [x] 2.2 Tests: escenarios de cadena (lineal, ramas, filtrado por generación, sin evolución) y de dificultad de captura

## 3. Interfaz

- [x] 3.1 `ui/overlay.py`: línea de captura, apartado «Evolución» y tooltips de habilidades (D5)
- [x] 3.2 Tests de UI: escenario «Datos adicionales» (Stufful)

## 4. Cierre

- [x] 4.1 README y CHANGELOG; todos los tests y `openspec validate --all --strict`
