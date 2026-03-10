import logging
import asyncpg
from asyncpg.exceptions import InterfaceError

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
            logger.info("PostgreSQL connection pool created (ms-rulebook)")
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL connection pool: {e}")
            raise
    return _pool


async def execute_query(query: str, *args):
    """Execute a query that returns results."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(query, *args)
    except Exception as e:
        logger.error(f"Database query error: {e}")
        raise


async def execute_insert(query: str, *args) -> int:
    """Execute an insert query and return the inserted ID."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchval(query, *args)
            return result
    except Exception as e:
        logger.error(f"Database insert error: {e}")
        raise


async def execute_update(query: str, *args) -> int:
    """Execute an update query and return the number of affected rows."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute(query, *args)
            return int(result.split()[-1]) if result else 0
    except Exception as e:
        logger.error(f"Database update error: {e}")
        raise


def serialize_rule(row) -> dict | None:
    """Convert PostgreSQL row to JSON-serializable dict."""
    if row is None:
        return None

    return {
        "id": str(row["id"]),
        "sensor_source": row["sensor_source"],
        "sensor_metric": row["sensor_metric"],
        "operator": row["operator"],
        "threshold_value": float(row["threshold_value"]),
        "target_actuator": row["target_actuator"],
        "target_state": row["target_state"],
        "enabled": row["enabled"],
        "description": row["description"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
    }


async def create_rule(data: dict) -> dict:
    """Create a new rule in the database."""
    try:
        query = """
            INSERT INTO mars.rules (
                sensor_source,
                sensor_metric,
                operator,
                threshold_value,
                target_actuator,
                target_state,
                enabled,
                description
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id, sensor_source, sensor_metric, operator, threshold_value, target_actuator, target_state, enabled, description, created_at, updated_at
        """
        rows = await execute_query(
            query,
            data.get("sensor_source"),
            data.get("sensor_metric"),
            data.get("operator"),
            data.get("threshold_value"),
            data.get("target_actuator"),
            data.get("target_state"),
            data.get("enabled", True),
            data.get("description"),
        )
        return serialize_rule(rows[0]) if rows else None
    except InterfaceError as e:
        logger.error(f"Integrity error creating rule: {e}")
        raise ValueError(f"Invalid rule data: {e}")
    except Exception as e:
        logger.error(f"Error creating rule: {e}")
        raise


async def list_rules() -> list[dict]:
    """List all rules from the database."""
    try:
        query = """
            SELECT id, sensor_source, sensor_metric, operator, threshold_value, target_actuator, target_state, enabled, description, created_at, updated_at
            FROM mars.rules
            ORDER BY created_at DESC
        """
        rows = await execute_query(query)
        return [serialize_rule(row) for row in rows]
    except Exception as e:
        logger.error(f"Error listing rules: {e}")
        raise


async def get_rule(rule_id: str) -> dict | None:
    """Get a single rule by ID."""
    try:
        query = """
            SELECT id, sensor_source, sensor_metric, operator, threshold_value, target_actuator, target_state, enabled, description, created_at, updated_at
            FROM mars.rules
            WHERE id = $1
        """
        rows = await execute_query(query, int(rule_id))
        return serialize_rule(rows[0]) if rows else None
    except (ValueError, IndexError) as e:
        logger.error(f"Error getting rule {rule_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error getting rule {rule_id}: {e}")
        raise


async def update_rule(rule_id: str, data: dict) -> dict | None:
    """Update a rule (full replacement)."""
    try:
        query = """
            UPDATE mars.rules
            SET sensor_source = $2,
                sensor_metric = $3,
                operator = $4,
                threshold_value = $5,
                target_actuator = $6,
                target_state = $7,
                enabled = $8,
                description = $9,
                updated_at = NOW()
            WHERE id = $1
            RETURNING id, sensor_source, sensor_metric, operator, threshold_value, target_actuator, target_state, enabled, description, created_at, updated_at
        """
        rows = await execute_query(
            query,
            int(rule_id),
            data.get("sensor_source"),
            data.get("sensor_metric"),
            data.get("operator"),
            data.get("threshold_value"),
            data.get("target_actuator"),
            data.get("target_state"),
            data.get("enabled", True),
            data.get("description"),
        )
        return serialize_rule(rows[0]) if rows else None
    except ValueError as e:
        logger.error(f"Invalid rule ID {rule_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error updating rule {rule_id}: {e}")
        raise


async def delete_rule(rule_id: str) -> bool:
    """Delete a rule by ID."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute("DELETE FROM mars.rules WHERE id = $1", int(rule_id))
            return result == "DELETE 1"
    except Exception as e:
        logger.error(f"Error deleting rule {rule_id}: {e}")
        raise
