# Validación manual

Comprobaciones que no se pueden automatizar (juegos reales, máquina limpia, publicación).
Marca cada una al hacerla y anota el resultado.

## Reconocimiento con juegos reales

Con `recognition.debug = true` en `%APPDATA%\BattleLens\config.toml`: calibra, reconoce unos 10 rivales distintos y anota cuántos acierta y el tiempo que aparece en `app.log`.

- [x] **Switch** — Pokémon Espada (Eden). 13/10/2026: tras las correcciones de captura y preprocesado, Stufful se reconoce en ~80 ms.
- [ ] **GBA** — p. ej. Esmeralda o Rojo Fuego (mGBA). Aciertos: __/10
- [ ] **NDS** — p. ej. Platino o Negro (melonDS/DeSmuME). Aciertos: __/10
- [ ] **Forma regional** — un Pokémon de Galar en Espada (Zigzagoon, Ponyta…): la ficha muestra la forma de Galar.
- [ ] **Detección automática** — en un juego real, la ficha aparece al entrar en combate, cambia con cada rival y se oculta al terminar; caminando por el mapa no aparece nada.
- [ ] **Tu Pokémon y dobles** — calibrar la región de tu Pokémon y la del 2.º rival en un juego con combates dobles (Espada): aparecen dos fichas con «Contra tu X», que se actualiza al cambiar de Pokémon.
- [ ] **Modo competitivo** — con la región del rival incluyendo el nivel: se lee el nivel, los movimientos probables coinciden con los que usa el rival salvaje y `Ctrl+Alt+M` cambia de modo con la ficha abierta.
- [ ] **Estadísticas por juego** — en Rojo/Azul la ficha competitiva muestra «Especial»; en Let's Go y Leyendas: Arceus, las estadísticas reales de un Pokémon propio (pantalla del equipo) caen dentro del rango de la ficha.
- [ ] **Formas alternativas** — en X/Y, contra un Pokémon que megaevoluciona, `Ctrl+Alt+F` muestra su mega y la ficha la mantiene hasta que sale; en Platino, Rotom alterna entre sus cinco formas.
- [ ] **Nivel en Espada a pantalla completa** — con la región del rival incluyendo el nivel, reconocer unos 10 rivales en modo Competitivo y anotar en cuántos aparece el nivel: __/10.
- [ ] **Tus movimientos** — calibrar el menú de ataques en Espada y en un juego de GBA: al abrir «Luchar» la ficha muestra tus 4 movimientos con su multiplicador; en el siguiente combate con el mismo Pokémon aparecen sin abrir el menú; las animaciones del combate no ocultan la ficha.
- [ ] **Activación automática** — con perfiles de dos juegos, cambiar de juego en el emulador y comprobar que se activa el perfil correcto.

## Instalador y publicación

- [ ] Desinstalar respondiendo «Sí» a borrar los datos: no queda `%APPDATA%\BattleLens`.
- [ ] Instalar en una máquina (o VM) sin Python y usar la app.
- [ ] Instalar el OCR desde «Instalar OCR de Windows…» en una máquina que no lo tenga.
- [ ] Primera ejecución de la CI en GitHub en verde.
- [ ] Primera Release publicada con el instalador, el ZIP y `SHA256SUMS.txt`.
- [ ] Con una versión instalada anterior a la última Release, aparece el aviso de versión nueva y «Descargar…» abre la página correcta.
- [ ] Las plantillas de issues aparecen al pulsar «New issue» en GitHub.

## Web (Coolify)

Siguiendo [deploy-website.md](deploy-website.md):

- [ ] Registro DNS de `battlelens.minim-labs.app` y recurso creado en Coolify (Dockerfile, base `/site`, puerto 80).
- [ ] `https://battlelens.minim-labs.app` carga con HTTPS y `/health` responde `ok`.
- [ ] La consola del navegador no muestra errores de CSP y el botón EN/ES funciona.
- [ ] Un push que cambia `site/` vuelve a desplegar la web solo; uno que no la toca, no.
- [ ] Con las variables de Umami en Coolify: el log muestra «Umami activado», Umami registra una visita y un evento `download`, y el pie muestra el aviso de analítica.
