"""MongoDB database connection using Motor (async driver)."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

# Global client instance
_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


def get_client() -> AsyncIOMotorClient:
    """Get or create the MongoDB client."""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri)
    return _client


def get_database() -> AsyncIOMotorDatabase:
    """Get the database from the MongoDB connection URI.

    The database name is extracted from the URI, consistent with the SvelteKit app.
    """
    global _database
    if _database is None:
        client = get_client()
        # Use 'humanbenchmark' as the database name (same as SvelteKit)
        _database = client["humanbenchmark"]
    return _database


async def close_database():
    """Close the MongoDB connection."""
    global _client, _database
    if _client:
        _client.close()
        _client = None
        _database = None


async def ensure_indexes():
    """Ensure required database indexes exist.

    This helps prevent sort memory limit errors and improves query performance.
    """
    db = get_database()
    collection = db["gamesessions"]

    # Index for sorting user sessions by lastUpdated (descending)
    # This is critical for the /adventure/user/{user_id}/sessions endpoint
    await collection.create_index(
        [("userId", 1), ("gameType", 1), ("lastUpdated", -1)],
        name="user_sessions_sort_index",
        background=True
    )

    print("✅ Database indexes created successfully")
