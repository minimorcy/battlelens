"""Informe de un problema: ZIP con todo lo necesario para reproducir un fallo (spec problem-report).

Sin Qt ni red: la app recoge los datos y aquí se escriben. Nada se envía; el tester adjunta el ZIP.
"""

from __future__ import annotations

import io
import json
import os
import re
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

import numpy as np
from PIL import Image

from .. import REPO_URL

REPORTS_DIR = "informes"
MAX_DEBUG_FILES = 20
TEXT_SUFFIXES = (".json", ".toml", ".txt", ".log")
ISSUE_TEMPLATE = "bug_report.yml"


@dataclass
class ReportInputs:
    data_dir: Path
    summary: dict  # resumen para informe.json (versión, sistema, idiomas, perfil…)
    description: str = ""
    emulator_image: np.ndarray | None = None
    region_crops: dict[str, np.ndarray] = field(default_factory=dict)
    readings: dict[str, dict] = field(default_factory=dict)
    capture_error: str | None = None


def sanitize(text: str, home: str | None = None, username: str | None = None) -> str:
    """Sustituye la carpeta del usuario por %USERPROFILE% y su nombre por <usuario> (spec problem-report)."""
    home = home if home is not None else str(Path.home())
    username = username if username is not None else (os.environ.get("USERNAME") or Path(home).name)
    if home:
        windows = home.replace("/", "\\")
        # Tal cual, con barras normales y escapada dentro de un JSON (C:\Users\…)
        for variant in sorted({windows, windows.replace("\\", "/"), windows.replace("\\", "\\\\")}, key=len, reverse=True):
            text = re.sub(re.escape(variant), "%USERPROFILE%", text, flags=re.IGNORECASE)
    if username and len(username) >= 2:
        text = re.sub(rf"(?<![\w]){re.escape(username)}(?![\w])", "<usuario>", text, flags=re.IGNORECASE)
    return text


def _is_text(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or ".log" in path.name.lower()


def _png(image: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    Image.fromarray(image).save(buffer, format="PNG")
    return buffer.getvalue()


def write_report(inputs: ReportInputs, now: datetime | None = None, home: str | None = None,
                 username: str | None = None) -> Path:
    """Escribe el ZIP en <datos>/informes/ y devuelve su ruta."""
    now = now or datetime.now()
    out_dir = inputs.data_dir / REPORTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"battlelens-informe-{now:%Y%m%d-%H%M%S}.zip"
    tmp = target.with_suffix(".zip.tmp")

    def clean(text: str) -> str:
        return sanitize(text, home, username)

    summary = dict(inputs.summary)
    summary["fecha"] = now.isoformat(timespec="seconds")
    summary["descripcion"] = inputs.description
    if inputs.capture_error:
        summary["captura"] = {"incluida": False, "motivo": inputs.capture_error}
    else:
        summary["captura"] = {"incluida": inputs.emulator_image is not None}

    try:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("informe.json", clean(json.dumps(summary, ensure_ascii=False, indent=2)))

            def add_file(path: Path, arcname: str) -> None:
                if _is_text(path):
                    zf.writestr(arcname, clean(path.read_text(encoding="utf-8", errors="replace")))
                else:
                    zf.write(path, arcname)

            config = inputs.data_dir / "config.toml"
            if config.is_file():
                add_file(config, "config.toml")
            for profile in sorted((inputs.data_dir / "profiles").glob("*.json")):
                add_file(profile, f"profiles/{profile.name}")
            for log in sorted(inputs.data_dir.glob("app.log*")):
                add_file(log, log.name)
            debug = inputs.data_dir / "debug"
            if debug.is_dir():
                recent = sorted((p for p in debug.iterdir() if p.is_file()), key=lambda p: p.stat().st_mtime)
                for path in recent[-MAX_DEBUG_FILES:]:
                    add_file(path, f"debug/{path.name}")
            if inputs.emulator_image is not None:
                zf.writestr("captura/emulador.png", _png(inputs.emulator_image))
            for role, crop in inputs.region_crops.items():
                zf.writestr(f"captura/{role}.png", _png(crop))
            if inputs.readings:
                zf.writestr("captura/lecturas.json", clean(json.dumps(inputs.readings, ensure_ascii=False, indent=2)))
        os.replace(tmp, target)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    return target


def issue_form_url(version: str | None, emulator: str | None, game: str | None) -> str:
    """Formulario de fallo de GitHub con los campos rellenados (spec problem-report)."""
    params = {"template": ISSUE_TEMPLATE, "version": version, "emulator": emulator, "game": game}
    return f"{REPO_URL}/issues/new?" + urlencode({k: v for k, v in params.items() if v})
