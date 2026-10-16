import json
import sys

import pytest

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows")


# ---- autocomprobación -------------------------------------------------------

def test_self_test_correcto(tmp_path):
    from battlelens import __version__
    from battlelens.app import main

    out = tmp_path / "res.json"
    assert main(["--self-test", "--self-test-output", str(out)]) == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["ok"] and report["version"] == __version__
    assert report["checks"]["dataset"]["status"] == "ok"
    assert report["checks"]["match"]["detail"] == "PIDGEY → #16"
    assert report["checks"]["ocr"]["status"] in {"ok", "warn"}
    assert all(c["status"] == "ok" for k, c in report["checks"].items() if k.startswith("import:"))


def test_self_test_dataset_ausente(tmp_path, monkeypatch):
    from battlelens import selftest
    from battlelens.core import pokedex

    def missing(cls, path=None):
        raise pokedex.DatasetMissingError("pokedex.json")

    monkeypatch.setattr(pokedex.Pokedex, "load", classmethod(missing))
    out = tmp_path / "res.json"
    assert selftest.main(out) != 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["checks"]["dataset"]["status"] == "fail"
    assert "pokedex.json" in report["checks"]["dataset"]["detail"]


def test_ocr_ausente_es_aviso(tmp_path, monkeypatch):
    from battlelens import selftest
    from battlelens.platform import ocr

    def no_ocr(preferred):
        raise ocr.OcrLanguageError(preferred, [])

    monkeypatch.setattr(ocr, "resolve_languages", no_ocr)
    assert selftest.main(tmp_path / "r.json") == 0
    report = json.loads((tmp_path / "r.json").read_text(encoding="utf-8"))
    assert report["checks"]["ocr"]["status"] == "warn"


# ---- instalación guiada del OCR ---------------------------------------------

@pytest.mark.parametrize(
    ("ui", "tag"),
    [("es-ES", "es-ES"), ("es-MX", "es-ES"), ("en-GB", "en-US"), ("de-AT", "de-DE"), ("pl-PL", "en-US"), ("ja-JP", "en-US")],
)
def test_idioma_propuesto(ui, tag):
    from battlelens.platform.ocr_setup import proposed_ocr_tag

    assert proposed_ocr_tag(ui) == tag


def test_idioma_interfaz_windows():
    from battlelens.platform.ocr_setup import ui_language_tag

    assert "-" in ui_language_tag()


def test_comando_powershell():
    from battlelens.platform.ocr_setup import capability_name, powershell_arguments

    assert capability_name("es-ES") == "Language.OCR~~~es-ES~0.0.1.0"
    args = powershell_arguments("es-ES")
    assert "Add-WindowsCapability -Online -Name 'Language.OCR~~~es-ES~0.0.1.0'" in args
    assert "-ErrorAction Stop" in args and "exit 1" in args and "-NoProfile" in args


@pytest.mark.parametrize(
    ("launched", "code", "outcome"),
    [(True, 0, "success"), (True, 1, "failed"), (False, 1223, "cancelled"), (False, 5, "failed")],
)
def test_resultados_de_instalacion(monkeypatch, launched, code, outcome):
    from battlelens.platform import ocr_setup

    monkeypatch.setattr(ocr_setup, "_run_elevated", lambda exe, params: (launched, code))
    result = ocr_setup.install_ocr("es-ES")
    assert result.outcome.value == outcome and result.tag == "es-ES"


# ---- interfaz ---------------------------------------------------------------

def test_acerca_de(qapp):
    from battlelens import REPO_URL, __version__
    from battlelens.ui.about import AboutPanel

    text = AboutPanel().text()
    assert f"Versión {__version__}" in text
    assert REPO_URL in text and "MIT" in text and "PokéAPI" in text and "no oficial" in text


def test_icono_original_cargado(qapp):
    from battlelens.ui.icons import app_icon

    assert not app_icon().isNull()


def test_menu_bandeja_ocr(qapp):
    from battlelens.ui.tray import Tray

    tray = Tray(lambda: [], lambda: None, lambda: ([], None), {})
    labels = [a.text() for a in tray.menu.actions()]
    assert "Instalar OCR de Windows…" in labels
    assert not tray.install_ocr_action.isVisible()
    tray.set_ocr_missing(True)
    assert tray.install_ocr_action.isVisible()
    tray.hide()
