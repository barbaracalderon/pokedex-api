from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from database import (
    check_database_exists,
    create_database,
    fetch_and_save_pokemon_data,
    export_to_xml,
)
import sqlite3

app = FastAPI(
    title="Pokédex API",
    description="API para gerenciar uma Pokédex, listando todos os Pokémon capturados com paginação.",
    version="1.0.0",
)


class Pokemon(BaseModel):
    id: int
    name: str
    url: str


@app.on_event("startup")
async def startup_event():
    if not check_database_exists():
        create_database()
        await fetch_and_save_pokemon_data()


@app.get(
    "/pokemon",
    response_model=dict,
    summary="Listar Pokémon",
    description="Retorna uma lista de Pokémon com paginação, ordenados alfabeticamente pelo nome.",
)
async def get_pokemon(
    offset: int = Query(None, alias="offset"), limit: int = Query(None, alias="limit")
):
    conn = sqlite3.connect("pokemon.db")
    cursor = conn.cursor()

    if offset is None or limit is None:
        cursor.execute("SELECT * FROM pokemon ORDER BY name")
    else:
        cursor.execute(
            "SELECT * FROM pokemon ORDER BY name LIMIT ? OFFSET ?", (limit, offset)
        )
    pokemon_data = cursor.fetchall()

    formatted_data = [
        {"id_api": row[0], "name": row[1], "url": row[2]} for row in pokemon_data
    ]

    conn.close()

    if not formatted_data:
        raise HTTPException(status_code=404, detail="No Pokémon found")

    pagination = {}
    if offset is not None and limit is not None:
        if offset > 0:
            pagination["paginaAnterior"] = (
                f"/pokemon?offset={max(offset - limit, 0)}&limit={limit}"
            )
        else:
            pagination["paginaAnterior"] = None

        if len(formatted_data) == limit:
            pagination["paginaProxima"] = (
                f"/pokemon?offset={offset + limit}&limit={limit}"
            )
        else:
            pagination["paginaProxima"] = None

    return {"pokemon": formatted_data, "pagination": pagination}


@app.get(
    "/export",
    summary="Exportar lista de Pokémon para XML",
    description="Exporta a lista de Pokémon ordenada para um arquivo XML.",
)
async def export_pokemon_to_xml():
    return await export_to_xml()


@app.get("/data", summary="Get Pokemon Details", description="Retrieve and display Pokemon details from the database.")
async def get_pokemon_data():
    try:
        conn = sqlite3.connect('pokemon.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM pokemon')

        rows = cursor.fetchall()

        formatted_data = [{'id_api': row[0], 'name': row[1], "type": row[3], "power": row[4], "image": row[5]} for row in rows]

        conn.close()

        return formatted_data

    except sqlite3.Error as e:
        return {"error": str(e)}
