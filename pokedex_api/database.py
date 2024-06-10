import logging
import sqlite3
import httpx
import xml.etree.ElementTree as ET
from fastapi.responses import FileResponse
from typing import Union, Optional, Dict, Any
from fastapi import HTTPException

POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon"
DATABASE = "pokemon.db"


def create_database(database: str = DATABASE):
    logging.info("Creating database...")
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS pokemon
                    (id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    type TEXT,
                    power TEXT,
                    image TEXT NOT NULL);"""
    )
    conn.commit()
    conn.close()
    logging.info("General database created successfully.")


async def fetch_and_save_pokemon_data(url: str = POKEAPI_URL, database: str = DATABASE):
    async with httpx.AsyncClient() as client:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        try:
            while url:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                pokemon_data = data["results"]

                batch_data = []
                for pokemon in pokemon_data:
                    url_details = pokemon["url"]
                    response_details = await client.get(url_details)
                    response_details.raise_for_status()
                    pokemon_details = response_details.json()

                    name = pokemon_details["name"]
                    types = [
                        entry["type"]["name"] for entry in pokemon_details["types"]
                    ]
                    image = (
                        pokemon_details["sprites"]["front_default"]
                        or "default_image_url"
                    )

                    batch_data.append(
                        (
                            name,
                            url_details,
                            types[0],
                            types[1] if len(types) > 1 else "",
                            image,
                        )
                    )

                cursor.executemany(
                    "INSERT INTO pokemon (name, url, type, power, image) VALUES (?, ?, ?, ?, ?)",
                    batch_data,
                )
                conn.commit()
                url = data["next"]
        finally:
            conn.close()


async def export_to_xml(
    filename: str = "pokemon.xml", database: str = DATABASE
) -> Union[FileResponse, None]:
    """
    Export Pokémon data to XML file.

    Args:
        filename (str): The name of the XML file to export data to. Defaults to 'pokemon.xml'.
        database (str) : The path of the database where data will be fetched from.

    Returns:
        Union[FileResponse, None]: A FileResponse containing the exported XML file if successful, else None.
    """
    try:
        logging.info("Exporting Pokémon to XML...")
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM pokemon ORDER BY name")
        pokemon_data = cursor.fetchall()

        logging.info(f"Fetched {len(pokemon_data)} Pokémon entries from the database.")

        root = ET.Element("Pokemons")
        for pokemon in pokemon_data:
            pokemon_elem = ET.SubElement(root, "Pokemon")
            ET.SubElement(pokemon_elem, "id").text = str(pokemon[0])
            ET.SubElement(pokemon_elem, "name").text = pokemon[1]
            ET.SubElement(pokemon_elem, "url").text = pokemon[2]

        tree = ET.ElementTree(root)
        tree.write(filename, encoding="utf-8", xml_declaration=True)

        logging.info("Pokémon exported to XML successfully.")
        return FileResponse(
            path=filename, media_type="application/xml", filename=filename
        )

    except sqlite3.Error as e:
        logging.error(f"Error exporting Pokémon data to XML: {e}")
        return None

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None

    finally:
        if conn:
            conn.close()


async def get_pokemon_data(
    start_index: Optional[int] = None,
    page_size: Optional[int] = None,
    details: bool = False,
    database: str = DATABASE,
) -> Dict[str, Any]:
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM pokemon")
        total_count = cursor.fetchone()[0]

        if start_index is None or page_size is None:
            cursor.execute("SELECT * FROM pokemon ORDER BY name")
        else:
            cursor.execute(
                "SELECT * FROM pokemon ORDER BY name LIMIT ? OFFSET ?",
                (page_size, start_index),
            )
        pokemon_data = cursor.fetchall()

        formatted_data = []
        for row in pokemon_data:
            pokemon_dict = {
                "id": row[0],
                "name": row[1],
                "url": row[2],
            }
            if details:
                pokemon_dict.update({"type": row[3], "power": row[4], "image": row[5]})
            formatted_data.append(pokemon_dict)

        pagination = {"paginaAnterior": None, "paginaProxima": None}

        if start_index is not None and page_size is not None:
            if start_index + page_size < total_count:
                pagination["paginaProxima"] = (
                    f"/pokemons?start_index={start_index + page_size}&page_size={page_size}"
                )

            if start_index > 0:
                pagination["paginaAnterior"] = (
                    f"/pokemons?start_index={max(start_index - page_size, 0)}&page_size={page_size}"
                )

        return {"pokemon": formatted_data, "pagination": pagination}

    finally:
        conn.close()
