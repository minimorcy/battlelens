# -*- mode: python ; coding: utf-8 -*-
# Spec de PyInstaller para BattleLens. Se usa a través de packaging/build.py,
# que genera el archivo de versión de Windows y lo pasa en BATTLELENS_VERSION_FILE.
import os

from PyInstaller.utils.hooks import collect_submodules, copy_metadata

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))
SRC = os.path.join(ROOT, "src")
PKG = os.path.join(SRC, "battlelens")

datas = [
    (os.path.join(PKG, "data", "pokedex.json"), "battlelens/data"),
    (os.path.join(PKG, "data", "learnsets.json"), "battlelens/data"),
    (os.path.join(PKG, "assets", "icon.png"), "battlelens/assets"),
    (os.path.join(PKG, "stream", "static"), "battlelens/stream/static"),  # página para OBS (add-stream-mode D7)
    (os.path.join(ROOT, "LICENSE"), "."),
]
datas += copy_metadata("battlelens")

# winrt carga sus proyecciones de forma dinámica: se incluyen explícitamente.
hiddenimports = collect_submodules("winrt")

excludes = [
    "tkinter",
    "unittest",
    "pydoc",
    "pytest",
    "cv2",
    "PyQt6.QtQml",
    "PyQt6.QtQuick",
    "PyQt6.QtQuickWidgets",
    "PyQt6.QtWebEngineCore",
    "PyQt6.QtWebEngineWidgets",
    "PyQt6.QtMultimedia",
    "PyQt6.QtNetwork",
    "PyQt6.QtSql",
    "PyQt6.QtPdf",
    "PyQt6.QtSvg",
    "PyQt6.QtOpenGL",
    "PyQt6.QtOpenGLWidgets",
    "PyQt6.QtDBus",
    "PyQt6.QtBluetooth",
    "PyQt6.QtPositioning",
    "PyQt6.QtDesigner",
    "PyQt6.QtHelp",
    "PyQt6.QtPrintSupport",
]

a = Analysis(
    [os.path.join(SPECPATH, "entry.py")],
    pathex=[SRC],
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=excludes,
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="BattleLens",
    console=False,
    icon=os.path.join(SPECPATH, "battlelens.ico"),
    version=os.environ.get("BATTLELENS_VERSION_FILE"),
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, upx=False, name="BattleLens")
