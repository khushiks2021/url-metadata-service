import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings


logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect() -> None:
    """Establish connection to MongoDB and create indexes."""
    global _client, _db

    _client = AsyncIOMotorClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=5000,
    )
    _db = _client[settings.mongodb_db_name]

    await _db.metadata.create_index("url", unique=True)
    logger.info("Connected to MongoDB and ensured indexes.")


async def disconnect() -> None:
    """Close the MongoDB connection."""
    global _client, _db

    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("Disconnected from MongoDB.")


def get_collection():
    """Return the metadata collection. Raises if not connected."""
    if _db is None:
        raise RuntimeError("Database not connected. Call connect() first.")
    return _db.metadata


async def find_by_url(url: str) -> dict[str, Any] | None:
    """Look up a metadata record by URL."""
    return await get_collection().find_one(
        {"url": url},
        {"_id": 0},
    )


async def upsert_record(record: dict[str, Any]) -> None:
    """Insert or replace a metadata record keyed by URL."""
    await get_collection().replace_one(
        {"url": record["url"]},
        record,
        upsert=True,
    )