from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse
from .database import get_pokemon_data, export_to_xml
from .models import PokemonListResponse, PokemonDetailsResponse

router = APIRouter()


@router.get("/", tags=["root"])
async def root():
    return RedirectResponse(url="/docs")


@router.get(
    "/pokemons",
    response_model=PokemonListResponse,
    summary="List Pokémon",
    description="Returns a list of Pokémon with pagination, ordered alphabetically by name.",
)
async def get_pokemon_route(
    start_index: int = Query(None, alias="start_index"),
    page_size: int = Query(None, alias="page_size"),
):
    """
    Retrieves a list of Pokémon with pagination.

    Args:
        start_index (int): The index to start retrieving Pokémon from.
        page_size (int): The number of Pokémon per page.

    Returns:
        dict: A dictionary containing a list of Pokémon, even if empty, and pagination information.
    """
    pokemon_data = await get_pokemon_data(
        start_index=start_index, page_size=page_size, details=False
    )
    return pokemon_data


@router.get(
    "/export",
    summary="Export Pokémon List to XML",
    description="Exports the sorted list of Pokémon to an XML file.",
)
async def export_pokemon_to_xml():
    """
    Exports the sorted list of Pokémon to an XML file.

    Returns:
        FileResponse: The XML file containing the Pokémon data.
    """
    return await export_to_xml()


@router.get(
    "/data",
    response_model=PokemonDetailsResponse,
    summary="Get Pokémon Data",
    description="Returns a list of Pokémon data with pagination, ordered alphabetically by name.",
)
async def get_pokemon_data_route(
    start_index: int = Query(None, alias="start_index"),
    page_size: int = Query(None, alias="page_size"),
):
    """
    Retrieves Pokémon data from the database with pagination.

    Args:
        start_index (int): The index to start retrieving Pokémon from.
        page_size (int): The number of Pokémon per page.

    Returns:
        dict: A dictionary containing a list of Pokémon details and pagination information.
    """
    pokemon_data = await get_pokemon_data(
        start_index=start_index, page_size=page_size, details=True
    )
    return pokemon_data
