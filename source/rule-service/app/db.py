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
            logger.info("PostgreSQL connection pool created (rule-service)")
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
            # Parse the result string to get affected rows count
            return int(result.split()[-1]) if result else 0
    except Exception as e:
        logger.error(f"Database update error: {e}")
        raise


def serialize_rule(row) -> dict:
    """Convert PostgreSQL row to JSON-serializable dict."""
    if row is None:
        return None
    return {
        "id": row["id"],
        "_id": str(row["id"]),  # MongoDB compatibility
        "sensor_id": row["sensor_id"],
        "operator": row["operator"],
        "threshold": row["threshold"],
        "unit": row["unit"],
        "actuator_id": row["actuator_id"],
        "actuator_state": row["actuator_state"],
        "enabled": row["enabled"],
        "description": row["description"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
    }


async def create_rule(data: dict) -> dict:
    """Create a new rule in the database."""
    try:
        query = """
            INSERT INTO mars.rules (sensor_id, operator, threshold, unit, actuator_id, actuator_state, enabled, description)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id, sensor_id, operator, threshold, unit, actuator_id, actuator_state, enabled, description, created_at, updated_at
        """
        row = await execute_query(
            query,
            data.get("sensor_id"),
            data.get("operator"),
            data.get("threshold"),
            data.get("unit"),
            data.get("actuator_id"),
            data.get("actuator_state"),
            data.get("enabled", True),
            data.get("description"),
        )
        return serialize_rule(row[0]) if row else None
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
            SELECT id, sensor_id, operator, threshold, unit, actuator_id, actuator_state, enabled, description, created_at, updated_at
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
            SELECT id, sensor_id, operator, threshold, unit, actuator_id, actuator_state, enabled, description, created_at, updated_at
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
    """Update a rule and return the updated rule."""
    try:
        # Build dynamic update query
        update_fields = []
        values = []
        param_count = 1
        
        for key, value in data.items():
            if key in ["sensor_id", "operator", "threshold", "unit", "actuator_id", "actuator_state", "enabled", "description"]:
                update_fields.append(f"{key} = ${param_count}")
                values.append(value)
                param_count += 1
        
        if not update_fields:
            return await get_rule(rule_id)
        
        # Add updated_at and rule_id
        update_fields.append(f"updated_at = NOW()")
        values.append(int(rule_id))
        
        query = f"""
            UPDATE mars.rules
            SET {', '.join(update_fields)}
            WHERE id = ${param_count}
            RETURNING id, sensor_id, operator, threshold, unit, actuator_id, actuator_state, enabled, description, created_at, updated_at
        """
        rows = await execute_query(query, *values)
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
