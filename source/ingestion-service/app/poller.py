import asyncio
import logging
from typing import Any

import httpx

from app.config import settings
from app.kafka_producer import publish_raw_event

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sensor registry
# Maps sensor_id → REST path (relative to SIMULATOR_BASE_URL)
# Source: Project_Specification.md § 3.2
# ---------------------------------------------------------------------------
SENSOR_ENDPOINTS: dict[str, str] = {
    "greenhouse_temperature": "/api/sensors/greenhouse_temperature",
    "entrance_humidity":      "/api/sensors/entrance_humidity",
    "co2_hall":               "/api/sensors/co2_hall",
    "hydroponic_ph":          "/api/sensors/hydroponic_ph",
    "water_tank_level":       "/api/sensors/water_tank_level",
    "corridor_pressure":      "/api/sensors/corridor_pressure",
    "air_quality_pm25":       "/api/sensors/air_quality_pm25",
    "air_quality_voc":        "/api/sensors/air_quality_voc",
}


async def poll_sensor(client: httpx.AsyncClient, sensor_id: str, path: str) -> None:
    """Fetch one sensor reading and forward it to Kafka."""
    url = f"{settings.simulator_base_url}{path}"
    try:
        response = await client.get(url, timeout=5.0)
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        await publish_raw_event(sensor_id, payload)
    except httpx.HTTPStatusError as exc:
        logger.warning("HTTP error polling %s: %s", sensor_id, exc.response.status_code)
    except httpx.RequestError as exc:
        logger.warning("Request error polling %s: %s", sensor_id, exc)


async def poll_all_sensors(client: httpx.AsyncClient) -> None:
    """Poll every sensor concurrently in one sweep."""
    tasks = [
        poll_sensor(client, sensor_id, path)
        for sensor_id, path in SENSOR_ENDPOINTS.items()
    ]
    await asyncio.gather(*tasks, return_exceptions=True)


async def polling_loop() -> None:
    """Infinite polling loop; runs as a background asyncio task."""
    logger.info(
        "Polling loop started — interval=%ds, sensors=%d",
        settings.poll_interval_seconds,
        len(SENSOR_ENDPOINTS),
    )
    async with httpx.AsyncClient(base_url=settings.simulator_base_url) as client:
        while True:
            await poll_all_sensors(client)
            await asyncio.sleep(settings.poll_interval_seconds)
