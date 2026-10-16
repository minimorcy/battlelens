"""Localización de la imagen del juego dentro del área cliente del emulador (add-game-presets D2).

1. Bandas: solo las filas y columnas oscuras y lisas son fondo del emulador (bandas al escalar sin
   deformar, hueco entre las pantallas de DS). La imagen es el bloque más grande entre ellas. Las filas
   lisas claras pueden ser del propio juego (fondos blancos), así que no se descartan.
2. DS: si el bloque tiene las dos pantallas (en vertical u horizontal), se toma la superior/izquierda.
3. Proporción: lo que sobra (barras claras de menús o de estado, con texto) se separa por el borde más
   marcado.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

UNIFORM_STD = 4.0  # desviación típica de luminancia por debajo de la cual una fila/columna es lisa
DARK_LUMA = 40.0  # las bandas del emulador son oscuras
MIN_BAND_PX = 4
MIN_BAND_FRACTION = 0.015
ASPECT_TOLERANCE = 0.06
MIN_KEPT = 0.85  # si hay que recortar más, la proporción de partida no era la del juego
DS_STACKED = 256 / 384  # dos pantallas en vertical
DS_SIDE_BY_SIDE = 512 / 192  # dos pantallas en horizontal
DS_LAYOUT_TOLERANCE = 0.12


@dataclass(frozen=True)
class Viewport:
    x: int
    y: int
    width: int
    height: int
    reliable: bool = True

    @property
    def aspect(self) -> float:
        return self.width / self.height if self.height else 0.0


def _luma(frame: np.ndarray) -> np.ndarray:
    if frame.ndim == 2:
        return frame.astype(np.float32)
    rgb = frame[..., :3].astype(np.float32)
    return rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114


def _longest_run(mask: np.ndarray) -> tuple[int, int]:
    """(inicio, fin) del tramo más largo de valores verdaderos; el primero si hay empate."""
    best, start = (0, 0), None
    for i, value in enumerate(np.append(mask, False)):
        if value and start is None:
            start = i
        elif not value and start is not None:
            if i - start > best[1] - best[0]:
                best = (start, i)
            start = None
    return best


def _bands(mask: np.ndarray) -> np.ndarray:
    """Solo cuentan como bandas los tramos oscuros con grosor suficiente: las líneas negras finas del
    propio juego (bordes de cuadros de texto) no parten la imagen."""
    min_len = max(MIN_BAND_PX, round(len(mask) * MIN_BAND_FRACTION))
    bands = np.zeros_like(mask)
    start = None
    for i, value in enumerate(np.append(mask, False)):
        if value and start is None:
            start = i
        elif not value and start is not None:
            touches_edge = start == 0 or i == len(mask)
            if i - start >= min_len or touches_edge:
                bands[start:i] = True
            start = None
    return bands


def _content_box(luma: np.ndarray) -> tuple[int, int, int, int]:
    """(arriba, abajo, izquierda, derecha) del bloque más grande entre bandas oscuras y lisas."""
    h, w = luma.shape
    dark_rows = _bands((luma.std(axis=1) < UNIFORM_STD) & (luma.mean(axis=1) < DARK_LUMA))
    top, bottom = _longest_run(~dark_rows)
    if bottom <= top:
        return 0, h, 0, w
    block = luma[top:bottom]
    dark_cols = _bands((block.std(axis=0) < UNIFORM_STD) & (block.mean(axis=0) < DARK_LUMA))
    left, right = _longest_run(~dark_cols)
    if right <= left:
        return top, bottom, 0, w
    return top, bottom, left, right


def _best_cut(profile: np.ndarray, start: int, excess: int, target: int) -> int:
    """Desplazamiento (0..excess) que deja los bordes más marcados en los dos extremos de la imagen.

    El corte en k pone la imagen en [start + k, start + k + target): se suman los saltos de luminancia
    justo antes de su primera fila y justo después de la última.
    """
    if excess <= 0:
        return 0
    jumps = np.abs(np.diff(profile))

    def jump(i: int) -> float:
        return float(jumps[i]) if 0 <= i < len(jumps) else 0.0

    scores = [(jump(start + k - 1) + jump(start + k + target - 1), -abs(k - excess / 2), k) for k in range(excess + 1)]
    return max(scores)[2]


def _fit(luma: np.ndarray, box: tuple[int, int, int, int], aspect: float) -> tuple[int, int, int, int]:
    """Recorta lo que sobra del recuadro para la proporción pedida, cortando por el borde más marcado."""
    top, bottom, left, right = box
    height, width = bottom - top, right - left
    if abs(width / height - aspect) / aspect <= 0.01:
        return box
    if width / height < aspect:  # sobra altura: barra de menús arriba o de estado abajo
        target = round(width / aspect)
        top_cut = _best_cut(luma[:, left:right].mean(axis=1), top, height - target, target)
        return top + top_cut, top + top_cut + target, left, right
    target = round(height * aspect)
    left_cut = _best_cut(luma[top:bottom, :].mean(axis=0), left, width - target, target)
    return top, bottom, left + left_cut, left + left_cut + target


def _ds_top_screen(box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """Pantalla superior (o izquierda) si el recuadro tiene las dos pantallas de DS juntas."""
    top, bottom, left, right = box
    height, width = bottom - top, right - left
    ratio = width / height
    if abs(ratio - DS_STACKED) / DS_STACKED <= DS_LAYOUT_TOLERANCE:
        return top, top + height // 2, left, right
    if abs(ratio - DS_SIDE_BY_SIDE) / DS_SIDE_BY_SIDE <= DS_LAYOUT_TOLERANCE:
        return top, bottom, left, left + width // 2
    return box


def find_viewport(frame: np.ndarray, aspect: float, ds: bool = False) -> Viewport:
    """Rectángulo de la imagen del juego (o de la pantalla superior de DS) en píxeles del área cliente."""
    luma = _luma(frame)
    box = _content_box(luma)
    if ds:
        box = _ds_top_screen(box)
    top, bottom, left, right = _fit(luma, box, aspect)
    width, height = right - left, bottom - top
    reliable = height > 0 and abs(width / height - aspect) / aspect <= ASPECT_TOLERANCE
    kept = (width * height) / max(1, (box[1] - box[0]) * (box[3] - box[2]))
    # Una pantalla lisa (negro entre escenas, fundidos) no dice dónde está la imagen.
    has_content = height > 0 and width > 0 and float(luma[top:bottom, left:right].std()) >= UNIFORM_STD
    return Viewport(left, top, width, height, reliable and kept >= MIN_KEPT and has_content)
