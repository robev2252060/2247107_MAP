import logging
import asyncpg

from app.config import settings

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Get or create the PostgreSQL connection pool."""
    global _pool
    if _pool is None:
        try:
            _pool = await asyncpg.create_pool(
                dsn=settings.database_url,
                min_size=5,
                max_size=20,
            )
            logger.info("PostgreSQL connection pool created (processing-service)")
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL connection pool: {e}")
            raise
    return _pool


async def fetch_rules(sensor_id: str) -> list[dict]:
    """Fetch all active rules matching the given sensor_id."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, sensor_id, operator, threshold, unit, actuator_id, actuator_state, enabled, description, created_at, updated_at
                FROM mars.rules
                WHERE sensor_id = $1 AND enabled = TRUE
                ORDER BY created_at DESC
                """,
                sensor_id
            )
        
        # Convert rows to dictionaries
        rules = []
        for row in rows:
            rules.append({
                "id": row["id"],
                "_id": row["id"],  # Keep _id for compatibility with rule_engine
                "sensor_id": row["sensor_id"],
                "operator": row["operator"],
                "threshold": row["threshold"],
                "unit": row["unit"],
                "actuator_id": row["actuator_id"],
                "actuator_state": row["actuator_state"],
                "enabled": row["enabled"],
                "description": row["description"],
            })
        
        logger.debug(f"Fetched {len(rules)} active rules for sensor {sensor_id}")
        return rules
    except Exception as e:
        logger.error(f"Error fetching rules for sensor {sensor_id}: {e}")
        return []  # Return empty list on error to allow processing to continue
