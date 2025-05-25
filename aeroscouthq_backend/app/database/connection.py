import databases
import sqlalchemy
from sqlalchemy import create_engine, MetaData
from app.core.config import settings

# Database URL from settings
DATABASE_URL = settings.DATABASE_URL

# Asynchronous database connection using 'databases' library
# force_rollback=True is useful for testing to keep the database clean
database = databases.Database(DATABASE_URL, force_rollback=settings.TESTING)

# SQLAlchemy MetaData object to hold table definitions
metadata = MetaData()

# Synchronous SQLAlchemy engine
# Required for Alembic migrations and potentially for synchronous operations
# or tools that don't support async drivers directly.
# We replace 'sqlite+aiosqlite' with 'sqlite' for compatibility with create_engine
# and add connect_args for SQLite thread safety in web frameworks.
sync_engine_url = settings.DATABASE_URL
if sync_engine_url.startswith("sqlite+aiosqlite"):
    sync_engine_url = sync_engine_url.replace("+aiosqlite", "")

engine = create_engine(
    sync_engine_url,
    connect_args={"check_same_thread": False} # Necessary for SQLite with multiple threads/requests
)

# Placeholder functions for establishing and closing the async database connection
# These will typically be called during application startup and shutdown.
async def connect_db():
    """Establishes the asynchronous database connection."""
    try:
        await database.connect()
        print("Database connection established.")

        # 确保locations表存在
        await ensure_locations_table_exists()
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        # Depending on the application's needs, you might want to raise the exception
        # or handle it differently (e.g., retry logic).

async def ensure_locations_table_exists():
    """确保locations表存在，如果不存在则创建它"""
    try:
        # 检查locations表是否存在
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name='locations'"
        result = await database.fetch_val(query)

        if not result:
            print("locations表不存在，正在创建...")
            # 创建locations表
            create_table_query = """
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                trip_type TEXT,
                mode TEXT,
                raw_data TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
            await database.execute(create_table_query)

            # 创建索引
            create_index_query = "CREATE INDEX IF NOT EXISTS idx_locations_query ON locations (query)"
            await database.execute(create_index_query)

            print("locations表和索引创建成功")
        else:
            print("locations表已存在")
    except Exception as e:
        print(f"确保locations表存在时出错: {e}")

async def disconnect_db():
    """Closes the asynchronous database connection."""
    try:
        await database.disconnect()
        print("Database connection closed.")
    except Exception as e:
        print(f"Error disconnecting from the database: {e}")

# Optional: Function to create all tables defined in the metadata
# Useful for initial setup or testing environments, but migrations (Alembic)
# are preferred for production environments.
# def create_all_tables():
#     """Creates all tables defined in the metadata using the synchronous engine."""
#     print("Attempting to create all tables...")
#     try:
#         metadata.create_all(bind=engine)
#         print("Tables created successfully (if they didn't exist).")
#     except Exception as e:
#         print(f"Error creating tables: {e}")

# Example usage (usually not needed here, called from main.py or tests)
# if __name__ == "__main__":
#     # Example of creating tables directly (use with caution)
#     # create_all_tables()
#
#     # Example of running async connection/disconnection (requires asyncio runner)
#     import asyncio
#     async def main():
#         await connect_db()
#         # Perform some database operations if needed
#         await disconnect_db()
#     # asyncio.run(main())