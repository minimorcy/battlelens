"""Preparación del recorte del nombre para el OCR (fuentes pixeladas)."""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter

from ..core.profiles import Region

# Alturas (px) a las que se normaliza el recorte y desenfoque opcional. El OCR de Windows
# lee mejor el texto pixelado a alturas pequeñas; probar varias y quedarse con la mejor
# coincidencia es mucho más robusto que una única variante (ver design.md, D6).
VARIANT_HEIGHTS = (18, 20, 24, 28, 32, 36, 40)
VARIANT_BLURS = (0.0, 0.7)
# Variantes en gris sin binarizar: funcionan mejor con texto suavizado de juegos 3D (Switch, 3DS)
# y con regiones holgadas que incluyen fondos mezclados (ver tarea 9.2 de add-battle-overlay-mvp).
GRAY_HEIGHTS = (24, 32, 48)
PADDING_PX = 10


def crop_region(image: np.ndarray, region: Region) -> np.ndarray:
    """Recorta de una captura RGB (alto, ancho, 3) la región relativa del perfil."""
    h, w = image.shape[:2]
    x, y, rw, rh = region.to_pixels(w, h)
    return image[y : y + rh, x : x + rw].copy()


def to_gray(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return image
    return np.asarray(Image.fromarray(image).convert("L"))  # luminancia ITU-R 601


def otsu_threshold(gray: np.ndarray) -> int:
    """Umbral que maximiza la varianza entre clases (píxeles <= t frente a > t)."""
    hist = np.bincount(gray.ravel(), minlength=256).astype(np.float64)
    levels = np.arange(256, dtype=np.float64)
    w0 = np.cumsum(hist)
    w1 = w0[-1] - w0
    sum0 = np.cumsum(hist * levels)
    with np.errstate(divide="ignore", invalid="ignore"):
        m0 = sum0 / w0
        m1 = (sum0[-1] - sum0) / w1
        variance = w0 * w1 * (m0 - m1) ** 2
    return int(np.argmax(np.nan_to_num(variance)))


def binarize(crop: np.ndarray) -> np.ndarray:
    """Escala de grises + Otsu, con texto oscuro (0) sobre fondo claro (255)."""
    gray = to_gray(crop)
    binary = np.where(gray > otsu_threshold(gray), 255, 0).astype(np.uint8)
    # El texto ocupa menos superficie que el fondo: si predomina el negro, el fondo es oscuro.
    if np.count_nonzero(binary) < binary.size / 2:
        binary = 255 - binary
    return binary


def preprocess(crop: np.ndarray, height: int = 24, blur: float = 0.0) -> np.ndarray:
    """Binariza, normaliza la altura del recorte a `height` px y añade margen blanco."""
    binary = binarize(crop)
    factor = height / binary.shape[0]
    width = max(1, round(binary.shape[1] * factor))
    # Reducir con LANCZOS conserva mejor los trazos finos; ampliar sin interpolar mantiene los píxeles.
    resample = Image.Resampling.LANCZOS if factor < 1 else Image.Resampling.NEAREST
    image = Image.fromarray(binary).resize((width, height), resample)
    if blur > 0:
        image = image.filter(ImageFilter.GaussianBlur(radius=blur))
    return np.pad(np.asarray(image), PADDING_PX, constant_values=255)


def gray_variant(crop: np.ndarray, height: int) -> np.ndarray:
    """Escala de grises sin binarizar, con la altura normalizada y margen blanco."""
    gray = to_gray(crop)
    factor = height / gray.shape[0]
    width = max(1, round(gray.shape[1] * factor))
    resample = Image.Resampling.LANCZOS if factor < 1 else Image.Resampling.BICUBIC
    image = Image.fromarray(gray).resize((width, height), resample)
    return np.pad(np.asarray(image), PADDING_PX, constant_values=255)


def preprocess_variants(crop: np.ndarray) -> list[np.ndarray]:
    """Todas las variantes a probar con el OCR: original, grises y binarizadas (fuentes pixeladas)."""
    variants = [np.ascontiguousarray(crop)]
    variants += [gray_variant(crop, h) for h in GRAY_HEIGHTS]
    variants += [preprocess(crop, h, b) for b in VARIANT_BLURS for h in VARIANT_HEIGHTS]
    return variants


FINGERPRINT_SIZE = (32, 12)


def fingerprint(crop: np.ndarray) -> np.ndarray:
    """Huella barata del recorte para detectar cambios: miniatura en gris de 32×12 (battle-detection)."""
    small = Image.fromarray(to_gray(crop)).resize(FINGERPRINT_SIZE, Image.Resampling.BOX)
    return np.asarray(small, dtype=np.uint8)


def fingerprint_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Diferencia media absoluta (0-255) entre dos huellas."""
    return float(np.mean(np.abs(a.astype(np.int16) - b.astype(np.int16))))
