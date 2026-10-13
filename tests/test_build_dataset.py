import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("build_dataset", ROOT / "tools" / "build_dataset.py")
build_dataset = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_dataset)


def test_descarga_fallida_no_sobrescribe(tmp_path, monkeypatch):
    output = tmp_path / "pokedex.json"
    output.write_text('{"previo": true}', encoding="utf-8")

    def falla(name, use_cache):
        raise build_dataset.DownloadError("sin red")

    monkeypatch.setattr(build_dataset, "fetch_csv", falla)
    code = build_dataset.main(["--no-cache", "--output", str(output)])

    assert code != 0
    assert output.read_text(encoding="utf-8") == '{"previo": true}'


def _rows(header: str, *lines: str) -> list[dict[str, str]]:
    import csv
    import io

    return list(csv.DictReader(io.StringIO("\n".join([header, *lines]))))


def _mini_tables():
    stats = [f"{pid},{sid},50,0" for pid in (263, 10174) for sid in range(1, 7)]
    return {
        "languages": _rows("id,iso639,iso3166,identifier,official,order", "7,es,es,es,1,10", "9,en,us,en,1,7"),
        "pokemon_species": _rows("id,identifier,generation_id", "263,zigzagoon,3"),
        "pokemon_species_names": _rows("pokemon_species_id,local_language_id,name,genus", "263,7,Zigzagoon,", "263,9,Zigzagoon,"),
        "pokemon": _rows("id,identifier,species_id,is_default", "263,zigzagoon,263,1", "10174,zigzagoon-galar,263,0"),
        "pokemon_types": _rows("pokemon_id,type_id,slot", "263,1,1", "10174,17,1", "10174,1,2"),
        "pokemon_types_past": _rows("pokemon_id,generation_id,type_id,slot", "263,2,2,1"),
        "pokemon_stats": _rows("pokemon_id,stat_id,base_stat,effort", *stats),
        "pokemon_abilities": _rows("pokemon_id,ability_id,is_hidden,slot", "263,53,0,1", "10174,53,0,1"),
        "abilities": _rows("id,identifier", "53,pickup"),
        "ability_names": _rows("ability_id,local_language_id,name", "53,7,Recogida", "53,9,Pickup"),
        "types": _rows("id,identifier,generation_id", "1,normal,1", "2,fighting,1", "17,dark,2", "10001,unknown,2"),
        "type_names": _rows("type_id,local_language_id,name", "1,7,Normal", "2,7,Lucha", "17,7,Siniestro"),
        "type_efficacy": _rows("damage_type_id,target_type_id,damage_factor", "2,1,200", "2,17,200", "1,1,100"),
        "type_efficacy_past": _rows("damage_type_id,target_type_id,damage_factor,generation_id", "2,17,100,1"),
        "pokemon_forms": _rows(
            "id,identifier,form_identifier,pokemon_id,introduced_in_version_group_id,is_default,is_battle_only,is_mega,form_order,order",
            "263,zigzagoon,,263,5,1,0,0,1,1",
            "10333,zigzagoon-galar,galar,10174,20,1,0,0,2,2",
        ),
        "pokemon_form_names": _rows(
            "pokemon_form_id,local_language_id,form_name,pokemon_name",
            "10333,7,Forma de Galar,",
            "10333,9,Galarian Form,Galarian Zigzagoon",
        ),
        "versions": _rows("id,version_group_id,identifier", "33,20,sword", "34,20,shield", "35,21,the-isle-of-armor-sword"),
        "version_names": _rows("version_id,local_language_id,name", "33,7,Espada", "34,7,Escudo", "33,9,Sword"),
        "version_groups": _rows("id,identifier,generation_id,order", "20,sword-shield,8,22", "21,the-isle-of-armor,8,23"),
        "pokemon_evolution": [],
        "evolution_triggers": [],
        "items": [],
        "item_names": [],
        "ability_flavor_text": [],
    }


def test_build_con_formas_juegos_y_datos_anteriores():
    data = build_dataset.build(_mini_tables())
    assert data["format"] == 2
    assert data["type_generation"] == {"normal": 1, "fighting": 1, "dark": 2}
    assert data["type_efficacy_past"] == [
        {"attacker": "fighting", "defender": "dark", "factor": 1.0, "until_generation": 1}
    ]
    assert [g["id"] for g in data["games"]] == ["sword-shield"]  # la DLC no es un juego aparte
    game = data["games"][0]
    assert game["regional_form"] == "galar" and game["names"]["es"] == "Espada / Escudo"
    zig = data["species"][0]
    assert zig["past_types"] == [{"until_generation": 2, "types": ["fighting"]}]
    (form,) = zig["forms"]
    assert form["form"] == "galar" and form["types"] == ["dark", "normal"]
    assert form["names"] == {"es": "Zigzagoon de Galar", "en": "Galarian Zigzagoon"}


def test_build_con_habilidades_anteriores():
    tables = _mini_tables()
    tables["pokemon_abilities_past"] = _rows(
        "pokemon_id,generation_id,ability_id,is_hidden,slot", "263,6,26,0,1", "263,4,,1,3"
    )
    tables["abilities"] = _rows("id,identifier", "53,pickup", "26,levitate")
    zig = build_dataset.build(tables)["species"][0]
    assert zig["abilities"][0]["slot"] == 1
    assert zig["past_abilities"] == [
        {"until_generation": 4, "slot": 3, "ability": None},
        {"until_generation": 6, "slot": 1,
         "ability": {"identifier": "levitate", "names": {}, "hidden": False, "slot": 1}},
    ]


def test_build_con_evoluciones_y_descripciones():
    tables = _mini_tables()
    tables["pokemon_species"] = _rows(
        "id,identifier,generation_id,evolves_from_species_id,capture_rate", "263,zigzagoon,3,,255"
    )
    tables["pokemon_evolution"] = _rows(
        "id,evolved_species_id,evolution_trigger_id,version_group_id,is_default,trigger_item_id,minimum_level,"
        "gender_id,location_id,held_item_id,time_of_day,known_move_id,known_move_type_id,minimum_happiness",
        "1,263,3,5,1,82,,,,,,,,",
    )
    tables["evolution_triggers"] = _rows("id,identifier", "3,use-item")
    tables["items"] = _rows("id,identifier", "82,fire-stone")
    tables["item_names"] = _rows("item_id,local_language_id,name", "82,7,Piedra Fuego")
    tables["ability_flavor_text"] = _rows(
        "ability_id,version_group_id,language_id,flavor_text",
        '53,5,7,"Texto viejo"',
        '53,20,7,"Puede recoger\nobjetos\ntras el combate."',
    )
    data = build_dataset.build(tables)
    zig = data["species"][0]
    assert zig["capture_rate"] == 255
    assert zig["evolution"]["trigger"] == "use-item" and zig["evolution"]["item"] == "fire-stone"
    assert data["items"] == {"fire-stone": {"es": "Piedra Fuego"}}
    assert data["ability_descriptions"]["pickup"]["es"] == "Puede recoger objetos tras el combate."
