## 1. Preparación

- [x] 1.0 Renombrar el proyecto a BattleLens: paquete `src/battlelens/`, nombre de distribución y script `battlelens`, `APP_NAME`/carpeta de datos `BattleLens`, `BATTLELENS_HOME`, textos de la interfaz y README; todos los tests en verde
- [x] 1.1 Convertir el script temporal de precisión en `tests/test_ocr_accuracy.py` (36 nombres pixelados sintéticos, umbral ≥ 34/36) y registrar el resultado de referencia con OpenCV
- [x] 1.2 Añadir la *fixture* `requires_ocr` que omite con motivo los tests de OCR, de precisión y de integración cuando no hay paquete de OCR compatible
- [x] 1.3 Añadir `LICENSE` (MIT), `CHANGELOG.md` con la sección 0.2.0 y la constante única del nombre de la app, la URL del repositorio y el aviso legal en `battlelens/__init__.py`, con la versión leída de `importlib.metadata`

## 2. Eliminar OpenCV

- [x] 2.1 Reescribir `vision/preprocess.py` con numpy + Pillow según la tabla D5 (incluido Otsu en numpy) y añadir un test de Otsu con un histograma bimodal conocido
- [x] 2.2 Sustituir OpenCV en `platform/ocr.py` (conversión a RGBA) y en `pipeline.py` (PNG con Pillow)
- [x] 2.3 Quitar `opencv-python-headless` de las dependencias, ejecutar todos los tests y comprobar que el test de precisión sigue en ≥ 34/36 (si no, ajustar σ y alturas)

## 3. Funciones de la app

- [x] 3.1 Implementar `--self-test` / `--self-test-output` en `app.main` (D4), sin crear interfaz, con test unitario que lo invoca en proceso
- [x] 3.2 Generar el icono original con `packaging/make_icon.py` (.ico de 16 a 256 px y .png) y usarlo en la bandeja y en las ventanas, eliminando la Poké Ball
- [x] 3.3 Implementar `ui/about.py` («Acerca de»: versión, licencia, enlace al repositorio, atribución a PokéAPI y aviso no oficial) y añadirlo al menú de la bandeja
- [x] 3.4 Implementar `platform/ocr_setup.py` (idioma propuesto según la interfaz de Windows, `ShellExecuteExW runas`, espera en segundo plano, cancelación de UAC 1223, comprobación posterior) con tests de la elección de idioma y de la construcción del comando
- [x] 3.5 Integrar la instalación del OCR en la app: aviso al arrancar, opción del menú solo si falta, mensajes de éxito, cancelación, fallo y reinicio necesario
- [x] 3.6 Cambiar el nombre del mutex a `BattleLens` (D6) y actualizar su test

## 4. Empaquetado

- [x] 4.1 Crear `packaging/entry.py` y `packaging/battlelens.spec` (datas, copy_metadata, hiddenimports de winrt, excludes de Qt, sin UPX, con icono y versión)
- [x] 4.2 Crear `packaging/build.py`: leer la versión, generar el archivo de versión de Windows, compilación limpia, poda de traducciones, informe de tamaño y fallo si se supera el presupuesto
- [x] 4.3 Compilar en local, pasar `--self-test` sobre el `.exe`, comprobar sus propiedades de versión, arrancarlo desde otro directorio de trabajo y verificar que la carpeta ocupa ≤ 150 MB

## 5. Instalador

- [x] 5.1 Crear `packaging/installer.iss` (por usuario, AppId fijo, AppMutex, es/en, licencia, tareas de escritorio e inicio con Windows, ejecutar al terminar, pregunta de borrado de datos al desinstalar)
- [x] 5.2 Ampliar `build.py` para generar el instalador con ISCC (si está disponible) y el ZIP portable con nombres versionados, y comprobar que el instalador ocupa ≤ 60 MB
- [x] 5.3 Probar en local: instalar sin administrador, actualizar encima conservando perfiles, detectar la app abierta, desinstalar con y sin borrar datos, y usar la versión portable

## 6. CI y publicación

- [x] 6.1 Crear `.github/workflows/ci.yml` (tests + `openspec validate --all --strict`; en `main`, compilación y artefactos durante 14 días)
- [x] 6.2 Crear `.github/workflows/release.yml` (comprobar etiqueta = versión, tests, compilación, self-test, ISCC, ZIP, SHA256SUMS, notas desde CHANGELOG, `gh release create`)
- [x] 6.3 Crear el script `packaging/release_notes.py` que extrae la sección de una versión de `CHANGELOG.md` y añade el aviso legal y las instrucciones de SmartScreen, con test

## 7. Documentación y primera publicación

- [x] 7.1 Reescribir el README con una sección para usuarios (descarga, instalación, aviso de SmartScreen, OCR, uso) separada de la de desarrollo, más el aviso legal y la atribución
- [x] 7.2 Ejecutar todos los tests y `openspec validate --all --strict`
- [ ] 7.3 (Usuario) Crear el repositorio en GitHub, autenticar `gh`, subir `main`, comprobar que la CI pasa y probar el artefacto en una máquina limpia
- [ ] 7.4 (Usuario) Crear la etiqueta `v0.2.0` y comprobar la Release publicada
