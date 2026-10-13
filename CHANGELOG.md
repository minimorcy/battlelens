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
- Modos de ficha: **Normal** (compacta, aventura y captura) y **Competitivo** (nivel, estadísticas reales, movimientos probables, velocidad, habilidades y entrenamiento).

### Cambiado
- El proyecto pasa a llamarse **BattleLens**.
- Preprocesado sin OpenCV (descarga mucho más pequeña).
- Icono propio.
- Mejor reconocimiento en juegos 3D (Switch/3DS) y con regiones holgadas.

## [0.1.0] - 2026-10-13

### Añadido
- Primera versión: reconocimiento del Pokémon rival por OCR en cualquier emulador, perfiles de calibración por juego, ficha superpuesta con tipos, debilidades, estadísticas base y habilidades.
