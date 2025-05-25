from typing import List, Optional, Dict

from sqlalchemy import select, insert

from app.database.connection import database
from app.database.models import potential_hubs_table

async def add_potential_hub(hub_data: Dict) -> int:
    """
    Adds a potential hub to the database.

    Args:
        hub_data: A dictionary containing the hub data. Expected keys should match
                  the columns in potential_hubs_table (e.g., 'iata_code', 'name',
                  'city', 'country', 'latitude', 'longitude', 'is_active').

    Returns:
        The ID of the newly inserted hub.
    """
    # Ensure required fields are present if necessary, or handle potential KeyError
    # Example: if 'iata_code' not in hub_data: raise ValueError("Missing iata_code")

    insert_query = insert(potential_hubs_table).values(hub_data)
    last_record_id = await database.execute(insert_query)
    return last_record_id

async def get_active_china_hubs() -> List[Dict]:
    """
    Retrieves a list of active potential hubs located in China.

    Returns:
        A list of dictionaries, where each dictionary represents an active hub in China.
        Returns an empty list if no such hubs are found.
    """
    select_query = select(potential_hubs_table).where(
        potential_hubs_table.c.is_active == True,
        # Use the new country_code column for precise matching
        potential_hubs_table.c.country_code == 'CN'
    )
    results = await database.fetch_all(select_query)
    # Convert RowProxy objects to dictionaries
    return [dict(result) for result in results]

async def get_all_hubs() -> List[Dict]:
    """
    Retrieves all potential hubs from the database.

    Returns:
        A list of dictionaries, where each dictionary represents a hub.
    """
    select_query = select(potential_hubs_table)
    results = await database.fetch_all(select_query)
    return [dict(result) for result in results]

# You might want other functions like:
# async def get_hub_by_iata(iata_code: str) -> Optional[Dict]:
# async def update_hub_status(iata_code: str, is_active: bool):