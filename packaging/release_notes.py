"""Genera las notas de una Release a partir de CHANGELOG.md.

Uso:  uv run python packaging/release_notes.py 0.2.0 [--output dist/release-notes.md]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_HEADER = re.compile(r"^## \[(?P<version>[^\]]+)\]", re.MULTILINE)

INSTALL_NOTES = """\
## Instalación

1. Descarga **`BattleLens-Setup-{version}.exe`** (o el ZIP portable si no quieres instalar nada).
2. Ejecútalo. No pide permisos de administrador.
3. Si Windows muestra «Windows protegió su PC» (SmartScreen), pulsa **Más información → Ejecutar de todas formas**.
   Aparece porque el ejecutable no está firmado con un certificado de pago. Puedes comprobar la descarga con `SHA256SUMS.txt`.
4. BattleLens usa el OCR de Windows. Si falta el paquete de idioma, la app te ofrece instalarlo desde su menú.

## Installation

1. Download **`BattleLens-Setup-{version}.exe`** (or the portable ZIP if you'd rather not install anything).
2. Run it. No administrator rights needed.
3. If Windows shows "Windows protected your PC" (SmartScreen), click **More info → Run anyway**.
   It appears because the executable isn't signed with a paid certificate. You can verify the download with `SHA256SUMS.txt`.
4. BattleLens uses Windows' built-in OCR. If the language pack is missing, the app offers to install it from its menu.
"""

DISCLAIMER = (
    "> BattleLens es un proyecto de fans no oficial. No está afiliado ni respaldado por Nintendo, "
    "The Pokémon Company, Creatures Inc. ni GAME FREAK inc. Pokémon y los nombres de los Pokémon son "
    "marcas registradas de sus respectivos titulares. Datos de Pokémon: PokéAPI (BSD-3-Clause).\n>\n"
    "> BattleLens is an unofficial fan project. It is not affiliated with, endorsed, sponsored or approved by "
    "Nintendo, The Pokémon Company, Creatures Inc. or GAME FREAK inc. Pokémon and Pokémon character names are "
    "trademarks of their respective owners. Pokémon data: PokéAPI (BSD-3-Clause)."
)


class ChangelogError(ValueError):
    pass


def extract_section(changelog: str, version: str) -> str:
    matches = list(_HEADER.finditer(changelog))
    for i, m in enumerate(matches):
        if m.group("version") == version:
            end = matches[i + 1].start() if i + 1 < len(matches) else len(changelog)
            body = changelog[m.end() : end]
            body = body.split("\n", 1)[1] if "\n" in body else ""  # quita el resto de la línea del título
            return body.strip()
    raise ChangelogError(f"CHANGELOG.md no tiene sección para la versión {version}")


def build_notes(changelog: str, version: str) -> str:
    return "\n\n".join([extract_section(changelog, version), INSTALL_NOTES.format(version=version).strip(), DISCLAIMER]) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version")
    parser.add_argument("--changelog", type=Path, default=ROOT / "CHANGELOG.md")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        notes = build_notes(args.changelog.read_text(encoding="utf-8"), args.version)
    except ChangelogError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(notes, encoding="utf-8")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(notes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
