import datetime
from typing import Optional, List, Dict

from sqlalchemy import select, insert, update, text

from app.database.connection import database
from app.database.models import locations_table, airports_table # Assuming airports_table exists if needed

# TODO: Define cache expiry duration (e.g., in hours or seconds)
CACHE_EXPIRY_HOURS = 6 # Example: Cache results for 6 hours

async def get_cached_location(query: str, trip_type: str, mode: str) -> Optional[Dict]:
    """
    Retrieves cached location data from the database.

    Args:
        query: The search query (e.g., city name, airport code).
        trip_type: Type of trip (e.g., 'flight', 'hotel').
        mode: Search mode (e.g., 'dep', 'arr', 'city').

    Returns:
        A dictionary containing the cached result if found and not expired, otherwise None.
    """
    select_query = select(locations_table).where(
        locations_table.c.query == query,
        locations_table.c.trip_type == trip_type,
        locations_table.c.mode == mode
    ).order_by(locations_table.c.updated_at.desc()).limit(1) # Get the latest entry

    result = await database.fetch_one(select_query)

    if result:
        # Check cache expiry
        now = datetime.datetime.now(datetime.timezone.utc)
        # Ensure updated_at is timezone-aware for comparison
        updated_at_aware = result['updated_at'].replace(tzinfo=datetime.timezone.utc)
        if now - updated_at_aware < datetime.timedelta(hours=CACHE_EXPIRY_HOURS):
            # Convert RowProxy to dict before returning
            return dict(result)
        else:
            # Cache expired
            return None
    return None

async def save_location_result(query: str, trip_type: str, mode: str, raw_json_response_str: str):
    """
    Saves or updates location search results (raw JSON response) in the database.

    Args:
        query: The search query.
        trip_type: Type of trip.
        mode: Search mode.
        raw_json_response_str: The raw JSON response string from the API.
    """
    # Check if a record already exists
    select_query = select(locations_table.c.id).where(
        locations_table.c.query == query,
        locations_table.c.trip_type == trip_type,
        locations_table.c.mode == mode
    )
    existing_id = await database.fetch_val(select_query)

    values = {
        "query": query,
        "trip_type": trip_type,
        "mode": mode,
        "raw_data": raw_json_response_str, # Store the raw JSON string
        "updated_at": datetime.datetime.now(datetime.timezone.utc)
    }

    if existing_id:
        # Update existing record
        update_query = update(locations_table).where(locations_table.c.id == existing_id).values(values)
        await database.execute(update_query)
    else:
        # Insert new record
        insert_query = insert(locations_table).values(values)
        await database.execute(insert_query)

# --- Optional Airport Specific CRUD ---
# Uncomment and implement if a separate, structured airport table is used.

# async def get_cached_airport(iata_code: str) -> Optional[Dict]:
#     """
#     Retrieves cached airport data from the airports_table.
#     """
#     # Implement query similar to get_cached_location but for airports_table
#     # Consider cache expiry based on 'updated_at'
#     query = select(airports_table).where(airports_table.c.iata_code == iata_code)
#     result = await database.fetch_one(query)
#     # Add expiry check if needed
#     return dict(result) if result else None

# async def save_airport_result(airport_data: Dict):
#     """
#     Saves or updates airport data in the airports_table.
#     Expects airport_data to contain 'iata_code' and other relevant fields.
#     """
#     # Implement insert/update logic similar to save_location_result
#     # Use ON CONFLICT DO UPDATE or check existence first if needed
#     iata_code = airport_data.get("iata_code")
#     if not iata_code:
#         # Handle error: IATA code is required
#         return

#     values = {**airport_data, "updated_at": datetime.datetime.now(datetime.timezone.utc)}

#     # Example using PostgreSQL's ON CONFLICT (requires asyncpg dialect)
#     # Or check existence first for SQLite/MySQL
#     # insert_stmt = insert(airports_table).values(values)
#     # on_conflict_stmt = insert_stmt.on_conflict_do_update(
#     #     index_elements=['iata_code'], # Assuming unique constraint on iata_code
#     #     set_=values
#     # )
#     # await database.execute(on_conflict_stmt)

#     # Basic Insert/Update for SQLite:
#     existing = await get_cached_airport(iata_code)
#     if existing:
#         update_query = update(airports_table).where(airports_table.c.iata_code == iata_code).values(values)
#         await database.execute(update_query)
#     else:
#         insert_query = insert(airports_table).values(values)
#         await database.execute(insert_query)