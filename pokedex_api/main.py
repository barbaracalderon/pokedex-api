from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router as api_router
from .database import create_database, fetch_and_save_pokemon_data
import os


app = FastAPI(
    title="Pokédex API",
    description="API for managing a Pokédex, listing all captured Pokémon with pagination.",
    version="1.0.0",
)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    if os.path.exists("pokemon.db") is False:
        create_database()
        await fetch_and_save_pokemon_data()
