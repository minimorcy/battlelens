"""Perfiles de calibración por juego con regiones relativas al área cliente."""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path

from ..i18n import _
from .storage import write_json_atomic

log = logging.getLogger(__name__)

MIN_REGION_PX = 8
DEFAULT_OCR_LANGUAGES = ("es", "en")
_EPS = 1e-6


class ProfileError(ValueError):
    pass


class RegionTooSmallError(ProfileError):
    def __init__(self, width: int, height: int) -> None:
        super().__init__(
            _("La región mide {width}×{height} px; el mínimo es {min} px de ancho y de alto.",
              width=width, height=height, min=MIN_REGION_PX)
        )


@dataclass(frozen=True)
class Region:
    """Rectángulo en fracciones [0, 1] del área cliente."""

    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        values = (self.x, self.y, self.width, self.height)
        if not all(isinstance(v, (int, float)) for v in values):
            raise ProfileError(_("La región debe contener números"))
        if not all(-_EPS <= v <= 1 + _EPS for v in values):
            raise ProfileError(_("Las coordenadas de la región deben estar en [0, 1]"))
        if self.width <= 0 or self.height <= 0:
            raise ProfileError(_("La región debe tener ancho y alto positivos"))
        if self.x + self.width > 1 + _EPS or self.y + self.height > 1 + _EPS:
            raise ProfileError(_("La región se sale del área cliente"))

    @classmethod
    def from_pixels(cls, x: int, y: int, width: int, height: int, client_w: int, client_h: int) -> Region:
        if width < MIN_REGION_PX or height < MIN_REGION_PX:
            raise RegionTooSmallError(width, height)
        return cls(
            round(x / client_w, 6),
            round(y / client_h, 6),
            round(width / client_w, 6),
            round(height / client_h, 6),
        )

    def remap(self, source: Region, target: Region) -> Region:
        """La misma posición relativa a `source` (la imagen del juego al calibrar), llevada a `target`."""
        x = target.x + (self.x - source.x) / source.width * target.width
        y = target.y + (self.y - source.y) / source.height * target.height
        w = self.width / source.width * target.width
        h = self.height / source.height * target.height
        x, y = min(max(x, 0.0), 1.0), min(max(y, 0.0), 1.0)
        w, h = max(min(w, 1.0 - x), 1e-6), max(min(h, 1.0 - y), 1e-6)
        return Region(round(x, 6), round(y, 6), round(w, 6), round(h, 6))

    def to_pixels(self, client_w: int, client_h: int) -> tuple[int, int, int, int]:
        x = min(max(round(self.x * client_w), 0), client_w - 1)
        y = min(max(round(self.y * client_h), 0), client_h - 1)
        w = max(1, min(round(self.width * client_w), client_w - x))
        h = max(1, min(round(self.height * client_h), client_h - y))
        return x, y, w, h


@dataclass(frozen=True)
class Profile:
    name: str
    region: Region
    ocr_languages: tuple[str, ...] = DEFAULT_OCR_LANGUAGES
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))
    game: str | None = None  # id del grupo de versiones (p. ej. "sword-shield"); None = sin especificar
    rival2_region: Region | None = None  # nombre del 2.º rival (combates dobles)
    own_region: Region | None = None  # nombre de tu Pokémon
    moves_region: Region | None = None  # menú de ataques; no es una región de nombre (add-own-moves D1)
    # Imagen del juego en el área cliente cuando se midieron las regiones (anchor-regions-to-game); None = perfil
    # antiguo: las regiones son fracciones fijas de la ventana
    game_area: Region | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ProfileError(_("El perfil necesita un nombre"))
        if not self.ocr_languages or not all(isinstance(lang, str) for lang in self.ocr_languages):
            raise ProfileError(_("El perfil necesita al menos un idioma de OCR"))

    def with_region(self, region: Region) -> Profile:
        return replace(self, region=region)

    def with_game(self, game: str | None) -> Profile:
        return replace(self, game=game)

    def with_role_region(self, role: str, region: Region | None) -> Profile:
        """Cambia la región de un rol: "rival", "rival2", "own" o "moves" (None la quita, salvo "rival")."""
        if role == "rival":
            if region is None:
                raise ProfileError(_("La región del rival es obligatoria"))
            return replace(self, region=region)
        if role == "rival2":
            return replace(self, rival2_region=region)
        if role == "own":
            return replace(self, own_region=region)
        if role == "moves":
            return replace(self, moves_region=region)
        raise ValueError(role)

    def placed(self, area: Region) -> Profile:
        """Las regiones llevadas a la imagen del juego `area` de la captura actual."""
        if self.game_area is None or area == self.game_area:
            return self

        def move(region: Region | None) -> Region | None:
            return region.remap(self.game_area, area) if region is not None else None

        return replace(self, region=move(self.region), rival2_region=move(self.rival2_region),
                       own_region=move(self.own_region), moves_region=move(self.moves_region), game_area=area)

    def regions(self) -> dict[str, Region]:
        """Regiones configuradas en orden fijo: rival, rival2, own (design.md D1)."""
        found = {"rival": self.region, "rival2": self.rival2_region, "own": self.own_region}
        return {role: region for role, region in found.items() if region is not None}

    def to_dict(self) -> dict:
        data = asdict(self)
        data["ocr_languages"] = list(self.ocr_languages)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Profile:
        try:
            region = Region(**data["region"])
            return cls(
                name=data["name"],
                region=region,
                ocr_languages=tuple(data.get("ocr_languages") or DEFAULT_OCR_LANGUAGES),
                id=data["id"],
                created_at=data["created_at"],
                game=data.get("game"),
                rival2_region=Region(**data["rival2_region"]) if data.get("rival2_region") else None,
                own_region=Region(**data["own_region"]) if data.get("own_region") else None,
                moves_region=Region(**data["moves_region"]) if data.get("moves_region") else None,
                game_area=Region(**data["game_area"]) if data.get("game_area") else None,
            )
        except (KeyError, TypeError) as exc:
            raise ProfileError(_("Perfil con formato inválido: {error}", error=exc)) from exc


class ProfileStore:
    """Perfiles en disco (un JSON por perfil) y selección del perfil activo."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.profiles: dict[str, Profile] = {}
        self.active_id: str | None = None

    def load(self, preferred_active: str | None = None) -> None:
        self.profiles.clear()
        if self.directory.is_dir():
            for path in sorted(self.directory.glob("*.json")):
                try:
                    profile = Profile.from_dict(json.loads(path.read_text(encoding="utf-8")))
                except (OSError, ValueError) as exc:
                    log.warning("Perfil ignorado (%s): %s", path.name, exc)
                    continue
                self.profiles[profile.id] = profile
        self.active_id = preferred_active if preferred_active in self.profiles else self._first_id()

    @property
    def active(self) -> Profile | None:
        return self.profiles.get(self.active_id) if self.active_id else None

    def find_by_game(self, game: str) -> Profile | None:
        """Perfil de un juego: el activo si ya lo es; si no, el primero por nombre."""
        active = self.active
        if active is not None and active.game == game:
            return active
        return next((p for p in self.sorted_profiles() if p.game == game), None)

    def sorted_profiles(self) -> list[Profile]:
        return sorted(self.profiles.values(), key=lambda p: p.name.lower())

    def set_active(self, profile_id: str) -> None:
        if profile_id not in self.profiles:
            raise KeyError(profile_id)
        self.active_id = profile_id

    def save(self, profile: Profile, activate: bool = True) -> None:
        write_json_atomic(self._path(profile.id), profile.to_dict())
        self.profiles[profile.id] = profile
        if activate or self.active_id is None:
            self.active_id = profile.id

    def delete(self, profile_id: str) -> None:
        self._path(profile_id).unlink(missing_ok=True)
        self.profiles.pop(profile_id, None)
        if self.active_id == profile_id or self.active_id not in self.profiles:
            self.active_id = self._first_id()

    def _first_id(self) -> str | None:
        ordered = self.sorted_profiles()
        return ordered[0].id if ordered else None

    def _path(self, profile_id: str) -> Path:
        return self.directory / f"{profile_id}.json"
