"""Comprobación de versión nueva en GitHub Releases (spec update-check)."""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable

from .. import REPO_URL, __version__

log = logging.getLogger(__name__)

API_URL = "https://api.github.com/repos/minimorcy/battlelens/releases/latest"
TIMEOUT_SECONDS = 5
CHECK_EVERY = timedelta(hours=24)
_VERSION = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


@dataclass(frozen=True)
class Release:
    version: str
    url: str


def parse_version(text: str | None) -> tuple[int, int, int] | None:
    match = _VERSION.match((text or "").strip())
    return tuple(int(g) for g in match.groups()) if match else None  # type: ignore[return-value]


def is_newer(candidate: str | None, current: str) -> bool:
    """True si `candidate` es una versión X.Y.Z válida y mayor que `current`."""
    new, cur = parse_version(candidate), parse_version(current.split("+")[0])
    return new is not None and (cur is None or new > cur)


def due(last_check: str | None, now: datetime | None = None) -> bool:
    if not last_check:
        return True
    try:
        last = datetime.fromisoformat(last_check)
    except ValueError:
        return True
    return (now or datetime.now(timezone.utc)) - last >= CHECK_EVERY


def _fetch_latest() -> dict:
    request = urllib.request.Request(
        API_URL,
        headers={"Accept": "application/vnd.github+json", "User-Agent": f"BattleLens/{__version__}"},
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def check_latest(current: str = __version__, fetch: Callable[[], dict] = _fetch_latest) -> Release | None:
    """Release más nueva que `current`, o None (al día, sin Releases o error de red, que solo se registra)."""
    try:
        data = fetch()
    except urllib.error.HTTPError as exc:
        log.info("Comprobación de actualizaciones: HTTP %s", exc.code)
        return None
    except (OSError, ValueError) as exc:
        log.info("Comprobación de actualizaciones fallida: %s", exc)
        return None
    if not isinstance(data, dict):
        log.info("Comprobación de actualizaciones: respuesta inesperada")
        return None
    tag = data.get("tag_name")
    if not is_newer(tag, current):
        return None
    version = ".".join(str(n) for n in parse_version(tag))
    return Release(version, data.get("html_url") or f"{REPO_URL}/releases/latest")
