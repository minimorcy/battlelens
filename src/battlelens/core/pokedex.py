"""Dataset local de especies, formas regionales, juegos y cálculo de eficacia de tipos."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from importlib import resources
from pathlib import Path

from .abilities import AbilityEffect, affects_typing, resolve

STAT_ORDER = ("hp", "attack", "defense", "special_attack", "special_defense", "speed")
# Orden en la ficha; «special» solo existe en la Gen 1 (add-generation-stats D3)
STAT_DISPLAY_ORDER = ("hp", "attack", "defense", "special", "special_attack", "special_defense", "speed")
SPECIAL_SPLIT_GENERATION = 2
# Juegos con Megaevolución y regresión primigenia (add-alternate-forms D2)
MEGA_GAMES = frozenset({
    "x-y", "omega-ruby-alpha-sapphire", "sun-moon", "ultra-sun-ultra-moon", "lets-go-pikachu-lets-go-eevee",
    "legends-za", "mega-dimension", "champions",
})
MULTIPLIER_GROUPS = (4.0, 2.0, 0.5, 0.25, 0.0)
CURRENT_GENERATION = 9
ABILITIES_FROM_GENERATION = 3
HIDDEN_ABILITIES_FROM_GENERATION = 5


class DatasetMissingError(RuntimeError):
    def __init__(self, path: Path | str) -> None:
        super().__init__(
            f"No se encuentra el dataset ({path}). Genéralo con: uv run python tools/build_dataset.py"
        )


def _localized(names: dict[str, str], lang: str, fallback: str) -> str:
    return names.get(lang) or names.get("en") or fallback


@dataclass(frozen=True)
class Ability:
    identifier: str
    names: dict[str, str]
    hidden: bool
    descriptions: dict[str, str] = field(default_factory=dict, compare=False)
    slot: int = field(default=0, compare=False)  # 1, 2 o 3 (oculta)

    def name(self, lang: str) -> str:
        return _localized(self.names, lang, self.identifier)

    def description(self, lang: str) -> str:
        return _localized(self.descriptions, lang, "")


# Etiquetas de las condiciones de evolución (add-richer-species-info D4); otros idiomas usan "en"
_EVOLUTION_LABELS = {
    "es": {"level": "Nv. {n}", "trade": "Intercambio", "trade_item": "Intercambio con {item}",
           "friendship": "Amistad", "day": "de día", "night": "de noche", "special": "Especial"},
    "en": {"level": "Lv. {n}", "trade": "Trade", "trade_item": "Trade holding {item}",
           "friendship": "Friendship", "day": "by day", "night": "at night", "special": "Special"},
}


def capture_difficulty(rate: int | None) -> str | None:
    """Clasificación del ratio de captura (spec pokemon-data, «Dificultad de captura»)."""
    if rate is None:
        return None
    if rate >= 190:
        return "Fácil"
    if rate >= 75:
        return "Media"
    if rate >= 25:
        return "Difícil"
    return "Muy difícil"


@dataclass(frozen=True)
class PastAbility:
    """Habilidad de un hueco vigente hasta una generación; None = hueco vacío (add-ability-aware-matchups D2)."""

    until_generation: int
    slot: int
    ability: Ability | None


def abilities_in(
    abilities: tuple[Ability, ...], past: tuple[PastAbility, ...], generation: int
) -> tuple[Ability, ...]:
    """Habilidades vigentes en una generación: cada hueco toma la entrada pasada más cercana que la cubra."""
    by_slot: dict[int, Ability | None] = {a.slot: a for a in abilities}
    chosen: dict[int, int] = {}
    for p in past:
        if p.until_generation >= generation and (p.slot not in chosen or p.until_generation < chosen[p.slot]):
            chosen[p.slot] = p.until_generation
            by_slot[p.slot] = p.ability
    return tuple(a for _, a in sorted(by_slot.items()) if a is not None)


@dataclass(frozen=True)
class PastStats:
    until_generation: int
    stats: dict[str, int]


def stats_in(stats: dict[str, int], past: tuple[PastStats, ...], generation: int) -> dict[str, int]:
    """Estadísticas base vigentes en una generación; en la Gen 1, «special» sustituye a At. Esp. y Def. Esp."""
    result = dict(stats)
    chosen: dict[str, int] = {}
    for p in past:
        if p.until_generation < generation:
            continue
        for key, value in p.stats.items():
            if key not in chosen or p.until_generation < chosen[key]:
                chosen[key] = p.until_generation
                result[key] = value
    if generation < SPECIAL_SPLIT_GENERATION:
        special = result.get("special", result.get("special_attack"))
        result.pop("special_attack", None)
        result.pop("special_defense", None)
        if special is not None:
            result["special"] = special
    else:
        result.pop("special", None)
    return result


@dataclass(frozen=True)
class Evolution:
    trigger: str
    min_level: int | None = None
    item: str | None = None
    held_item: str | None = None
    min_happiness: int | None = None
    time_of_day: str | None = None


@dataclass(frozen=True)
class Form:
    identifier: str
    form: str  # p. ej. "galar", "paldea-combat-breed"
    names: dict[str, str]
    types: tuple[str, ...]
    stats: dict[str, int]
    abilities: tuple[Ability, ...]
    pokemon: str | None = None  # identificador del Pokémon en PokéAPI (p. ej. "zigzagoon-galar")
    weight_kg: float | None = None
    height_m: float | None = None
    ev_yield: dict[str, int] = field(default_factory=dict, compare=False)
    past_abilities: tuple[PastAbility, ...] = field(default=(), compare=False)
    past_stats: tuple[PastStats, ...] = field(default=(), compare=False)
    kind: str = "regional"  # "regional", "mega" o "alternate" (add-alternate-forms D1)
    introduced: str | None = None  # juego (grupo de versiones) en que apareció

    def name(self, lang: str) -> str:
        return _localized(self.names, lang, self.identifier)

    def abilities_in(self, generation: int) -> tuple[Ability, ...]:
        return abilities_in(self.abilities, self.past_abilities, generation)

    def stats_in(self, generation: int) -> dict[str, int]:
        return stats_in(self.stats, self.past_stats, generation)


@dataclass(frozen=True)
class PastTypes:
    until_generation: int
    types: tuple[str, ...]


@dataclass(frozen=True)
class Species:
    id: int
    identifier: str
    generation: int
    names: dict[str, str]
    types: tuple[str, ...]
    stats: dict[str, int]
    abilities: tuple[Ability, ...]
    past_types: tuple[PastTypes, ...] = ()
    forms: tuple[Form, ...] = ()
    capture_rate: int | None = None
    evolves_from: int | None = None
    evolution: Evolution | None = None
    pokemon: str | None = None  # identificador del Pokémon en PokéAPI (p. ej. "zigzagoon-galar")
    weight_kg: float | None = None
    height_m: float | None = None
    ev_yield: dict[str, int] = field(default_factory=dict, compare=False)
    past_abilities: tuple[PastAbility, ...] = field(default=(), compare=False)
    past_stats: tuple[PastStats, ...] = field(default=(), compare=False)

    def name(self, lang: str) -> str:
        return _localized(self.names, lang, self.identifier)

    @property
    def stat_total(self) -> int:
        return sum(self.stats.values())

    def abilities_in(self, generation: int) -> tuple[Ability, ...]:
        return abilities_in(self.abilities, self.past_abilities, generation)

    def stats_in(self, generation: int) -> dict[str, int]:
        return stats_in(self.stats, self.past_stats, generation)

    def types_in(self, generation: int) -> tuple[str, ...]:
        """Tipos de la forma por defecto vigentes en una generación (design.md D3)."""
        applicable = [p for p in self.past_types if p.until_generation >= generation]
        return min(applicable, key=lambda p: p.until_generation).types if applicable else self.types


@dataclass(frozen=True)
class Game:
    id: str
    generation: int
    regional_form: str | None
    names: dict[str, str]
    version_names: tuple[dict[str, str], ...]
    order: int = 0  # orden del grupo de versiones en PokéAPI

    def name(self, lang: str) -> str:
        return _localized(self.names, lang, self.id)


@dataclass(frozen=True)
class OtherForm:
    name: str
    types: tuple[str, ...]


@dataclass(frozen=True)
class SpeciesView:
    """Lo que la ficha muestra de una especie en un juego concreto."""

    species_id: int
    name: str
    form: str | None
    types: tuple[str, ...]
    stats: dict[str, int]
    abilities: tuple[Ability, ...]
    generation: int
    matchups: dict[float, list[str]]
    other_forms: tuple[OtherForm, ...] = field(default_factory=tuple)
    capture_rate: int | None = None
    capture_difficulty: str | None = None
    # Etapas de la cadena evolutiva: cada etapa, una tupla de (nombre, condición o None)
    evolution: tuple[tuple[tuple[str, str | None], ...], ...] = field(default_factory=tuple)
    game_id: str | None = None
    pokemon: str | None = None
    weight_kg: float | None = None
    ev_yield: dict[str, int] = field(default_factory=dict)
    # Efectos defensivos de sus habilidades, seguros y posibles (add-ability-aware-matchups D3)
    ability_effects: tuple[AbilityEffect, ...] = field(default_factory=tuple)
    form_id: str | None = None  # identificador de la forma mostrada (el de la especie si es la base)
    base_pokemon: str | None = None  # Pokémon de la especie, para los movimientos de las megas

    def effects_against(self, attacking: str) -> tuple[AbilityEffect, ...]:
        return tuple(e for e in self.ability_effects if e.type == attacking)

    @property
    def stat_keys(self) -> tuple[str, ...]:
        return tuple(k for k in STAT_DISPLAY_ORDER if k in self.stats)

    @property
    def stat_total(self) -> int:
        return sum(self.stats.values())


def _ability(a: dict, descriptions: dict[str, dict[str, str]], default_slot: int) -> Ability:
    slot = a.get("slot") or (3 if a["hidden"] else default_slot)
    return Ability(a["identifier"], a["names"], a["hidden"], descriptions.get(a["identifier"], {}), slot)


def _abilities(raw: list[dict], descriptions: dict[str, dict[str, str]] | None = None) -> tuple[Ability, ...]:
    descriptions = descriptions or {}
    return tuple(_ability(a, descriptions, i + 1) for i, a in enumerate(raw))


def _past_stats(raw: list[dict]) -> tuple[PastStats, ...]:
    return tuple(PastStats(p["until_generation"], p["stats"]) for p in raw)


def _past_abilities(raw: list[dict], descriptions: dict[str, dict[str, str]]) -> tuple[PastAbility, ...]:
    return tuple(
        PastAbility(p["until_generation"], p["slot"],
                    _ability(p["ability"], descriptions, p["slot"]) if p.get("ability") else None)
        for p in raw
    )


class Pokedex:
    def __init__(self, data: dict) -> None:
        self.languages: list[str] = data["languages"]
        self.type_names: dict[str, dict[str, str]] = {k: v["names"] for k, v in data["types"].items()}
        self.type_efficacy: dict[str, dict[str, float]] = data["type_efficacy"]
        self.type_generation: dict[str, int] = data.get("type_generation", {})
        self._efficacy_past: list[dict] = data.get("type_efficacy_past", [])
        self.games: list[Game] = [
            Game(
                g["id"],
                g["generation"],
                g.get("regional_form"),
                g.get("names", {}),
                tuple(v.get("names", {}) for v in g.get("versions", [])),
                g.get("order", 0),
            )
            for g in data.get("games", [])
        ]
        self._games_by_id = {g.id: g for g in self.games}
        self.item_names: dict[str, dict[str, str]] = data.get("items", {})
        descriptions = data.get("ability_descriptions", {})
        self._species: dict[int, Species] = {}
        self._children: dict[int, list[int]] = {}
        for s in data["species"]:
            evo = s.get("evolution")
            self._species[s["id"]] = Species(
                id=s["id"],
                identifier=s["identifier"],
                generation=s["generation"],
                names=s["names"],
                types=tuple(s["types"]),
                stats=s["stats"],
                abilities=_abilities(s["abilities"], descriptions),
                past_types=tuple(PastTypes(p["until_generation"], tuple(p["types"])) for p in s.get("past_types", [])),
                forms=tuple(
                    Form(
                        f["identifier"], f["form"], f["names"], tuple(f["types"]), f["stats"],
                        _abilities(f["abilities"], descriptions),
                        pokemon=f.get("pokemon") or f["identifier"],
                        weight_kg=f.get("weight_kg"),
                        height_m=f.get("height_m"),
                        ev_yield=f.get("ev_yield", {}),
                        past_abilities=_past_abilities(f.get("past_abilities", []), descriptions),
                        past_stats=_past_stats(f.get("past_stats", [])),
                        kind=f.get("kind", "regional"),
                        introduced=f.get("introduced"),
                    )
                    for f in s.get("forms", [])
                ),
                capture_rate=s.get("capture_rate"),
                evolves_from=s.get("evolves_from"),
                evolution=Evolution(**evo) if evo else None,
                pokemon=s.get("pokemon"),
                weight_kg=s.get("weight_kg"),
                height_m=s.get("height_m"),
                ev_yield=s.get("ev_yield", {}),
                past_abilities=_past_abilities(s.get("past_abilities", []), descriptions),
                past_stats=_past_stats(s.get("past_stats", [])),
            )
            if s.get("evolves_from"):
                self._children.setdefault(s["evolves_from"], []).append(s["id"])
        self._charts: dict[int, dict[str, dict[str, float]]] = {}

    @classmethod
    def load(cls, path: Path | None = None) -> Pokedex:
        if path is None:
            resource = resources.files("battlelens") / "data" / "pokedex.json"
            if not resource.is_file():
                raise DatasetMissingError(resource)
            return cls(json.loads(resource.read_text(encoding="utf-8")))
        if not path.is_file():
            raise DatasetMissingError(path)
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def __len__(self) -> int:
        return len(self._species)

    def __iter__(self):
        return iter(self._species.values())

    def get_species(self, species_id: int) -> Species:
        return self._species[species_id]

    def get_game(self, game_id: str | None) -> Game | None:
        return self._games_by_id.get(game_id) if game_id else None

    def type_name(self, type_id: str, lang: str) -> str:
        return _localized(self.type_names.get(type_id, {}), lang, type_id)

    # ---- tablas de tipos ---------------------------------------------------

    def type_chart(self, generation: int = CURRENT_GENERATION) -> dict[str, dict[str, float]]:
        """Tabla atacante → defensor → multiplicador vigente en una generación (design.md D3)."""
        if generation not in self._charts:
            existing = [t for t in self.type_efficacy if self.type_generation.get(t, 1) <= generation]
            chart = {a: {d: self.type_efficacy[a].get(d, 1.0) for d in existing} for a in existing}
            overrides: dict[tuple[str, str], tuple[int, float]] = {}
            for row in self._efficacy_past:
                key = (row["attacker"], row["defender"])
                if row["until_generation"] >= generation and key[0] in chart and key[1] in chart:
                    current = overrides.get(key)
                    if current is None or row["until_generation"] < current[0]:
                        overrides[key] = (row["until_generation"], row["factor"])
            for (a, d), (_, factor) in overrides.items():
                chart[a][d] = factor
            self._charts[generation] = chart
        return self._charts[generation]

    def damage_multipliers(
        self, defending_types: tuple[str, ...] | list[str], generation: int = CURRENT_GENERATION
    ) -> dict[str, float]:
        """Multiplicador de daño recibido por cada tipo de ataque existente en la generación."""
        result = {}
        for attacking, row in self.type_chart(generation).items():
            factor = 1.0
            for t in defending_types:
                factor *= row.get(t, 1.0)
            result[attacking] = factor
        return result

    def defensive_matchups(
        self,
        defending_types: tuple[str, ...] | list[str],
        generation: int = CURRENT_GENERATION,
        abilities: tuple[Ability, ...] = (),
    ) -> dict[float, list[str]]:
        """Agrupa los tipos de ataque en ×4, ×2, ×½, ×¼ y ×0 (se omite ×1), con los efectos seguros
        de las habilidades que dan un multiplicador de los grupos (add-ability-aware-matchups D3)."""
        groups: dict[float, list[str]] = {m: [] for m in MULTIPLIER_GROUPS}
        for attacking, base in self.damage_multipliers(defending_types, generation).items():
            factor, _ = resolve(abilities, attacking, base)
            if factor not in groups and factor != 1.0:
                factor = base
            if factor in groups:
                groups[factor].append(attacking)
        return groups

    def ability_effects(
        self, defending_types: tuple[str, ...], abilities: tuple[Ability, ...], generation: int = CURRENT_GENERATION
    ) -> tuple[AbilityEffect, ...]:
        """Efectos seguros y posibles de las habilidades sobre cada tipo de ataque de la generación."""
        if not any(affects_typing(a.identifier) for a in abilities):
            return ()
        effects: list[AbilityEffect] = []
        for attacking, base in self.damage_multipliers(defending_types, generation).items():
            effects.extend(resolve(abilities, attacking, base)[1])
        return tuple(effects)

    # ---- evolución ----------------------------------------------------------

    def evolution_condition(self, evolution: Evolution | None, lang: str) -> str | None:
        if evolution is None:
            return None
        labels = _EVOLUTION_LABELS.get(lang, _EVOLUTION_LABELS["en"])

        def item(identifier: str) -> str:
            return _localized(self.item_names.get(identifier, {}), lang, identifier)

        if evolution.trigger == "use-item" and evolution.item:
            return item(evolution.item)
        if evolution.trigger == "trade":
            return labels["trade_item"].format(item=item(evolution.held_item)) if evolution.held_item else labels["trade"]
        if evolution.trigger == "level-up":
            if evolution.min_level:
                text = labels["level"].format(n=evolution.min_level)
            elif evolution.min_happiness:
                text = labels["friendship"]
            else:
                return labels["special"]
            if evolution.time_of_day in ("day", "night"):
                text += f" {labels[evolution.time_of_day]}"
            return text
        return labels["special"]

    def evolution_stages(
        self, species_id: int, generation: int = CURRENT_GENERATION, lang: str = "es"
    ) -> tuple[tuple[tuple[str, str | None], ...], ...]:
        """Cadena completa desde la especie base, en etapas, sin especies posteriores al juego (D3)."""
        root = self.get_species(species_id)
        while root.evolves_from and root.evolves_from in self._species:
            parent = self._species[root.evolves_from]
            if parent.generation > generation:
                break
            root = parent
        stages: list[tuple[tuple[str, str | None], ...]] = []
        level = [root]
        first = True
        while level:
            stages.append(tuple(
                (sp.name(lang), None if first else self.evolution_condition(sp.evolution, lang)) for sp in level
            ))
            first = False
            level = [
                self._species[c]
                for sp in level
                for c in self._children.get(sp.id, [])
                if self._species[c].generation <= generation
            ]
        return tuple(stages)

    # ---- vista según el juego ----------------------------------------------

    def form_available(self, form: Form, game: Game | None) -> bool:
        """Forma disponible en un juego (add-alternate-forms D2); las regionales siempre lo están."""
        if form.kind == "regional" or game is None:
            return True
        if form.kind == "mega" and game.id not in MEGA_GAMES:
            return False
        introduced = self.get_game(form.introduced)
        return introduced is None or introduced.order <= game.order

    def _auto_form(self, species: Species, game: Game | None) -> Form | None:
        if game and game.regional_form:
            return next(
                (f for f in species.forms if f.kind == "regional" and f.form.startswith(game.regional_form)), None
            )
        return None

    def form_cycle(self, species_id: int, game_id: str | None = None) -> tuple[str, ...]:
        """Forma mostrada sin elegir seguida de las demás disponibles en el juego (add-alternate-forms D3)."""
        species = self.get_species(species_id)
        game = self.get_game(game_id)
        auto = self._auto_form(species, game)
        cycle = [auto.identifier if auto else species.identifier]
        for identifier in [species.identifier] + [
            f.identifier for f in species.forms if self.form_available(f, game)
        ]:
            if identifier not in cycle:
                cycle.append(identifier)
        return tuple(cycle)

    def view(
        self, species_id: int, game_id: str | None = None, lang: str = "es", form: str | None = None
    ) -> SpeciesView:
        """Forma, tipos, habilidades y eficacias de una especie en un juego (design.md D1-D3).

        `form` elige una forma por su identificador (el de la especie es la forma base); si no está
        disponible en el juego, se usa la forma automática (regional o base).
        """
        species = self.get_species(species_id)
        game = self.get_game(game_id)
        generation = game.generation if game else CURRENT_GENERATION

        chosen = None
        if form is not None and form in self.form_cycle(species_id, game_id):
            chosen = species if form == species.identifier else next(f for f in species.forms if f.identifier == form)
        if chosen is None:
            chosen = self._auto_form(species, game)
        form = chosen if isinstance(chosen, Form) else None

        source = form if form is not None else species
        if form is not None:
            name, types, stats = form.name(lang), form.types, form.stats_in(generation)
            abilities = form.abilities_in(generation)
        else:
            name, types, stats = species.name(lang), species.types_in(generation), species.stats_in(generation)
            abilities = species.abilities_in(generation)

        if generation < ABILITIES_FROM_GENERATION:
            abilities = ()
        elif generation < HIDDEN_ABILITIES_FROM_GENERATION:
            abilities = tuple(a for a in abilities if not a.hidden)

        others: list[OtherForm] = []
        if form is not None:
            others.append(OtherForm(species.name(lang), species.types_in(generation)))
        others += [
            OtherForm(f.name(lang), f.types)
            for f in species.forms
            if f is not form and self.form_available(f, game)
        ]

        return SpeciesView(
            species_id=species.id,
            name=name,
            form=form.form if form else None,
            types=types,
            stats=stats,
            abilities=abilities,
            generation=generation,
            matchups=self.defensive_matchups(types, generation, abilities),
            other_forms=tuple(others),
            capture_rate=species.capture_rate,
            capture_difficulty=capture_difficulty(species.capture_rate),
            evolution=self.evolution_stages(species.id, generation, lang),
            game_id=game.id if game else None,
            pokemon=source.pokemon,
            weight_kg=source.weight_kg,
            ev_yield=source.ev_yield,
            ability_effects=self.ability_effects(types, abilities, generation),
            form_id=form.identifier if form else species.identifier,
            base_pokemon=species.pokemon,
        )
