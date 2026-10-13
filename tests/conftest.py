import pytest


@pytest.fixture(scope="session")
def qapp():
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(scope="session")
def requires_ocr():
    """Omite el test si Windows no tiene un paquete de OCR compatible (p. ej. en un runner de CI)."""
    import sys

    if sys.platform != "win32":
        pytest.skip("OCR nativo de Windows")
    from battlelens.platform.ocr import OcrLanguageError, available_languages, resolve_languages

    try:
        return resolve_languages(("es", "en", "fr", "de", "it"))
    except OcrLanguageError:
        pytest.skip(f"sin paquete de OCR es/en/fr/de/it (instalados: {available_languages() or 'ninguno'})")
