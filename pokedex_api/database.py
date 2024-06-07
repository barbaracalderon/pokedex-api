import logging
import sqlite3
import httpx
import xml.etree.ElementTree as ET
from fastapi.responses import FileResponse
from typing import Union

POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon"

def check_database_exists():
    try:
        conn = sqlite3.connect('pokemon.db')
        conn.close()
        return True
    except sqlite3.Error:
        return False

async def fetch_and_save_pokemon_data(url=POKEAPI_URL):
    async with httpx.AsyncClient() as client:
        conn = sqlite3.connect('pokemon.db')
        cursor = conn.cursor()
        
        try:
            while url:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                pokemon_data = data["results"]
                
                batch_data = []
                for pokemon in pokemon_data:
                    url_details = pokemon['url']
                    response_details = await client.get(url_details)
                    response_details.raise_for_status()
                    pokemon_details = response_details.json()

                    name = pokemon_details['name']
                    types = [entry['type']['name'] for entry in pokemon_details['types']]
                    image = pokemon_details['sprites']['front_default'] or 'default_image_url'  # Provide a default image URL if none is available

                    batch_data.append((name, url_details, types[0], types[1] if len(types) > 1 else '', image))

                cursor.executemany('INSERT INTO pokemon (name, url, type, power, image) VALUES (?, ?, ?, ?, ?)', batch_data)
                conn.commit()
                url = data["next"]
        finally:
            conn.close()

def create_database():
    logging.info("Creating database...")
    conn = sqlite3.connect('pokemon.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS pokemon
                    (id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    type TEXT,
                    power TEXT,
                    image TEXT NOT NULL);''')
    conn.commit()
    conn.close()
    logging.info("General database created successfully.")

async def export_to_xml(filename='pokemon.xml') -> Union[FileResponse, None]:
    logging.info("Exporting Pokémon to XML...")
    conn = sqlite3.connect('pokemon.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pokemon ORDER BY name')
    pokemon_data = cursor.fetchall()
    conn.close()

    root = ET.Element("Pokemons")
    for pokemon in pokemon_data:
        pokemon_elem = ET.SubElement(root, "Pokemon")
        ET.SubElement(pokemon_elem, "id").text = str(pokemon[0])
        ET.SubElement(pokemon_elem, "name").text = pokemon[1]
        ET.SubElement(pokemon_elem, "url").text = pokemon[2]

    tree = ET.ElementTree(root)
    tree.write(filename, encoding='utf-8', xml_declaration=True)

    logging.info("Pokémon exported to XML successfully.")
    return FileResponse(path=filename, media_type='application/xml', filename=filename)
