"""Ciclo de reconocimiento: captura → recorte → preprocesado → OCR → coincidencia."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image

from .core.matcher import MatchResult, NameMatcher
from .core.normalize import extract_level
from .core.pokedex import Pokedex, Species
from .core.profiles import Profile
from .vision.preprocess import crop_region, fingerprint, level_variants, preprocess_variants

log = logging.getLogger(__name__)

CaptureFn = Callable[[int], np.ndarray]
OcrFn = Callable[[np.ndarray, tuple[str, ...]], "OcrLike"]


class OcrLike:  # protocolo mínimo de platform.ocr.OcrOutput
    text: str


@dataclass(frozen=True)
class RecognitionResult:
    match: MatchResult
    species: Species | None
    timings_ms: dict[str, float] = field(default_factory=dict)
    fingerprint: np.ndarray | None = None  # huella combinada de las regiones (detección automática)
    rival2: MatchResult | None = None  # 2.º rival (combates dobles), si el perfil tiene esa región
    own: MatchResult | None = None  # tu Pokémon, si el perfil tiene esa región
    levels: tuple[int | None, int | None, int | None] = (None, None, None)  # (rival, rival2, own)

    @property
    def recognized(self) -> bool:
        return self.species is not None

    @property
    def any_rival(self) -> bool:
        return self.species is not None or (self.rival2 is not None and self.rival2.recognized)

    @property
    def key(self) -> tuple[int | None, int | None, int | None]:
        """Combinación (rival, 2.º rival, tu Pokémon) para la detección automática."""
        return (
            self.match.species_id,
            self.rival2.species_id if self.rival2 else None,
            self.own.species_id if self.own else None,
        )


@dataclass(frozen=True)
class CropReading:
    match: MatchResult
    image: np.ndarray
    readings: tuple[str, ...]

    @property
    def level(self) -> int | None:
        """Nivel leído en cualquiera de las lecturas, empezando por la de mejor coincidencia (level-reading)."""
        return extract_level([self.match.raw_text, *self.readings])


LEVEL_EXTRA_VARIANTS = 3


def read_crop(crop: np.ndarray, ocr_fn: OcrFn, matcher: NameMatcher, languages: tuple[str, ...]) -> CropReading:
    """Pasa cada variante preprocesada por el OCR y conserva la de mayor puntuación.

    Se detiene en cuanto una variante alcanza 100 y se ha leído el nivel. Si el nivel no aparece,
    prueba unas pocas variantes más y la mitad derecha ampliada (improve-level-reading D2-D3).
    """
    variants = preprocess_variants(crop)
    best: MatchResult | None = None
    best_image = variants[0]
    readings: list[str] = []
    pending = list(variants)
    while pending:
        image = pending.pop(0)
        text = ocr_fn(image, languages).text
        readings.append(text)
        match = matcher.match(text)
        if best is None or match.score > best.score or (not best.raw_text.strip() and text.strip()):
            best, best_image = match, image
        if match.score >= 100:
            break
    if best is not None and best.score >= 100 and extract_level([best.raw_text, *readings]) is None:
        extra = [*(v for v in pending if v.ndim == 2 and not _is_binary(v)), *(v for v in pending if _is_binary(v))]
        for image in extra[:LEVEL_EXTRA_VARIANTS]:
            readings.append(ocr_fn(image, languages).text)
            if extract_level(readings[-1:]) is not None:
                break
        else:
            readings += [ocr_fn(image, languages).text for image in level_variants(crop)]
    return CropReading(best, best_image, tuple(readings))


def _is_binary(image: np.ndarray) -> bool:
    return image.ndim == 2 and bool(np.isin(image, (0, 255)).all())


def crop_regions(frame: np.ndarray, profile: Profile) -> dict[str, np.ndarray]:
    """Recorta de una misma captura cada región configurada (rival, rival2, own)."""
    return {role: crop_region(frame, region) for role, region in profile.regions().items()}


def combined_fingerprint(crops: dict[str, np.ndarray]) -> np.ndarray:
    """Huellas de todas las regiones concatenadas en horizontal (design.md D3)."""
    return np.hstack([fingerprint(c) for c in crops.values()])


def read_regions(
    crops: dict[str, np.ndarray], ocr_fn: OcrFn, matcher: NameMatcher, languages: tuple[str, ...]
) -> dict[str, CropReading]:
    return {role: read_crop(crop, ocr_fn, matcher, languages) for role, crop in crops.items()}


def levels_of(readings: dict[str, CropReading]) -> tuple[int | None, int | None, int | None]:
    return tuple(readings[r].level if r in readings else None for r in ("rival", "rival2", "own"))  # type: ignore[return-value]


class RecognitionPipeline:
    def __init__(
        self,
        pokedex: Pokedex,
        matcher: NameMatcher,
        capture_fn: CaptureFn,
        ocr_fn: OcrFn,
        debug_dir: Path | None = None,
    ) -> None:
        self.pokedex = pokedex
        self.matcher = matcher
        self.capture_fn = capture_fn
        self.ocr_fn = ocr_fn
        self.debug_dir = debug_dir

    def run(self, hwnd: int, profile: Profile) -> RecognitionResult:
        """Lanza CaptureError u OcrLanguageError si no se puede completar el ciclo."""
        timings: dict[str, float] = {}
        t0 = time.perf_counter()

        def lap(name: str) -> None:
            nonlocal t0
            now = time.perf_counter()
            timings[name] = round((now - t0) * 1000, 1)
            t0 = now

        frame = self.capture_fn(hwnd)
        lap("captura")
        crops = crop_regions(frame, profile)
        lap("recorte")
        readings_by_role = read_regions(crops, self.ocr_fn, self.matcher, profile.ocr_languages)
        reading = readings_by_role["rival"]
        crop = crops["rival"]
        best, best_image, readings = reading.match, reading.image, list(reading.readings)
        rival2 = readings_by_role["rival2"].match if "rival2" in readings_by_role else None
        own = readings_by_role["own"].match if "own" in readings_by_role else None
        levels = levels_of(readings_by_role)
        lap("ocr")
        timings["total"] = round(sum(timings.values()), 1)

        species = self.pokedex.get_species(best.species_id) if best.species_id is not None else None
        log.info(
            "OCR=%r → %s (%.0f) en %s ms [%d variantes]",
            best.raw_text,
            species.identifier if species else "no reconocido",
            best.score,
            timings,
            len(readings),
        )
        if self.debug_dir is not None:
            self._dump(crop, best_image, profile, best, timings, readings)
        return RecognitionResult(best, species, timings, combined_fingerprint(crops), rival2, own, levels)

    def _dump(self, crop, processed, profile, match: MatchResult, timings, readings: list[str]) -> None:
        try:
            self.debug_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            _write_png(self.debug_dir / f"{stamp}-recorte.png", crop)
            _write_png(self.debug_dir / f"{stamp}-preprocesado.png", processed)
            (self.debug_dir / f"{stamp}.json").write_text(
                json.dumps(
                    {
                        "perfil": profile.name,
                        "ocr": match.raw_text,
                        "candidato": match.matched_name,
                        "especie": match.species_id,
                        "puntuacion": match.score,
                        "tiempos_ms": timings,
                        "lecturas": readings,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
        except OSError as exc:
            log.warning("No se pudo guardar el volcado de depuración: %s", exc)


def _write_png(path: Path, image: np.ndarray) -> None:
    Image.fromarray(image).save(path, format="PNG")
