import os
import sqlite3
import pytest
from ..routes import router as api_router
from ..main import app
from ..database import create_database, get_pokemon_data, export_to_xml
from fastapi import FastAPI, Query
from fastapi.testclient import TestClient

app.include_router(api_router)

client = TestClient(app)


@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client


def test_export_pokemon_to_xml(test_client):
    response = test_client.get("/export")
    assert response.status_code == 200


def test_get_pokemon_route(test_client):
    response = test_client.get("/pokemons?start_index=0&page_size=1")
    assert response.status_code == 200
    assert response.json()["pagination"]["paginaAnterior"] is None
    assert (
        response.json()["pagination"]["paginaProxima"]
        == "/pokemons?start_index=1&page_size=1"
    )
    assert len(response.json()["pokemon"]) == 1
    assert response.json()["pokemon"][0]["name"] == "abomasnow"
    assert response.json()["pokemon"][0]["id"] == 460
    assert (
        response.json()["pokemon"][0]["url"] == "https://pokeapi.co/api/v2/pokemon/460/"
    )


def test_get_pokemon_data_route(test_client):
    response = test_client.get("/data?start_index=0&page_size=1")
    assert response.status_code == 200
    assert response.json()["pagination"]["paginaAnterior"] is None
    assert (
        response.json()["pagination"]["paginaProxima"]
        == "/pokemons?start_index=1&page_size=1"
    )
    assert len(response.json()["pokemon"]) == 1
    assert response.json()["pokemon"][0]["name"] == "abomasnow"
    assert response.json()["pokemon"][0]["id"] == 460
    assert (
        response.json()["pokemon"][0]["url"] == "https://pokeapi.co/api/v2/pokemon/460/"
    )
