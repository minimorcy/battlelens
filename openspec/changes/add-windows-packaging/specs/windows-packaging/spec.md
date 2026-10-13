## ADDED Requirements

### Requirement: Compilación del ejecutable
El proyecto SHALL incluir un script `packaging/build.py` que, partiendo de una carpeta `build/` y `dist/` limpias, genere con PyInstaller la carpeta `dist/BattleLens/` con el ejecutable `BattleLens.exe`. El ejecutable MUST ser de tipo ventana (sin consola) y MUST funcionar en un Windows 10/11 sin Python instalado.

#### Scenario: Compilación local
- **WHEN** un desarrollador ejecuta `uv run python packaging/build.py` en Windows
- **THEN** se genera `dist/BattleLens/BattleLens.exe` y el script termina con código 0

#### Scenario: Equipo sin Python
- **WHEN** se copia la carpeta `dist/BattleLens/` a un equipo sin Python ni uv y se ejecuta el `.exe`
- **THEN** la aplicación arranca, sin ventana de consola, y aparece el icono en la bandeja del sistema

### Requirement: Recursos incluidos
El ejecutable SHALL incluir `pokedex.json`, el icono de la aplicación y el archivo `LICENSE`, y MUST cargarlos sin depender del directorio de trabajo.

#### Scenario: Arranque desde otra carpeta
- **WHEN** se lanza el ejecutable desde un acceso directo cuyo directorio de trabajo es distinto de la carpeta de instalación
- **THEN** el dataset se carga correctamente

### Requirement: Versión única
La versión de la aplicación SHALL definirse solo en `pyproject.toml`. El ejecutable MUST incluirla en sus metadatos de archivo de Windows (versión del archivo y del producto) y la aplicación MUST mostrarla en tiempo de ejecución.

#### Scenario: Propiedades del archivo
- **WHEN** `pyproject.toml` indica la versión 0.2.0 y se compila
- **THEN** las propiedades del `.exe` en el Explorador muestran la versión 0.2.0 y el nombre de producto "BattleLens"

### Requirement: Autocomprobación
El ejecutable SHALL aceptar el argumento `--self-test`. Con él, carga el dataset, resuelve "PIDGEY" a la especie #16, comprueba que se pueden importar todos los módulos de la app (Qt, captura, OCR) y termina sin mostrar interfaz, con código 0 si todo es correcto y distinto de 0 si algo falla. El resultado MUST escribirse en un archivo cuya ruta se indica con `--self-test-output`. La falta de un paquete de OCR MUST notificarse como aviso, no como fallo.

#### Scenario: Ejecutable correcto
- **WHEN** se ejecuta `BattleLens.exe --self-test --self-test-output resultado.json`
- **THEN** el proceso termina con código 0 en menos de 30 s y `resultado.json` contiene la versión y el estado de cada comprobación

#### Scenario: Dataset ausente en el paquete
- **WHEN** el ejecutable se ha compilado sin `pokedex.json`
- **THEN** la autocomprobación termina con código distinto de 0 e indica qué comprobación falló

### Requirement: Dependencias mínimas
El paquete MUST NOT incluir OpenCV. El preprocesado SHALL implementarse con numpy y Pillow manteniendo el comportamiento de la spec `name-recognition`. Los módulos de Qt que no se usen (QML, WebEngine, multimedia, etc.) y sus traducciones MUST excluirse.

#### Scenario: Precisión mantenida
- **WHEN** se ejecuta el banco de pruebas de precisión del OCR (36 nombres pixelados sintéticos)
- **THEN** se reconocen correctamente al menos 34 de los 36

#### Scenario: Presupuesto de tamaño
- **WHEN** se compila la versión de distribución
- **THEN** la carpeta `dist/BattleLens/` ocupa como máximo 150 MB y el instalador como máximo 60 MB
