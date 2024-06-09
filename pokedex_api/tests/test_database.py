import os
import sqlite3
import pytest
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock
from starlette.responses import FileResponse
from pokedex_api.database import (
    create_database,
    fetch_and_save_pokemon_data,
    export_to_xml,
    get_pokemon_data,
)


DATABASE_TEST = "test_pokemon.db"
XML_FILE_TEST = "test_pokemon.xml"


MOCK_POKEMON_LIST_RESPONSE = {
    "results": [
        {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"},
    ],
    "next": "https://pokeapi.co/api/v2/pokemon/?offset=20&limit=20",
}

MOCK_POKEMON_DETAILS_RESPONSE = {
    "name": "bulbasaur",
    "types": [{"type": {"name": "grass"}}, {"type": {"name": "poison"}}],
    "sprites": {"front_default": "https://pokeapi.co/media/sprites/pokemon/1.png"},
}

MOCK_NEXT_POKEMON_LIST_RESPONSE = {
    "results": [
        {"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/"},
    ],
    "next": None,
}

MOCK_NEXT_POKEMON_DETAILS_RESPONSE = {
    "name": "ivysaur",
    "types": [{"type": {"name": "grass"}}, {"type": {"name": "poison"}}],
    "sprites": {"front_default": "https://pokeapi.co/media/sprites/pokemon/2.png"},
}


@pytest.fixture(scope="function")
def temporary_database():
    yield DATABASE_TEST
    if os.path.exists(DATABASE_TEST):
        os.remove(DATABASE_TEST)


def test_create_database():
    create_database(DATABASE_TEST)

    assert os.path.exists(DATABASE_TEST)

    with sqlite3.connect(DATABASE_TEST) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='pokemon'"
        )
        table_exists = cursor.fetchone() is not None
        assert table_exists


@pytest.mark.asyncio
async def test_fetch_and_save_pokemon_data(mocker, temporary_database):
    mock_get = mocker.patch("httpx.AsyncClient.get")

    mock_response_list = MagicMock()
    mock_response_list.json.return_value = MOCK_POKEMON_LIST_RESPONSE
    mock_response_list.raise_for_status = MagicMock()

    mock_response_details = MagicMock()
    mock_response_details.json.return_value = MOCK_POKEMON_DETAILS_RESPONSE
    mock_response_details.raise_for_status = MagicMock()

    mock_next_response_list = MagicMock()
    mock_next_response_list.json.return_value = MOCK_NEXT_POKEMON_LIST_RESPONSE
    mock_next_response_list.raise_for_status = MagicMock()

    mock_next_response_details = MagicMock()
    mock_next_response_details.json.return_value = MOCK_NEXT_POKEMON_DETAILS_RESPONSE
    mock_next_response_details.raise_for_status = MagicMock()

    mock_get.side_effect = [
        mock_response_list,
        mock_response_details,
        mock_next_response_list,
        mock_next_response_details,
    ]

    create_database(DATABASE_TEST)

    await fetch_and_save_pokemon_data(database=temporary_database)

    with sqlite3.connect(temporary_database) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pokemon")
        results = cursor.fetchall()

        assert len(results) == 2
        assert results[0][1] == "bulbasaur"
        assert results[0][2] == "https://pokeapi.co/api/v2/pokemon/1/"
        assert results[0][3] == "grass"
        assert results[0][4] == "poison"
        assert results[0][5] == "https://pokeapi.co/media/sprites/pokemon/1.png"
        assert results[1][1] == "ivysaur"
        assert results[1][2] == "https://pokeapi.co/api/v2/pokemon/2/"
        assert results[1][3] == "grass"
        assert results[1][4] == "poison"
        assert results[1][5] == "https://pokeapi.co/media/sprites/pokemon/2.png"


@pytest.mark.asyncio
async def test_export_to_xml(temporary_database):
    create_temporary_database(DATABASE_TEST)

    conn = sqlite3.connect(DATABASE_TEST)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pokemon")
    pokemon_entries = cursor.fetchall()
    print(pokemon_entries)
    conn.close()

    response = await export_to_xml(filename=XML_FILE_TEST, database=DATABASE_TEST)

    assert isinstance(response, FileResponse)
    assert os.path.exists(XML_FILE_TEST)

    tree = ET.parse(XML_FILE_TEST)
    root = tree.getroot()
    xml_string = ET.tostring(root)
    print(xml_string)
    assert root.tag == "Pokemons"

    pokemons = root.findall("Pokemon")
    assert len(pokemons) == 2

    pokemon_elem = pokemons[0]
    assert pokemon_elem.find("id").text == "1"
    assert pokemon_elem.find("name").text == "bulbasaur"
    assert pokemon_elem.find("url").text == "https://pokeapi.co/api/v2/pokemon/1/"


def create_temporary_database(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS pokemon (id INTEGER PRIMARY KEY, name TEXT, url TEXT, type TEXT, power TEXT, image TEXT)"
    )
    cursor.execute(
        "INSERT INTO pokemon (id, name, url, type, power, image) VALUES (1, 'bulbasaur', 'https://pokeapi.co/api/v2/pokemon/1/', 'grass', 'poison', 'https://pokeapi.co/media/sprites/pokemon/1.png')"
    )
    cursor.execute(
        "INSERT INTO pokemon (id, name, url, type, power, image) VALUES (2, 'ivysaur', 'https://pokeapi.co/api/v2/pokemon/2/', 'grass', 'poison', 'https://pokeapi.co/media/sprites/pokemon/2.png')"
    )
    conn.commit()
    conn.close()


@pytest.mark.asyncio
async def test_get_pokemon_data(temporary_database):
    create_temporary_database(temporary_database)

    data = await get_pokemon_data(
        start_index=0, page_size=1, details=False, database=temporary_database
    )
    assert data["pagination"]["paginaAnterior"] is None
    assert data["pagination"]["paginaProxima"] == "/pokemon?start_index=1&page_size=1"
    assert len(data["pokemon"]) == 1
    assert data["pokemon"][0]["name"] == "bulbasaur"
    assert "type" not in data["pokemon"][0]

    data = await get_pokemon_data(
        start_index=0, page_size=2, details=True, database=temporary_database
    )
    assert data["pagination"]["paginaAnterior"] is None
    assert data["pagination"]["paginaProxima"] is None
    assert len(data["pokemon"]) == 2
    assert data["pokemon"][0]["name"] == "bulbasaur"
    assert data["pokemon"][0]["type"] == "grass"
    assert data["pokemon"][0]["power"] == "poison"
    assert (
        data["pokemon"][0]["image"] == "https://pokeapi.co/media/sprites/pokemon/1.png"
    )
    assert data["pokemon"][1]["name"] == "ivysaur"
    assert data["pokemon"][1]["type"] == "grass"
    assert data["pokemon"][1]["power"] == "poison"
    assert (
        data["pokemon"][1]["image"] == "https://pokeapi.co/media/sprites/pokemon/2.png"
    )

    data = await get_pokemon_data(
        start_index=1, page_size=1, details=True, database=temporary_database
    )
    assert data["pagination"]["paginaAnterior"] == "/pokemon?start_index=0&page_size=1"
    assert data["pagination"]["paginaProxima"] is None
    assert len(data["pokemon"]) == 1
    assert data["pokemon"][0]["name"] == "ivysaur"
    assert data["pokemon"][0]["type"] == "grass"
    assert data["pokemon"][0]["power"] == "poison"
    assert (
        data["pokemon"][0]["image"] == "https://pokeapi.co/media/sprites/pokemon/2.png"
    )
