## 1. Base

- [x] 1.1 `core/card_text.py`: líneas de habilidades y notas de la comparativa, usadas por el overlay (D3); los tests de la ficha siguen en verde
- [x] 1.2 `core/config.py`: claves `[stream]` y `hotkeys.toggle_stream`, con validación y plantilla (D6); tests

## 2. Fuente para OBS

- [x] 2.1 `stream/payload.py`: tarjetas en modo Normal y Competitivo (D4); tests con Machop contra Scorbunny
- [x] 2.2 `stream/server.py`: `StreamState` y `StreamServer` (D2); tests de `/`, `/state`, `Host` ajeno (403), ruta desconocida o de escape (404), método no GET y puerto ocupado
- [x] 2.3 `stream/static/`: `index.html`, `card.css` y `card.js` (D5); comprobación visual con un navegador sin interfaz

## 3. App e interfaz

- [x] 3.1 `app.py`: arrancar, parar y reiniciar el servidor, publicar en `_show_battle`, ocultar al terminar el combate, atajo de mostrar u ocultar y aviso de puerto ocupado (D6)
- [x] 3.2 `ui/tray.py` y `ui/settings.py`: «Modo stream», «Copiar URL para OBS» y sección de Ajustes
- [x] 3.3 `packaging/battlelens.spec` y `selftest.py`: archivos de la página (D7)
- [x] 3.4 Tests de controlador y de UI: publicar al mostrar, el clic en la privada no oculta la del stream, el fin del combate sí, el atajo alterna, la bandeja copia la URL y Ajustes reinicia el servidor

## 4. Cierre

- [x] 4.1 README (en y es: sección «Streaming / OBS» y configuración), CHANGELOG, `docs/manual-validation.md` (OBS real), todos los tests y `openspec validate --strict`
