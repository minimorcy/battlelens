# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/); versionado [SemVer](https://semver.org/lang/es/).

## [0.2.0] - Sin publicar

### Añadido
- Instalador para Windows (sin permisos de administrador) y versión portable.
- Instalación guiada del paquete de OCR de Windows cuando falta.
- Ventana «Acerca de» con versión, licencia y avisos.
- Publicación automática de versiones con GitHub Actions.
- Formas regionales (Alola, Galar, Hisui, Paldea), tipos y tabla de eficacias según la generación del juego.
- Juego por perfil, detectado por el título de la ventana, y activación automática del perfil al cambiar de juego.
- Captura del emulador aunque esté tapado por otras ventanas.
- Detección automática del combate: la ficha aparece y se oculta sola, sin pulsar ninguna tecla.
- Combates dobles (dos fichas) y comparativa «Contra tu X» con veredicto de ventaja/desventaja.
- Ratio de captura con su dificultad, cadena evolutiva y descripción de las habilidades.
- Ventana de ajustes (sin editar archivos) y aviso de versión nueva.
- Web del proyecto (inglés/español) y README en inglés, con analítica opcional de Umami (sin cookies).
- Las habilidades que cambian la eficacia (Levitación, Absorbe Agua, Superguarda…) se aplican a las debilidades y a «Contra tu X» si son seguras, y se avisan si son solo posibles. Las habilidades son las de la generación del juego (Gengar con Levitación hasta la Gen 6).
- Estadísticas base de la generación del juego (la «Especial» única de la Gen 1, los valores anteriores a la Gen 6) y rangos a su nivel con la fórmula de cada juego (Gen 1-2, Let's Go y Leyendas: Arceus).
- Megaevoluciones, regresiones primigenias y formas alternativas (Rotom, Deoxys, Giratina, Necrozma…) según el juego, en «Otras formas», con el atajo `Ctrl+Alt+F` para elegir la forma del rival.
- Modos de ficha: **Normal** (compacta, aventura y captura) y **Competitivo** (nivel, estadísticas reales, movimientos probables, velocidad, habilidades y entrenamiento).

### Cambiado
- El proyecto pasa a llamarse **BattleLens**.
- Preprocesado sin OpenCV (descarga mucho más pequeña).
- Icono propio.
- Mejor reconocimiento en juegos 3D (Switch/3DS) y con regiones holgadas.
- El nivel se lee con más fiabilidad: si el nombre se reconoce sin nivel, se reintenta con más variantes y con la mitad derecha ampliada, y se toleran dígitos leídos como letras («Nv. 1G»).

### Corregido
- En combates dobles con escalado de pantalla alto (150-200 %), los textos largos de la ficha se recortaban.
- La ficha competitiva no cabía en pantallas de 720-768 px de alto: ahora se ajusta a la pantalla y se desplaza con la rueda.

## [0.1.0] - 2026-10-13

### Añadido
- Primera versión: reconocimiento del Pokémon rival por OCR en cualquier emulador, perfiles de calibración por juego, ficha superpuesta con tipos, debilidades, estadísticas base y habilidades.
