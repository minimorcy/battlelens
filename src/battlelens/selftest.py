"""Autocomprobación del ejecutable empaquetado (`BattleLens.exe --self-test`).

No crea interfaz: el resultado se escribe en un JSON y el código de salida indica el éxito.
"""

from __future__ import annotations

import importlib
import json
import time
from pathlib import Path

from . import __version__

REQUIRED_MODULES = (
    "PyQt6.QtWidgets",
    "mss",
    "numpy",
    "PIL.Image",
    "rapidfuzz",
    "ssl",  # comprobación de actualizaciones por HTTPS
    "battlelens.platform.ocr",
    "battlelens.platform.capture",
    "battlelens.platform.hotkeys",
    "battlelens.ui.overlay",
    "battlelens.ui.tray",
    "battlelens.ui.about",
    "battlelens.ui.settings",
    "battlelens.core.updates",
    "battlelens.stream.server",
    "http.server",
)


def run_checks() -> dict:
    checks: dict[str, dict[str, str]] = {}

    def record(name: str, fn) -> None:
        try:
            detail = fn()
            checks[name] = {"status": "ok", "detail": str(detail or "")}
        except _Warning as exc:
            checks[name] = {"status": "warn", "detail": str(exc)}
        except Exception as exc:  # noqa: BLE001 - cualquier fallo debe quedar registrado
            checks[name] = {"status": "fail", "detail": f"{type(exc).__name__}: {exc}"}

    for module in REQUIRED_MODULES:
        record(f"import:{module}", lambda m=module: importlib.import_module(m) and None)

    state: dict = {}

    def load_dataset():
        from .core.pokedex import Pokedex

        state["dex"] = Pokedex.load()
        return f"{len(state['dex'])} especies"

    def match_pidgey():
        from .core.matcher import NameMatcher

        result = NameMatcher(state["dex"]).match("PIDGEY")
        if result.species_id != 16:
            raise AssertionError(f"PIDGEY → {result.species_id}")
        return "PIDGEY → #16"

    def ocr_languages():
        from .platform.ocr import OcrLanguageError, resolve_languages

        try:
            return ", ".join(resolve_languages(("es", "en", "fr", "de", "it")))
        except OcrLanguageError as exc:
            raise _Warning(str(exc)) from exc

    def load_learnsets():
        from .core.learnsets import Learnsets

        moves = Learnsets.get().probable_moves("stufful", 10, "sword-shield", 8)
        if len(moves) != 4:
            raise AssertionError(f"Stufful Nv. 10: {len(moves)} movimientos")
        return "Stufful Nv. 10 → 4 movimientos"

    def stream_page():
        from .stream.server import STATIC_FILES, read_static

        sizes = {name: len(read_static(name)) for name, _ in STATIC_FILES.values()}
        return ", ".join(f"{name} {size} B" for name, size in sizes.items())

    record("dataset", load_dataset)
    record("learnsets", load_learnsets)
    record("match", match_pidgey)
    record("stream", stream_page)
    record("ocr", ocr_languages)

    ok = all(c["status"] != "fail" for c in checks.values())
    return {"app": "BattleLens", "version": __version__, "ok": ok, "checks": checks}


class _Warning(Exception):
    pass


def main(output: Path | None) -> int:
    start = time.perf_counter()
    report = run_checks()
    report["seconds"] = round(time.perf_counter() - start, 2)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if report["ok"] else 1
