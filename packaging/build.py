"""Compila BattleLens para Windows: ejecutable (PyInstaller), instalador (Inno Setup) y ZIP portable.

Uso:
    uv run python packaging/build.py                 # ejecutable + instalador (si hay ISCC) + ZIP
    uv run python packaging/build.py --skip-installer
    uv run python packaging/build.py --self-test     # además, ejecuta la autocomprobación del .exe
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGING = ROOT / "packaging"
BUILD = ROOT / "build"
DIST = ROOT / "dist"
APP_DIR = DIST / "BattleLens"
EXE = APP_DIR / "BattleLens.exe"

MAX_APP_MB = 150
MAX_INSTALLER_MB = 60
ISCC_CANDIDATES = [
    Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Inno Setup 6" / "ISCC.exe",
    Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Inno Setup 6" / "ISCC.exe",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Inno Setup 6" / "ISCC.exe",
]
# Solo se conservan las traducciones de los diálogos estándar de Qt (botones Sí/No, etc.).
KEEP_TRANSLATIONS = ("qtbase_es", "qtbase_en", "qtbase_fr", "qtbase_de", "qtbase_it")
# Archivos de Qt que arrastran los plugins por defecto pero la app no usa (solo widgets + PNG):
# OpenGL por software (~20 MB), plugins de imagen PDF/SVG y las DLL que estos cargan.
UNUSED_QT_FILES = (
    "bin/opengl32sw.dll",
    "bin/Qt6Pdf.dll",
    "bin/Qt6Svg.dll",
    "bin/Qt6Network.dll",
    "plugins/imageformats/qpdf.dll",
    "plugins/imageformats/qsvg.dll",
    "plugins/iconengines/qsvgicon.dll",
)


class BuildError(RuntimeError):
    pass


def read_version() -> str:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return data["project"]["version"]


def version_tuple(version: str) -> tuple[int, int, int, int]:
    parts = [int(p) for p in version.split("+")[0].split("-")[0].split(".")]
    return tuple((parts + [0, 0, 0, 0])[:4])  # type: ignore[return-value]


def write_version_file(version: str, path: Path) -> None:
    v = version_tuple(version)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers={v}, prodvers={v}, mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040904B0', [
      StringStruct('CompanyName', 'minimorcy'),
      StringStruct('FileDescription', 'BattleLens'),
      StringStruct('FileVersion', '{version}'),
      StringStruct('InternalName', 'BattleLens'),
      StringStruct('LegalCopyright', 'MIT License'),
      StringStruct('OriginalFilename', 'BattleLens.exe'),
      StringStruct('ProductName', 'BattleLens'),
      StringStruct('ProductVersion', '{version}')])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
""",
        encoding="utf-8",
    )


def folder_mb(path: Path) -> float:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / 1024 / 1024


def run_pyinstaller(version: str) -> None:
    for d in (BUILD, DIST):
        try:
            shutil.rmtree(d)
        except FileNotFoundError:
            pass
        except PermissionError as exc:
            raise BuildError(f"No se puede limpiar {d}: ¿está BattleLens abierto o hay una terminal dentro? ({exc})")
    version_file = BUILD / "version_info.txt"
    write_version_file(version, version_file)
    env = {**os.environ, "BATTLELENS_VERSION_FILE": str(version_file)}
    cmd = [
        sys.executable, "-m", "PyInstaller", str(PACKAGING / "battlelens.spec"),
        "--noconfirm", "--clean", "--distpath", str(DIST), "--workpath", str(BUILD / "pyinstaller"),
    ]
    if subprocess.run(cmd, env=env, cwd=ROOT).returncode != 0:
        raise BuildError("PyInstaller falló")
    if not EXE.exists():
        raise BuildError(f"No se generó {EXE}")


def add_top_level_files() -> None:
    # PyInstaller 6 deja los datos en _internal/; la licencia debe verse en la carpeta del programa.
    shutil.copy2(ROOT / "LICENSE", APP_DIR / "LICENSE.txt")


def prune() -> None:
    qt = APP_DIR / "_internal" / "PyQt6" / "Qt6"
    for rel in UNUSED_QT_FILES:
        (qt / rel).unlink(missing_ok=True)
    for translations in APP_DIR.rglob("translations"):
        if translations.is_dir() and "Qt6" in translations.parts:
            for qm in translations.glob("*.qm"):
                if not qm.stem.startswith(KEEP_TRANSLATIONS):
                    qm.unlink()


def self_test() -> dict:
    output = BUILD / "self-test.json"
    output.unlink(missing_ok=True)
    proc = subprocess.run([str(EXE), "--self-test", "--self-test-output", str(output)], timeout=60, cwd=BUILD)
    if not output.exists():
        raise BuildError(f"La autocomprobación no generó informe (código {proc.returncode})")
    report = json.loads(output.read_text(encoding="utf-8"))
    for name, check in report["checks"].items():
        print(f"  [{check['status']:>4}] {name} {check['detail']}")
    if proc.returncode != 0:
        raise BuildError("La autocomprobación del ejecutable falló")
    return report


def find_iscc() -> Path | None:
    on_path = shutil.which("ISCC") or shutil.which("iscc")
    if on_path:
        return Path(on_path)
    return next((p for p in ISCC_CANDIDATES if p.exists()), None)


def build_installer(version: str, iscc: Path) -> Path:
    cmd = [
        str(iscc), "/Qp", f"/DAppVersion={version}", f"/DSourceDir={APP_DIR}", f"/DOutputDir={DIST}",
        f"/DRootDir={ROOT}", str(PACKAGING / "installer.iss"),
    ]
    if subprocess.run(cmd, cwd=PACKAGING).returncode != 0:
        raise BuildError("Inno Setup falló")
    installer = DIST / f"BattleLens-Setup-{version}.exe"
    if not installer.exists():
        raise BuildError(f"No se generó {installer}")
    return installer


def build_zip(version: str) -> Path:
    archive = DIST / f"BattleLens-{version}-portable.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for f in sorted(APP_DIR.rglob("*")):
            if f.is_file():
                zf.write(f, Path("BattleLens") / f.relative_to(APP_DIR))
    return archive


def write_checksums(files: list[Path]) -> Path:
    lines = []
    for f in files:
        digest = hashlib.sha256(f.read_bytes()).hexdigest()
        lines.append(f"{digest}  {f.name}")
    out = DIST / "SHA256SUMS.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skip-installer", action="store_true", help="no generar instalador ni ZIP")
    parser.add_argument("--require-installer", action="store_true", help="fallar si no se encuentra Inno Setup")
    parser.add_argument("--self-test", action="store_true", help="ejecutar BattleLens.exe --self-test")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    version = read_version()
    print(f"== BattleLens {version}")
    try:
        run_pyinstaller(version)
        add_top_level_files()
        prune()
        size = folder_mb(APP_DIR)
        print(f"== Carpeta del programa: {size:.1f} MB (máx. {MAX_APP_MB})")
        if size > MAX_APP_MB:
            raise BuildError(f"La carpeta ocupa {size:.1f} MB y el máximo es {MAX_APP_MB} MB")
        if args.self_test:
            print("== Autocomprobación")
            self_test()

        if not args.skip_installer:
            artifacts = []
            iscc = find_iscc()
            if iscc:
                installer = build_installer(version, iscc)
                mb = installer.stat().st_size / 1024 / 1024
                print(f"== Instalador: {installer.name} ({mb:.1f} MB, máx. {MAX_INSTALLER_MB})")
                if mb > MAX_INSTALLER_MB:
                    raise BuildError(f"El instalador ocupa {mb:.1f} MB y el máximo es {MAX_INSTALLER_MB} MB")
                artifacts.append(installer)
            elif args.require_installer:
                raise BuildError("No se encontró ISCC.exe (Inno Setup 6)")
            else:
                print("== Inno Setup no encontrado: se omite el instalador")
            archive = build_zip(version)
            print(f"== ZIP portable: {archive.name} ({archive.stat().st_size / 1024 / 1024:.1f} MB)")
            artifacts.append(archive)
            print(f"== {write_checksums(artifacts).name}")
    except (BuildError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
