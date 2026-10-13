## 1. Lógica

- [x] 1.1 `vision/preprocess.py`: `fingerprint(crop)` (32×12, gris, uint8) y `fingerprint_distance(a, b)` (media absoluta)
- [x] 1.2 `core/detection.py`: `BattleDetector` según D1-D4 (estabilidad, memoria del último intento, mostrar, ocultar por ausencia, resultados manuales, ocultación por el usuario)
- [x] 1.3 Tests con secuencias sintéticas: todos los escenarios de `battle-detection` (entrada en combate, escena en movimiento, región sin cambios, nuevo rival, ficha ocultada, sin reconocer, fin del combate, cambio breve, mismo rival en otro combate)

## 2. Configuración

- [x] 2.1 `core/config.py`: sección `[detection]` con valores por defecto y validación; `AppState.auto_detect`; plantilla de `config.toml` actualizada
- [x] 2.2 Tests: config antigua sin `[detection]`, valores inválidos y prioridad del estado sobre la configuración

## 3. Integración

- [x] 3.1 `app.py`: temporizador, tarea de captura y huella, reconocimiento sobre el recorte, acciones SHOW/HIDE, sincronización con el modo manual y la ocultación por el usuario, parada al salir
- [x] 3.2 `ui/tray.py`: acción marcable «Detección automática»
- [x] 3.3 Tests de integración con el emulador falso: aparece la ficha sin pulsar nada, cambia de rival y se oculta al «terminar» el combate; el conmutador persiste

## 4. Cierre

- [x] 4.1 README, CHANGELOG y `docs/manual-validation.md` (comprobar la detección automática en un juego real); todos los tests y `openspec validate --all --strict`
