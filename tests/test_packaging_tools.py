import importlib.util
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "packaging" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release_notes = _load("release_notes")
build = _load("build")

CHANGELOG = """# Changelog

## [0.3.0] - 2026-11-01

### Añadido
- Combates dobles.

## [0.2.0] - 2026-10-20

### Añadido
- Instalador.

## [0.1.0] - 2026-10-13

- Primera versión.
"""


def test_extrae_seccion_intermedia():
    section = release_notes.extract_section(CHANGELOG, "0.2.0")
    assert section == "### Añadido\n- Instalador."


def test_extrae_ultima_seccion():
    assert release_notes.extract_section(CHANGELOG, "0.1.0") == "- Primera versión."


def test_version_inexistente():
    with pytest.raises(release_notes.ChangelogError):
        release_notes.extract_section(CHANGELOG, "9.9.9")


def test_notas_incluyen_instalacion_y_aviso():
    notes = release_notes.build_notes(CHANGELOG, "0.2.0")
    assert "BattleLens-Setup-0.2.0.exe" in notes
    assert "SmartScreen" in notes and "no oficial" in notes
    assert "Combates dobles" not in notes


def test_changelog_real_tiene_la_version_actual():
    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    assert release_notes.extract_section((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), version)


@pytest.mark.parametrize(("version", "expected"), [("0.2.0", (0, 2, 0, 0)), ("1.10.3", (1, 10, 3, 0)), ("0.2.0+dev", (0, 2, 0, 0))])
def test_tupla_de_version(version, expected):
    assert build.version_tuple(version) == expected


def test_archivo_de_version_windows(tmp_path):
    out = tmp_path / "v.txt"
    build.write_version_file("0.2.0", out)
    text = out.read_text(encoding="utf-8")
    assert "filevers=(0, 2, 0, 0)" in text and "StringStruct('ProductVersion', '0.2.0')" in text
