## 1. Ficha por delante

- [x] 1.1 `OverlayWindow.keep_on_top()` con `SetWindowPos(HWND_TOPMOST, …, SWP_NOACTIVATE)` al mostrarse y en cada comprobación de la detección
- [x] 1.2 Test: la ficha queda por delante de otra ventana topmost en el orden Z de Win32

## 2. Regiones ancladas

- [x] 2.1 `presets.game_screen()`: proporción (y si es DS) de cada juego conocido
- [x] 2.2 `Region.remap()`, `Profile.game_area` y `Profile.placed()`, con persistencia compatible
- [x] 2.3 `GameAreaTracker` en el pipeline (una búsqueda por tamaño de captura) usado al reconocer, en la detección y en el informe de problemas
- [x] 2.4 `game_area` al guardar un preset, al crear un perfil a mano y al recalibrar una región
- [x] 2.5 `find_viewport` no fiable con pantallas lisas
- [x] 2.6 Tests: ventana con barras ↔ pantalla completa, perfiles antiguos, pantalla negra, caché y recalibración

## 3. Cierre

- [x] 3.1 CHANGELOG (Corregido / Fixed)
- [x] 3.2 Guía de uso: apartado de presets y problemas, en español e inglés
- [ ] 3.3 Prueba manual: emulador a pantalla completa y maximizado con un perfil creado con preset
