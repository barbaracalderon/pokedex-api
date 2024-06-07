from pydantic import BaseModel
from typing import Optional, List

class Pagination(BaseModel):
    paginaAnterior: Optional[str]
    paginaProxima: Optional[str]


class PokemonBase(BaseModel):
    id: int
    name: str
    url: str

class Pokemon(PokemonBase):
    type: Optional[str]
    power: Optional[str]
    image: Optional[str]

class PokemonListResponse(BaseModel):
    pokemon: List[PokemonBase]
    pagination: Pagination

class PokemonDetailsResponse(BaseModel):
    pokemon: List[Pokemon]
    pagination: Pagination
