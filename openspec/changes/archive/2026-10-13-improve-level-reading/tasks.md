## 1. Lectura del nivel

- [x] 1.1 `core/normalize.py`: confusiones de dígitos tras el prefijo (D1), con tests de los escenarios y de nombres que no son niveles
- [x] 1.2 `vision/preprocess.py`: `level_variants` (mitad derecha a 48 y 64 px) (D3)
- [x] 1.3 `pipeline.py`: parada temprana condicionada al nivel y lectura de la mitad derecha (D2-D3)
- [x] 1.4 Tests del pipeline con OCR simulado: nivel en otra variante, nivel solo en la mitad derecha, región sin nivel (como mucho 5 lecturas extra) y variante con nivel que para enseguida

## 2. Cierre

- [x] 2.1 README (en y es: limitación del nivel en 3D), CHANGELOG, `docs/manual-validation.md`, todos los tests y `openspec validate --strict`
