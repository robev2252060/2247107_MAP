import logging
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from app.config import settings

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None

COLLECTION_RULES = "rules"


def get_db() -> AsyncIOMotorDatabase:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri)
        logger.info("MongoDB client created (rule-service)")
    return _client[settings.mongodb_db]


def get_rules_collection() -> AsyncIOMotorCollection:
    return get_db()[COLLECTION_RULES]


def serialize_rule(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict."""
    doc["_id"] = str(doc["_id"])
    return doc


async def create_rule(data: dict) -> dict:
    col = get_rules_collection()
    result = await col.insert_one(data)
    created = await col.find_one({"_id": result.inserted_id})
    return serialize_rule(created)


async def list_rules() -> list[dict]:
    col = get_rules_collection()
    cursor = col.find({})
    docs = await cursor.to_list(length=None)
    return [serialize_rule(d) for d in docs]


async def get_rule(rule_id: str) -> dict | None:
    col = get_rules_collection()
    doc = await col.find_one({"_id": ObjectId(rule_id)})
    return serialize_rule(doc) if doc else None


async def update_rule(rule_id: str, data: dict) -> dict | None:
    col = get_rules_collection()
    await col.update_one({"_id": ObjectId(rule_id)}, {"$set": data})
    return await get_rule(rule_id)


async def delete_rule(rule_id: str) -> bool:
    col = get_rules_collection()
    result = await col.delete_one({"_id": ObjectId(rule_id)})
    return result.deleted_count == 1
