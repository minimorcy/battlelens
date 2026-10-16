## Why

La ventana «Ajustes» es hoy un formulario largo con cuatro grupos apilados y estilo por defecto de Windows, que no se parece en nada a la ficha. Además, la gestión de perfiles (juego, regiones, calibrar, eliminar) solo existe como submenús anidados de la bandeja, difíciles de descubrir y sin ver de un vistazo cómo está configurado cada perfil. Queremos un panel de ajustes completo y cuidado, y que la bandeja se quede con lo que se usa a diario.

## What Changes

- **Nueva ventana de Ajustes** con navegación lateral por secciones e iconos, tema oscuro coherente con la ficha (mismos colores y acento) y un tamaño cómodo y redimensionable:
  - **General:** idioma de la interfaz, comprobación de actualizaciones (con el botón de descarga si hay versión nueva), abrir la carpeta de datos, instalar el OCR de Windows (si falta) e informar de un problema.
  - **Ficha:** modo de la ficha, idioma de los datos Pokémon y ocultación automática.
  - **Reconocimiento:** umbral, detección automática (activada, intervalo, ocultar al terminar) y recortes de depuración.
  - **Atajos:** los seis atajos, con su error junto al campo.
  - **Modo stream:** activado, puerto, modo de la ficha del stream y la URL para OBS con botón «Copiar».
  - **Perfiles:** ventana del emulador, lista de perfiles con el activo marcado, juego del perfil, estado de cada región (rival, 2.º rival, tu Pokémon, menú de ataques) con botones para calibrar, recalibrar o quitar, y crear perfil (con preset o manual) o eliminarlo.
  - **Acerca de:** versión, enlace, licencia, atribución y aviso legal (sustituye al diálogo «Acerca de»).
- **Ficha a medida:** en Ficha, una tabla con cada sección de la ficha (contra tu Pokémon, tus movimientos, eficacias, estadísticas, habilidades, movimientos probables, entrenamiento, evolución y otras formas) y un interruptor por modo (Normal y Competitivo) para mostrarla u ocultarla, con «Mostrar todas». Se guarda en `config.toml` (`overlay.hidden_normal` y `overlay.hidden_competitive`) y la ficha del stream sigue la misma elección para su modo.
- **Dos tipos de cambio claramente separados:** lo que vive en `config.toml` se guarda con «Guardar» (y se descarta con «Cancelar»), como ahora; lo de la sección Perfiles se aplica al momento, igual que desde la bandeja.
- **La ventana no es modal y es única:** abrirla con ella ya abierta la trae al frente; la detección automática sigue funcionando mientras está abierta; las calibraciones se abren por encima.
- **Bandeja más ligera:** conserva reconocer, detección automática, modo de la ficha, modo stream y copiar URL, ventana del emulador, perfil activo, nuevo perfil con un preset, instalar OCR y descargar versión (cuando proceda), informar de un problema, «Ajustes…» y salir. Añade «Gestionar perfiles…» (abre Ajustes en Perfiles) y el doble clic en el icono abre Ajustes. **BREAKING (menú):** salen de la bandeja «Juego del perfil activo», «Regiones del perfil», «Calibrar nuevo perfil…», «Eliminar perfil activo…», «Abrir carpeta de datos» y «Acerca de…», que pasan al panel.

## Capabilities

### New Capabilities
<!-- ninguna -->

### Modified Capabilities
- `app-settings`: la ventana se organiza en secciones con navegación lateral, no es modal, incluye la gestión de perfiles, acciones de mantenimiento y «Acerca de».
- `battle-overlay`: el menú de la bandeja se reduce a las opciones rápidas, añade «Gestionar perfiles…» y el doble clic abre Ajustes.
- `game-profiles`: el juego del perfil se cambia desde Ajustes › Perfiles (deja de estar en la bandeja); el perfil activo se puede cambiar también desde allí.

## Impact

- **Código:** `ui/settings.py` reescrito (ventana con secciones, página de perfiles y estilos); `ui/about.py` pasa a ser un panel reutilizable dentro de Ajustes; `ui/tray.py` simplificado; `app.py` mantiene una única ventana de Ajustes no modal, conecta sus señales a las acciones existentes y la refresca al cambiar perfiles, ventana, stream o actualizaciones.
- **Textos:** nuevos textos en `i18n/en_menus.py`; se retiran las traducciones que dejan de usarse.
- **Tests:** se adaptan los de Ajustes, bandeja y «Acerca de»; nuevos para la página de perfiles y la navegación.
- **Configuración:** dos claves nuevas en `[overlay]` (`hidden_normal`, `hidden_competitive`). Por defecto la ficha es mínima: Normal solo con eficacias y Competitivo con eficacias y estadísticas (el resto se activa en Ajustes › Ficha). **BREAKING (ficha):** quien no tenga las claves en su `config.toml` pasa a ver esa ficha mínima.
- **Botón ✕ para cerrar la ficha:** arriba a la derecha (uno solo en los combates dobles). Un clic en el resto de la ficha ya no la oculta; el título de cada bloque la sigue plegando.
- **Sin dependencias nuevas** (iconos de la fuente de iconos de Windows, con símbolos Unicode de reserva).
