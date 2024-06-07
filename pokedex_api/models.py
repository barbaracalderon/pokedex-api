from pydantic import BaseModel
from typing import List

class Pagination(BaseModel):
    paginaAnterior: str
    paginaProxima: str

class Pokemon(BaseModel):
    id: int
    name: str
    url: str

class DetailedPokemon(Pokemon):
    type: str
    power: str
    image: str

class PokemonResponse(BaseModel):
    pokemon: List[Pokemon]
    pagination: Pagination

class DetailedPokemonResponse(BaseModel):
    pokemon: List[DetailedPokemon]
    pagination: Pagination