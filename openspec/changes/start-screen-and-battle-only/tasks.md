## 1. Solo en la pantalla de combate

- [x] 1.1 `with_levels_only(key, levels)`: quita los rivales leídos sin nivel
- [x] 1.2 Aplicarlo en el resultado automático si `detection.require_level` está activo
- [x] 1.3 Opción en `config.toml` y en Ajustes › Reconocimiento, con su texto en inglés
- [x] 1.4 Tests: filtro, controlador sin ficha en la Pokédex y con ficha en combate

## 2. Pantalla de inicio

- [x] 2.1 `StartDialog`: ventana (con actualizar), perfil (con preset), modo, detección y «Mostrar al abrir la app»
- [x] 2.2 Controlador: mostrarla al arrancar si `interface.start_screen`, aplicar lo elegido al pulsar «Empezar»
- [x] 2.3 Opción en `config.toml` y en Ajustes › General; `fill_window_combo` compartido con Ajustes
- [x] 2.4 Tests: aplica perfil, modo, detección y la opción; textos en inglés

## 3. Cierre

- [x] 3.1 Guía de uso (es/en): apartado y captura de la pantalla de inicio, opciones nuevas, problemas
- [x] 3.2 README (es/en) y CHANGELOG
- [ ] 3.3 Prueba manual: Pokédex y datos del Pokémon sin ficha; combates normales y dobles con ficha; pantalla de inicio con y sin perfiles
