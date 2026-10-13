"""Genera src/battlelens/data/pokedex.json a partir de los CSV públicos de PokéAPI.

Uso:  uv run python tools/build_dataset.py [--no-cache]
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/"
CSV_FILES = [
    "languages",
    "pokemon_species",
    "pokemon_species_names",
    "pokemon",
    "pokemon_types",
    "pokemon_stats",
    "pokemon_abilities",
    "abilities",
    "ability_names",
    "types",
    "type_names",
    "type_efficacy",
]
LANGUAGES = ["en", "es", "fr", "de", "it"]
STAT_KEYS = {1: "hp", 2: "attack", 3: "defense", 4: "special_attack", 5: "special_defense", 6: "speed"}
MAX_STANDARD_TYPE_ID = 18  # excluye "stellar", "unknown" y "shadow"

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "src" / "battlelens" / "data" / "pokedex.json"
CACHE_DIR = Path(__file__).resolve().parent / ".cache"


class DownloadError(RuntimeError):
    pass


def fetch_csv(name: str, use_cache: bool) -> list[dict[str, str]]:
    cache_file = CACHE_DIR / f"{name}.csv"
    if use_cache and cache_file.exists():
        text = cache_file.read_text(encoding="utf-8")
    else:
        url = f"{BASE_URL}{name}.csv"
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                text = resp.read().decode("utf-8")
        except OSError as exc:
            raise DownloadError(f"No se pudo descargar {url}: {exc}") from exc
        CACHE_DIR.mkdir(exist_ok=True)
        cache_file.write_text(text, encoding="utf-8")
    return list(csv.DictReader(io.StringIO(text)))


def build(tables: dict[str, list[dict[str, str]]]) -> dict:
    lang_by_id = {
        int(r["id"]): r["identifier"] for r in tables["languages"] if r["identifier"] in LANGUAGES
    }

    def localized(rows, key_field: str) -> dict[int, dict[str, str]]:
        out: dict[int, dict[str, str]] = {}
        for r in rows:
            lang = lang_by_id.get(int(r["local_language_id"]))
            if lang and r["name"]:
                out.setdefault(int(r[key_field]), {})[lang] = r["name"]
        return out

    # Tipos
    type_ident = {
        int(r["id"]): r["identifier"]
        for r in tables["types"]
        if int(r["id"]) <= MAX_STANDARD_TYPE_ID
    }
    type_names = localized(tables["type_names"], "type_id")
    types = {ident: {"id": tid, "names": type_names.get(tid, {})} for tid, ident in type_ident.items()}

    efficacy: dict[str, dict[str, float]] = {ident: {} for ident in type_ident.values()}
    for r in tables["type_efficacy"]:
        atk, dfn = int(r["damage_type_id"]), int(r["target_type_id"])
        if atk in type_ident and dfn in type_ident:
            efficacy[type_ident[atk]][type_ident[dfn]] = int(r["damage_factor"]) / 100

    # Habilidades
    ability_ident = {int(r["id"]): r["identifier"] for r in tables["abilities"]}
    ability_names = localized(tables["ability_names"], "ability_id")

    # Forma por defecto de cada especie
    default_pokemon = {
        int(r["species_id"]): int(r["id"]) for r in tables["pokemon"] if r["is_default"] == "1"
    }
    poke_types: dict[int, list[tuple[int, str]]] = {}
    for r in tables["pokemon_types"]:
        tid = int(r["type_id"])
        if tid in type_ident:
            poke_types.setdefault(int(r["pokemon_id"]), []).append((int(r["slot"]), type_ident[tid]))
    poke_stats: dict[int, dict[str, int]] = {}
    for r in tables["pokemon_stats"]:
        sid = int(r["stat_id"])
        if sid in STAT_KEYS:
            poke_stats.setdefault(int(r["pokemon_id"]), {})[STAT_KEYS[sid]] = int(r["base_stat"])
    poke_abilities: dict[int, list[tuple[int, dict]]] = {}
    for r in tables["pokemon_abilities"]:
        aid = int(r["ability_id"])
        poke_abilities.setdefault(int(r["pokemon_id"]), []).append(
            (
                int(r["slot"]),
                {
                    "identifier": ability_ident.get(aid, str(aid)),
                    "names": ability_names.get(aid, {}),
                    "hidden": r["is_hidden"] == "1",
                },
            )
        )

    species_names = localized(tables["pokemon_species_names"], "pokemon_species_id")
    species = []
    for r in sorted(tables["pokemon_species"], key=lambda r: int(r["id"])):
        sid = int(r["id"])
        pid = default_pokemon.get(sid)
        if pid is None:
            continue
        stats = poke_stats.get(pid, {})
        if len(stats) != len(STAT_KEYS):
            raise ValueError(f"Estadísticas incompletas para la especie {sid}")
        species.append(
            {
                "id": sid,
                "identifier": r["identifier"],
                "generation": int(r["generation_id"]),
                "names": species_names.get(sid, {}),
                "types": [t for _, t in sorted(poke_types.get(pid, []))],
                "stats": stats,
                "abilities": [a for _, a in sorted(poke_abilities.get(pid, []), key=lambda x: x[0])],
            }
        )

    return {
        "source": BASE_URL,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "languages": LANGUAGES,
        "types": types,
        "type_efficacy": efficacy,
        "species": species,
    }


def write_atomic(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".pokedex-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-cache", action="store_true", help="ignora los CSV descargados previamente")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)

    try:
        tables = {name: fetch_csv(name, use_cache=not args.no_cache) for name in CSV_FILES}
        data = build(tables)
    except (DownloadError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    write_atomic(data, args.output)
    print(f"{len(data['species'])} especies y {len(data['types'])} tipos -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
