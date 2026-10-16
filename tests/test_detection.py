import numpy as np
import pytest

from battlelens.core.detection import Action, BattleDetector
from battlelens.vision.preprocess import fingerprint, fingerprint_distance


def fp(value: int) -> np.ndarray:
    """Huella sintética uniforme: valores distintos = escenas distintas."""
    return np.full((12, 32), value, dtype=np.uint8)


@pytest.fixture
def det():
    return BattleDetector(fingerprint_distance, hide_after_seconds=4.0)


def feed(det, values, start=0.0, step=0.5):
    """Envía huellas y devuelve las acciones; t avanza `step` s por ciclo."""
    return [det.on_frame(fp(v), start + i * step) for i, v in enumerate(values)]


def test_huella_de_tamano_fijo():
    a = fingerprint(np.zeros((118, 309, 3), np.uint8))
    b = fingerprint(np.full((40, 120, 3), 255, np.uint8))
    assert a.shape == b.shape == (12, 32)
    assert fingerprint_distance(a, b) == 255.0


def test_entrada_en_combate_reconoce_una_vez(det):
    actions = feed(det, [10, 10, 10, 10, 10])
    assert actions.count(Action.RECOGNIZE) == 1
    assert actions[2] == Action.RECOGNIZE  # tras 2 ciclos estables


def test_escena_en_movimiento_no_reconoce(det):
    assert Action.RECOGNIZE not in feed(det, [10, 60, 110, 160, 210, 20, 70])


def test_region_sin_cambios_no_repite(det):
    feed(det, [10, 10, 10])
    det.on_result(None, fp(10), 1.0)
    assert Action.RECOGNIZE not in feed(det, [10, 10, 10, 10], start=1.5)
    assert Action.RECOGNIZE in feed(det, [90, 90, 90], start=3.5)


def test_nuevo_rival_muestra(det):
    assert det.on_result(16, fp(10), 1.0) == Action.SHOW
    assert det.on_result(19, fp(90), 2.0) == Action.SHOW
    assert det.shown_species == 19


def test_misma_especie_no_vuelve_a_mostrar(det):
    det.on_result(759, fp(10), 1.0)
    det.on_hidden_by_user()
    assert det.on_result(759, fp(12), 2.0) == Action.NONE


def test_sin_reconocer_no_muestra(det):
    assert det.on_result(None, fp(10), 1.0) == Action.NONE


def test_fin_del_combate_oculta(det):
    feed(det, [10, 10, 10])
    det.on_result(759, fp(10), 1.0)
    actions = feed(det, [200] * 10, start=1.5)  # escenario distinto durante 5 s
    assert Action.HIDE in actions
    assert det.shown_species is None


def test_cambio_breve_no_oculta(det):
    feed(det, [10, 10, 10])
    det.on_result(759, fp(10), 1.0)
    actions = feed(det, [200, 200, 10, 10, 10, 10, 10, 10, 10, 10], start=1.5)
    assert Action.HIDE not in actions


def test_cambio_de_barra_de_ps_con_reconocimiento_no_oculta(det):
    det.on_result(759, fp(10), 0.0)
    feed(det, [40, 40, 40], start=0.5)  # la barra de PS cambia la huella
    det.on_result(759, fp(40), 2.0)  # se vuelve a reconocer la misma especie
    assert Action.HIDE not in feed(det, [40] * 10, start=2.5)


def test_mismo_rival_en_otro_combate_se_vuelve_a_mostrar(det):
    det.on_result(759, fp(10), 0.0)
    feed(det, [200] * 10, start=0.5)  # se oculta
    assert det.on_result(759, fp(10), 6.0) == Action.SHOW


def test_ocultacion_desactivada():
    det = BattleDetector(fingerprint_distance, hide_after_seconds=0)
    det.on_result(759, fp(10), 0.0)
    assert Action.HIDE not in feed(det, [200] * 20, start=0.5)


def test_resultado_manual_cuenta_como_mostrado(det):
    det.on_manual_result(16, fp(10))
    assert det.on_result(16, fp(10), 1.0) == Action.NONE


def test_huellas_de_distinta_forma_son_distintas():
    # Perfiles con distinto número de regiones: la huella combinada cambia de ancho (32 px por región)
    a = np.zeros((12, 64), np.uint8)
    b = np.zeros((12, 32), np.uint8)
    assert fingerprint_distance(a, b) == 255.0
    detector = BattleDetector(fingerprint_distance, hide_after_seconds=4.0)
    detector.on_frame(a, 0.0)
    detector.on_frame(b, 0.5)  # no lanza ValueError
