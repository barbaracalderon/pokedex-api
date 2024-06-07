from fastapi import FastAPI
from routes import router as api_router
from database import create_database, fetch_and_save_pokemon_data
import os


app = FastAPI(
    title="Pokédex API",
    description="API for managing a Pokédex, listing all captured Pokémon with pagination.",
    version="1.0.0",
)

app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    if os.path.exists('pokemon.db') is False:
        create_database()
        await fetch_and_save_pokemon_data()
