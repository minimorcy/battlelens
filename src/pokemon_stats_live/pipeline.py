"""Ciclo de reconocimiento: captura → recorte → preprocesado → OCR → coincidencia."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from .core.matcher import MatchResult, NameMatcher
from .core.pokedex import Pokedex, Species
from .core.profiles import Profile
from .vision.preprocess import crop_region, preprocess_variants

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

    @property
    def recognized(self) -> bool:
        return self.species is not None


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
        crop = crop_region(frame, profile.region)
        variants = preprocess_variants(crop)
        lap("preprocesado")

        # Se prueba cada variante y se conserva la de mayor puntuación (parada temprana con 100).
        best: MatchResult | None = None
        best_image = variants[0]
        readings: list[str] = []
        for image in variants:
            text = self.ocr_fn(image, profile.ocr_languages).text
            readings.append(text)
            match = self.matcher.match(text)
            if best is None or match.score > best.score or (not best.raw_text.strip() and text.strip()):
                best, best_image = match, image
            if match.score >= 100:
                break
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
        return RecognitionResult(best, species, timings)

    def _dump(self, crop, processed, profile, match: MatchResult, timings, readings: list[str]) -> None:
        try:
            self.debug_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            _write_png(self.debug_dir / f"{stamp}-recorte.png", cv2.cvtColor(crop, cv2.COLOR_RGB2BGR))
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
    # cv2.imwrite no admite rutas no ASCII en Windows; se codifica en memoria.
    ok, buf = cv2.imencode(".png", image)
    if ok:
        path.write_bytes(buf.tobytes())
