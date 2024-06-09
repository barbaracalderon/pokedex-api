import os
import sqlite3
import pytest
from pokedex_api.database import create_database

DATABASE_TEST = "test_pokemon.db"

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
