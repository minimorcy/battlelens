import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("build_dataset", ROOT / "tools" / "build_dataset.py")
build_dataset = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_dataset)


def test_descarga_fallida_no_sobrescribe(tmp_path, monkeypatch):
    output = tmp_path / "pokedex.json"
    output.write_text('{"previo": true}', encoding="utf-8")

    def falla(name, use_cache):
        raise build_dataset.DownloadError("sin red")

    monkeypatch.setattr(build_dataset, "fetch_csv", falla)
    code = build_dataset.main(["--no-cache", "--output", str(output)])

    assert code != 0
    assert output.read_text(encoding="utf-8") == '{"previo": true}'
