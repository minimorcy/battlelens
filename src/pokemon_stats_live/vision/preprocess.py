"""Preparación del recorte del nombre para el OCR (fuentes pixeladas)."""

from __future__ import annotations

import cv2
import numpy as np

from ..core.profiles import Region

# Alturas (px) a las que se normaliza el recorte y desenfoque opcional. El OCR de Windows
# lee mejor el texto pixelado a alturas pequeñas; probar varias y quedarse con la mejor
# coincidencia es mucho más robusto que una única variante (ver design.md, D6).
VARIANT_HEIGHTS = (20, 24, 28, 32, 40)
VARIANT_BLURS = (0.0, 1.0)
PADDING_PX = 10


def crop_region(image: np.ndarray, region: Region) -> np.ndarray:
    """Recorta de una captura RGB (alto, ancho, 3) la región relativa del perfil."""
    h, w = image.shape[:2]
    x, y, rw, rh = region.to_pixels(w, h)
    return image[y : y + rh, x : x + rw].copy()


def binarize(crop: np.ndarray) -> np.ndarray:
    """Escala de grises + Otsu, con texto oscuro (0) sobre fondo claro (255)."""
    gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY) if crop.ndim == 3 else crop
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # El texto ocupa menos superficie que el fondo: si predomina el negro, el fondo es oscuro.
    if np.count_nonzero(binary) < binary.size / 2:
        binary = cv2.bitwise_not(binary)
    return binary


def preprocess(crop: np.ndarray, height: int = 24, blur: float = 0.0) -> np.ndarray:
    """Binariza, normaliza la altura del recorte a `height` px y añade margen blanco."""
    binary = binarize(crop)
    factor = height / binary.shape[0]
    interpolation = cv2.INTER_AREA if factor < 1 else cv2.INTER_NEAREST
    resized = cv2.resize(binary, None, fx=factor, fy=factor, interpolation=interpolation)
    if blur > 0:
        resized = cv2.GaussianBlur(resized, (0, 0), blur)
    return cv2.copyMakeBorder(
        resized, PADDING_PX, PADDING_PX, PADDING_PX, PADDING_PX, cv2.BORDER_CONSTANT, value=255
    )


def preprocess_variants(crop: np.ndarray) -> list[np.ndarray]:
    """Todas las variantes a probar con el OCR, de la más a la menos prometedora."""
    return [preprocess(crop, h, b) for b in VARIANT_BLURS for h in VARIANT_HEIGHTS]
