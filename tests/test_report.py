"""Informe de un problema (add-problem-report)."""

import json
import sys
import zipfile
from datetime import datetime
from urllib.parse import parse_qs, urlparse

import numpy as np
import pytest

from battlelens.core.report import ReportInputs, issue_form_url, sanitize, write_report

HOME = r"C:\Users\ash"
NOW = datetime(2026, 10, 14, 21, 30, 5)


def _data_dir(tmp_path):
    data = tmp_path / "BattleLens"
    (data / "profiles").mkdir(parents=True)
    (data / "debug").mkdir()
    (data / "config.toml").write_text('[overlay]\nlanguage = "es"\n', encoding="utf-8")
    (data / "profiles" / "abc.json").write_text('{"name": "Esmeralda"}', encoding="utf-8")
    (data / "app.log").write_text(f"INFO guardado en {HOME}\\AppData\\Roaming\\BattleLens\\debug por ash\n",
                                  encoding="utf-8")
    (data / "app.log.1").write_text("INFO anterior\n", encoding="utf-8")
    for i in range(25):
        (data / "debug" / f"{i:02d}-recorte.png").write_bytes(b"\x89PNG fake")
    return data


def test_limpieza_de_rutas_y_usuario():
    text = r"C:\Users\ash\AppData y c:/users/ash/x, usuario ash, pero no ashley ni flash"
    assert sanitize(text, HOME, "ash") == (
        r"%USERPROFILE%\AppData y %USERPROFILE%/x, usuario <usuario>, pero no ashley ni flash"
    )


def test_contenido_del_zip(tmp_path):
    data = _data_dir(tmp_path)
    frame = np.zeros((160, 240, 3), np.uint8)
    inputs = ReportInputs(
        data, {"version": "0.3.0", "emulador": {"exe": "mGBA.exe", "titulo": f"{HOME}\\roms\\emerald.gba"}},
        "No reconoce a Pidgey", frame, {"rival": frame[:20, :80], "own": frame[100:120, :80]},
        {"rival": {"texto": "PIDGEY", "especie": "pidgey", "puntuacion": 100.0, "nivel": 5}},
    )
    path = write_report(inputs, NOW, HOME, "ash")
    assert path == data / "informes" / "battlelens-informe-20261014-213005.zip"
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        assert {"informe.json", "config.toml", "profiles/abc.json", "app.log", "app.log.1",
                "captura/emulador.png", "captura/rival.png", "captura/own.png", "captura/lecturas.json"} <= names
        assert len([n for n in names if n.startswith("debug/")]) == 20  # solo los más recientes
        summary = json.loads(zf.read("informe.json"))
        assert summary["descripcion"] == "No reconoce a Pidgey" and summary["captura"] == {"incluida": True}
        assert summary["emulador"]["titulo"] == "%USERPROFILE%\\roms\\emerald.gba"
        log = zf.read("app.log").decode("utf-8")
        assert "ash" not in log and "%USERPROFILE%\\AppData" in log and "<usuario>" in log
    assert not list((data / "informes").glob("*.tmp"))


def test_informe_sin_captura(tmp_path):
    data = _data_dir(tmp_path)
    inputs = ReportInputs(data, {"version": "0.3.0"}, capture_error="WindowMinimized: ventana minimizada")
    with zipfile.ZipFile(write_report(inputs, NOW, HOME, "ash")) as zf:
        summary = json.loads(zf.read("informe.json"))
        assert summary["captura"] == {"incluida": False, "motivo": "WindowMinimized: ventana minimizada"}
        assert not any(n.startswith("captura/") for n in zf.namelist())


def test_url_del_formulario():
    url = issue_form_url("0.3.0", "mGBA.exe", "Emerald")
    parsed = urlparse(url)
    assert parsed.path.endswith("/issues/new")
    assert parse_qs(parsed.query) == {"template": ["bug_report.yml"], "version": ["0.3.0"],
                                      "emulator": ["mGBA.exe"], "game": ["Emerald"]}
    assert "game=" not in issue_form_url("0.3.0", "mGBA.exe", None)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows")
def test_controlador_crea_el_informe(qapp, tmp_path, monkeypatch):
    from battlelens import app as app_module
    from battlelens.app import Controller
    from battlelens.core.config import Config
    from battlelens.core.pokedex import Pokedex
    from battlelens.core.profiles import Profile, Region
    from battlelens.platform.capture import WindowMinimized
    from battlelens.platform.windows import WindowInfo

    monkeypatch.setenv("BATTLELENS_HOME", str(tmp_path))
    config = Config(hotkey_recognize="Ctrl+Alt+Shift+F20", hotkey_calibrate="Ctrl+Alt+Shift+F21",
                    hotkey_hide="Ctrl+Alt+Shift+F22", hotkey_toggle_mode="Ctrl+Alt+Shift+F18",
                    hotkey_cycle_form="Ctrl+Alt+Shift+F17", hotkey_toggle_stream="Ctrl+Alt+Shift+F16",
                    updates_check=False, detection_enabled=False)
    controller = Controller(qapp, config, Pokedex.load())
    try:
        profile = Profile("Esmeralda", Region(0.1, 0.1, 0.3, 0.1), game="emerald",
                          own_region=Region(0.5, 0.6, 0.3, 0.1))
        controller.profiles.save(profile)
        target = WindowInfo(1, "mGBA - emerald", "mGBA.exe", 1)
        monkeypatch.setattr(app_module, "capture_client", lambda hwnd: np.full((160, 240, 3), 255, np.uint8))
        path, url = controller._build_report("prueba", target, profile)
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            assert {"captura/emulador.png", "captura/rival.png", "captura/own.png", "captura/lecturas.json"} <= set(names)
            summary = json.loads(zf.read("informe.json"))
            assert summary["emulador"]["exe"] == "mGBA.exe" and summary["perfil"]["juego"] == "emerald"
        assert "emulator=mGBA.exe" in url and "game=Emerald" in url

        def minimized(hwnd):
            raise WindowMinimized()

        monkeypatch.setattr(app_module, "capture_client", minimized)
        path, _ = controller._build_report("", target, profile)
        with zipfile.ZipFile(path) as zf:
            assert json.loads(zf.read("informe.json"))["captura"]["incluida"] is False
    finally:
        controller.hotkeys.stop()
        controller.tray.hide()
        controller.overlay.close()


@pytest.mark.skipif(sys.platform != "win32", reason="Windows")
def test_dialogo_del_informe(qapp):
    from battlelens.ui.report import ReportDialog

    with_window = ReportDialog(True)
    assert with_window.include_capture.isChecked() and with_window.open_form.isChecked()
    with_window.description.setPlainText("  No reconoce a Pidgey  ")
    assert with_window.values() == ("No reconoce a Pidgey", True, True)
    without = ReportDialog(False)
    assert not without.include_capture.isChecked() and not without.include_capture.isEnabled()
