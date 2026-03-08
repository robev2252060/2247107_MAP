import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None


def get_db() -> AsyncIOMotorDatabase:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri)
        logger.info("MongoDB client created (processing-service)")
    return _client[settings.mongodb_db]


async def fetch_rules(sensor_id: str) -> list[dict]:
    """Fetch all active rules matching the given sensor_id."""
    db = get_db()
    cursor = db["rules"].find({"sensor_id": sensor_id, "enabled": {"$ne": False}})
    return await cursor.to_list(length=None)
