# Validación manual

Comprobaciones que no se pueden automatizar (juegos reales, máquina limpia, publicación).
Marca cada una al hacerla y anota el resultado.

## Reconocimiento con juegos reales

Con `recognition.debug = true` en `%APPDATA%\BattleLens\config.toml`: calibra, reconoce unos 10 rivales distintos y anota cuántos acierta y el tiempo que aparece en `app.log`.

- [x] **Switch** — Pokémon Espada (Eden). 13/10/2026: tras las correcciones de captura y preprocesado, Stufful se reconoce en ~80 ms.
- [ ] **GBA** — p. ej. Esmeralda o Rojo Fuego (mGBA). Aciertos: __/10
- [ ] **NDS** — p. ej. Platino o Negro (melonDS/DeSmuME). Aciertos: __/10
- [ ] **Forma regional** — un Pokémon de Galar en Espada (Zigzagoon, Ponyta…): la ficha muestra la forma de Galar.
- [ ] **Activación automática** — con perfiles de dos juegos, cambiar de juego en el emulador y comprobar que se activa el perfil correcto.

## Instalador y publicación

- [ ] Desinstalar respondiendo «Sí» a borrar los datos: no queda `%APPDATA%\BattleLens`.
- [ ] Instalar en una máquina (o VM) sin Python y usar la app.
- [ ] Instalar el OCR desde «Instalar OCR de Windows…» en una máquina que no lo tenga.
- [ ] Primera ejecución de la CI en GitHub en verde.
- [ ] Primera Release publicada con el instalador, el ZIP y `SHA256SUMS.txt`.
