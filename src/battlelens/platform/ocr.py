"""OCR nativo de Windows (Windows.Media.Ocr) a través de winrt."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from winrt.windows.globalization import Language
from winrt.windows.graphics.imaging import BitmapPixelFormat, SoftwareBitmap
from winrt.windows.media.ocr import OcrEngine
from winrt.windows.storage.streams import DataWriter


class OcrLanguageError(RuntimeError):
    def __init__(self, requested: tuple[str, ...] | list[str], available: list[str]) -> None:
        first = requested[0] if requested else "es"
        tag = {"es": "es-ES", "en": "en-US", "fr": "fr-FR", "de": "de-DE", "it": "it-IT"}.get(first, first)
        super().__init__(
            f"No hay OCR de Windows para los idiomas {list(requested)} (instalados: {available or 'ninguno'}). "
            "Instala el paquete en Configuración > Hora e idioma > Idioma y región > añadir idioma, "
            "o en PowerShell como administrador: "
            f'Add-WindowsCapability -Online -Name "Language.OCR~~~{tag}~0.0.1.0"'
        )


@dataclass(frozen=True)
class OcrOutput:
    text: str
    language: str | None


def available_languages() -> list[str]:
    return [lang.language_tag for lang in OcrEngine.available_recognizer_languages]


def resolve_languages(preferred: tuple[str, ...] | list[str]) -> list[str]:
    """Traduce las etiquetas del perfil ("es", "en-US"…) a idiomas de OCR instalados, en orden."""
    available = available_languages()
    resolved: list[str] = []
    for tag in preferred:
        primary = tag.lower().split("-")[0]
        exact = [a for a in available if a.lower() == tag.lower()]
        same_primary = [a for a in available if a.lower().split("-")[0] == primary]
        for candidate in exact or same_primary:
            if candidate not in resolved:
                resolved.append(candidate)
    if not resolved:
        raise OcrLanguageError(preferred, available)
    return resolved


@lru_cache(maxsize=None)
def _engine(language_tag: str) -> OcrEngine:
    return OcrEngine.try_create_from_language(Language(language_tag))


def _to_bitmap(image: np.ndarray) -> SoftwareBitmap:
    rgb = np.repeat(image[:, :, None], 3, axis=2) if image.ndim == 2 else image[:, :, :3]
    alpha = np.full((*rgb.shape[:2], 1), 255, dtype=np.uint8)
    rgba = np.ascontiguousarray(np.concatenate([rgb, alpha], axis=2), dtype=np.uint8)
    writer = DataWriter()
    writer.write_bytes(rgba.tobytes())
    return SoftwareBitmap.create_copy_from_buffer(
        writer.detach_buffer(), BitmapPixelFormat.RGBA8, rgba.shape[1], rgba.shape[0]
    )


async def _recognize_async(bitmap: SoftwareBitmap, language_tag: str) -> str:
    result = await _engine(language_tag).recognize_async(bitmap)
    return " ".join(line.text for line in result.lines).strip()


def recognize(image: np.ndarray, languages: tuple[str, ...] | list[str]) -> OcrOutput:
    """Ejecuta el OCR con cada idioma en orden y devuelve el primer resultado no vacío."""
    bitmap = _to_bitmap(image)
    for tag in resolve_languages(languages):
        text = asyncio.run(_recognize_async(bitmap, tag))
        if text:
            return OcrOutput(text, tag)
    return OcrOutput("", None)
