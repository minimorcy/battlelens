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
    "type_efficacy_past",
    "pokemon_types_past",
    "pokemon_forms",
    "pokemon_form_names",
    "versions",
    "version_names",
    "version_groups",
    "pokemon_evolution",
    "evolution_triggers",
    "items",
    "item_names",
    "ability_flavor_text",
    "pokemon_moves",
    "moves",
    "move_names",
    "move_damage_classes",
]
LANGUAGES = ["en", "es", "fr", "de", "it"]
STAT_KEYS = {1: "hp", 2: "attack", 3: "defense", 4: "special_attack", 5: "special_defense", 6: "speed"}
MAX_STANDARD_TYPE_ID = 18  # excluye "stellar", "unknown" y "shadow"
DATASET_FORMAT = 2

# Forma regional que predomina en cada juego (design.md D2). Let's Go usa formas de Alola.
REGIONAL_FORM_BY_GAME = {
    "sun-moon": "alola",
    "ultra-sun-ultra-moon": "alola",
    "lets-go-pikachu-lets-go-eevee": "alola",
    "sword-shield": "galar",
    "legends-arceus": "hisui",
    "scarlet-violet": "paldea",
}
# Las DLC se tratan como su juego base; las ediciones japonesas de la Gen 1 se agrupan con Rojo/Azul.
EXCLUDED_GAMES = {
    "the-isle-of-armor", "the-crown-tundra", "the-teal-mask", "the-indigo-disk", "red-green-japan", "blue-japan",
}
REGIONAL_PREFIXES = ("alola", "galar", "hisui", "paldea")
NON_REGIONAL_FORMS = {"alola-cap", "totem-alola"}

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "src" / "battlelens" / "data" / "pokedex.json"
LEARNSETS_OUTPUT = OUTPUT.with_name("learnsets.json")
LEVEL_UP_METHOD = "1"
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

    type_generation = {
        r["identifier"]: int(r["generation_id"]) for r in tables["types"] if int(r["id"]) <= MAX_STANDARD_TYPE_ID
    }
    efficacy_past = [
        {
            "attacker": type_ident[int(r["damage_type_id"])],
            "defender": type_ident[int(r["target_type_id"])],
            "factor": int(r["damage_factor"]) / 100,
            "until_generation": int(r["generation_id"]),
        }
        for r in tables["type_efficacy_past"]
        if int(r["damage_type_id"]) in type_ident and int(r["target_type_id"]) in type_ident
    ]

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
    poke_evs: dict[int, dict[str, int]] = {}
    for r in tables["pokemon_stats"]:
        sid = int(r["stat_id"])
        if sid in STAT_KEYS:
            poke_stats.setdefault(int(r["pokemon_id"]), {})[STAT_KEYS[sid]] = int(r["base_stat"])
            if int(r.get("effort") or 0):
                poke_evs.setdefault(int(r["pokemon_id"]), {})[STAT_KEYS[sid]] = int(r["effort"])
    poke_rows = {int(r["id"]): r for r in tables["pokemon"]}
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

    past_types: dict[int, dict[int, list[tuple[int, str]]]] = {}
    for r in tables["pokemon_types_past"]:
        tid = int(r["type_id"])
        if tid in type_ident:
            past_types.setdefault(int(r["pokemon_id"]), {}).setdefault(int(r["generation_id"]), []).append(
                (int(r["slot"]), type_ident[tid])
            )

    def pokemon_data(pid: int) -> dict:
        stats = poke_stats.get(pid, {})
        if len(stats) != len(STAT_KEYS):
            raise ValueError(f"Estadísticas incompletas para el Pokémon {pid}")
        row = poke_rows.get(pid, {})
        return {
            "pokemon": row.get("identifier"),
            "types": [t for _, t in sorted(poke_types.get(pid, []))],
            "stats": stats,
            "abilities": [a for _, a in sorted(poke_abilities.get(pid, []), key=lambda x: x[0])],
            "weight_kg": int(row["weight"]) / 10 if row.get("weight") else None,
            "height_m": int(row["height"]) / 10 if row.get("height") else None,
            "ev_yield": poke_evs.get(pid, {}),
        }

    # Formas regionales (design.md D2)
    species_of_pokemon = {int(r["id"]): int(r["species_id"]) for r in tables["pokemon"]}
    species_names = localized(tables["pokemon_species_names"], "pokemon_species_id")
    form_pokemon_names: dict[int, dict[str, str]] = {}
    form_labels: dict[int, dict[str, str]] = {}
    for r in tables["pokemon_form_names"]:
        lang = lang_by_id.get(int(r["local_language_id"]))
        if not lang:
            continue
        if r["pokemon_name"]:
            form_pokemon_names.setdefault(int(r["pokemon_form_id"]), {})[lang] = r["pokemon_name"]
        if r["form_name"]:
            form_labels.setdefault(int(r["pokemon_form_id"]), {})[lang] = r["form_name"]

    def form_display_names(form_id: int, sid: int) -> dict[str, str]:
        """Nombre completo de la forma; si PokéAPI no lo trae (p. ej. en español), se construye:
        "Forma de Galar" → "Zigzagoon de Galar"; cualquier otra etiqueta → "Tauros (Raza Combatiente)"."""
        names = dict(form_pokemon_names.get(form_id, {}))
        for lang, label in form_labels.get(form_id, {}).items():
            base = species_names.get(sid, {}).get(lang)
            if lang in names or not base:
                continue
            names[lang] = f"{base} {label[len('Forma '):]}" if label.startswith("Forma ") else f"{base} ({label})"
        return names
    forms_by_species: dict[int, list[tuple[int, dict]]] = {}
    for r in tables["pokemon_forms"]:
        form = r["form_identifier"]
        if not form or form in NON_REGIONAL_FORMS or not form.startswith(REGIONAL_PREFIXES):
            continue
        pid = int(r["pokemon_id"])
        sid = species_of_pokemon.get(pid)
        if sid is None or pid not in poke_stats:
            continue
        forms_by_species.setdefault(sid, []).append(
            (
                int(r["form_order"] or 0),
                {
                    "identifier": r["identifier"],
                    "form": form,
                    "names": form_display_names(int(r["id"]), sid),
                    "form_names": form_labels.get(int(r["id"]), {}),
                    **pokemon_data(pid),
                },
            )
        )

    # Catálogo de juegos (grupos de versiones)
    version_names = localized(tables["version_names"], "version_id")
    versions_by_group: dict[int, list[dict]] = {}
    for r in sorted(tables["versions"], key=lambda r: int(r["id"])):
        versions_by_group.setdefault(int(r["version_group_id"]), []).append(
            {"identifier": r["identifier"], "names": version_names.get(int(r["id"]), {})}
        )
    games = []
    for r in sorted(tables["version_groups"], key=lambda r: int(r["order"])):
        if r["identifier"] in EXCLUDED_GAMES:
            continue
        versions = versions_by_group.get(int(r["id"]), [])
        names = {
            lang: " / ".join(v["names"][lang] for v in versions if lang in v["names"])
            for lang in LANGUAGES
            if any(lang in v["names"] for v in versions)
        }
        games.append(
            {
                "id": r["identifier"],
                "generation": int(r["generation_id"]),
                "regional_form": REGIONAL_FORM_BY_GAME.get(r["identifier"]),
                "names": names,
                "versions": versions,
            }
        )

    # Descripción más reciente de cada habilidad por idioma (add-richer-species-info D1)
    latest_text: dict[tuple[int, str], tuple[int, str]] = {}
    for r in tables["ability_flavor_text"]:
        lang = lang_by_id.get(int(r["language_id"]))
        if not lang:
            continue
        key, vg = (int(r["ability_id"]), lang), int(r["version_group_id"])
        if key not in latest_text or vg > latest_text[key][0]:
            # Algunos textos traen "\n" escrito literalmente y guiones blandos (U+00AD)
            text = r["flavor_text"].replace("\\n", " ").replace("­", "")
            latest_text[key] = (vg, " ".join(text.split()))
    ability_descriptions: dict[str, dict[str, str]] = {}
    for (aid, lang), (_, text) in sorted(latest_text.items()):
        ability_descriptions.setdefault(ability_ident.get(aid, str(aid)), {})[lang] = text

    # Evoluciones: una condición por especie (D2) y nombres de los objetos implicados
    trigger_ident = {int(r["id"]): r["identifier"] for r in tables["evolution_triggers"]}
    item_ident = {int(r["id"]): r["identifier"] for r in tables["items"]}
    evolution_rows: dict[int, dict[str, str]] = {}
    for r in tables["pokemon_evolution"]:
        sid = int(r["evolved_species_id"])
        if sid not in evolution_rows or (r["is_default"] == "1" and evolution_rows[sid]["is_default"] != "1"):
            evolution_rows[sid] = r

    def opt_int(value: str) -> int | None:
        return int(value) if value else None

    used_items: set[int] = set()
    evolutions: dict[int, dict] = {}
    for sid, r in evolution_rows.items():
        item, held = opt_int(r["trigger_item_id"]), opt_int(r["held_item_id"])
        used_items.update(i for i in (item, held) if i is not None)
        evolutions[sid] = {
            "trigger": trigger_ident.get(int(r["evolution_trigger_id"]), "unclassified"),
            "min_level": opt_int(r["minimum_level"]),
            "item": item_ident.get(item) if item else None,
            "held_item": item_ident.get(held) if held else None,
            "min_happiness": opt_int(r["minimum_happiness"]),
            "time_of_day": r["time_of_day"] or None,
        }
    item_names: dict[str, dict[str, str]] = {}
    for r in tables["item_names"]:
        iid = int(r["item_id"])
        lang = lang_by_id.get(int(r["local_language_id"]))
        if iid in used_items and lang and r["name"]:
            item_names.setdefault(item_ident[iid], {})[lang] = r["name"]

    species = []
    for r in sorted(tables["pokemon_species"], key=lambda r: int(r["id"])):
        sid = int(r["id"])
        pid = default_pokemon.get(sid)
        if pid is None:
            continue
        species.append(
            {
                "id": sid,
                "identifier": r["identifier"],
                "generation": int(r["generation_id"]),
                "names": species_names.get(sid, {}),
                **pokemon_data(pid),
                "past_types": [
                    {"until_generation": gen, "types": [t for _, t in sorted(slots)]}
                    for gen, slots in sorted(past_types.get(pid, {}).items())
                ],
                "forms": [f for _, f in sorted(forms_by_species.get(sid, []), key=lambda x: x[0])],
                "capture_rate": opt_int(r.get("capture_rate", "")),
                "evolves_from": opt_int(r.get("evolves_from_species_id", "")),
                "evolution": evolutions.get(sid),
            }
        )

    return {
        "format": DATASET_FORMAT,
        "source": BASE_URL,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "languages": LANGUAGES,
        "types": types,
        "type_generation": type_generation,
        "type_efficacy": efficacy,
        "type_efficacy_past": efficacy_past,
        "games": games,
        "items": item_names,
        "ability_descriptions": ability_descriptions,
        "species": species,
    }


def build_learnsets(tables: dict[str, list[dict[str, str]]]) -> dict:
    """Movimientos por subida de nivel de cada Pokémon y juego, con las listas idénticas deduplicadas
    (add-display-modes D3)."""
    lang_by_id = {
        int(r["id"]): r["identifier"] for r in tables["languages"] if r["identifier"] in LANGUAGES
    }
    type_ident = {int(r["id"]): r["identifier"] for r in tables["types"] if int(r["id"]) <= MAX_STANDARD_TYPE_ID}
    poke_ident = {int(r["id"]): r["identifier"] for r in tables["pokemon"]}
    vg_ident = {int(r["id"]): r["identifier"] for r in tables["version_groups"]}
    class_ident = {int(r["id"]): r["identifier"] for r in tables["move_damage_classes"]}

    raw: dict[str, dict[str, set[tuple[int, int]]]] = {}
    for r in tables["pokemon_moves"]:
        if r["pokemon_move_method_id"] != LEVEL_UP_METHOD:
            continue
        pid, vg = int(r["pokemon_id"]), int(r["version_group_id"])
        if pid not in poke_ident or vg not in vg_ident:
            continue
        raw.setdefault(poke_ident[pid], {}).setdefault(vg_ident[vg], set()).add(
            (int(r["level"] or 0), int(r["move_id"]))
        )

    sets: list[list[list[int]]] = []
    index: dict[tuple, int] = {}
    pokemon: dict[str, dict[str, int]] = {}
    used_moves: set[int] = set()
    for ident, by_vg in sorted(raw.items()):
        for vg, entries in sorted(by_vg.items()):
            key = tuple(sorted(entries))
            if key not in index:
                index[key] = len(sets)
                sets.append([list(e) for e in key])
            pokemon.setdefault(ident, {})[vg] = index[key]
            used_moves.update(m for _, m in key)

    move_names: dict[int, dict[str, str]] = {}
    for r in tables["move_names"]:
        lang = lang_by_id.get(int(r["local_language_id"]))
        if lang and r["name"]:
            move_names.setdefault(int(r["move_id"]), {})[lang] = r["name"]

    def opt_int(value: str) -> int | None:
        return int(value) if value else None

    moves = {}
    for r in tables["moves"]:
        mid = int(r["id"])
        if mid in used_moves:
            moves[str(mid)] = {
                "identifier": r["identifier"],
                "names": move_names.get(mid, {}),
                "type": type_ident.get(int(r["type_id"])) if r["type_id"] else None,
                "class": class_ident.get(int(r["damage_class_id"])) if r["damage_class_id"] else None,
                "power": opt_int(r["power"]),
                "accuracy": opt_int(r["accuracy"]),
                "pp": opt_int(r["pp"]),
                "priority": int(r["priority"] or 0),
            }
    vg_order = {r["identifier"]: (int(r["generation_id"]), int(r["order"])) for r in tables["version_groups"]}
    return {"format": 1, "version_groups": vg_order, "moves": moves, "sets": sets, "pokemon": pokemon}


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
        learnsets = build_learnsets(tables)
    except (DownloadError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    write_atomic(data, args.output)
    write_atomic(learnsets, args.output.with_name("learnsets.json"))
    n_forms = sum(len(sp["forms"]) for sp in data["species"])
    print(f"{len(data['species'])} especies, {n_forms} formas regionales, {len(data['games'])} juegos -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
