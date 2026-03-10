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
            logger.info("PostgreSQL connection pool created (ms-automation)")
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL connection pool: {e}")
            raise
    return _pool


async def fetch_rules_for_source(sensor_source: str) -> list[dict]:
    """Fetch all active rules matching the given sensor_source."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, sensor_source, sensor_metric, operator, threshold_value, target_actuator, target_state, enabled, description
                FROM mars.rules
                WHERE sensor_source = $1 AND enabled = TRUE
                ORDER BY created_at DESC
                """,
                sensor_source
            )
        
        # Convert rows to dictionaries
        rules = []
        for row in rows:
            rules.append({
                "id": row["id"],
                "sensor_source": row["sensor_source"],
                "sensor_metric": row["sensor_metric"],
                "operator": row["operator"],
                "threshold_value": float(row["threshold_value"]),
                "target_actuator": row["target_actuator"],
                "target_state": row["target_state"],
                "enabled": row["enabled"],
                "description": row["description"],
            })
        
        logger.debug(f"Fetched {len(rules)} active rules for source {sensor_source}")
        return rules
    except Exception as e:
        logger.error(f"Error fetching rules for source {sensor_source}: {e}")
        return []  # Return empty list on error to allow processing to continue
