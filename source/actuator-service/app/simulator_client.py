"""
Simulator Actuator Client
-------------------------
Wraps the simulator's REST actuator API.

Simulator endpoint:
    POST /api/actuators/{actuator_id}
    Body: {"state": "ON" | "OFF"}

Available actuators (from spec § 3.4):
    cooling_fan, entrance_humidifier, hall_ventilation, habitat_heater
"""

import logging
from datetime import datetime, timezone
from typing import Literal

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# This needs to be in the database
KNOWN_ACTUATORS = {
    "cooling_fan",
    "entrance_humidifier",
    "hall_ventilation",
    "habitat_heater",
}

# In-memory cache of last-known actuator states and update timestamps
_actuator_state_cache: dict[str, dict[str, str]] = {}


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _cache_state(actuator_id: str, state: str, timestamp: str | None = None) -> None:
    _actuator_state_cache[actuator_id] = {
        "state": state,
        "updated_at": timestamp or _iso_now(),
    }


def _normalize_state(raw_state) -> str:
    """Normalize simulator state values to canonical 'ON' / 'OFF' strings."""
    if isinstance(raw_state, bool):
        return "ON" if raw_state else "OFF"
    if isinstance(raw_state, str):
        return "ON" if raw_state.upper() == "ON" else "OFF"
    return "OFF"


async def set_actuator_state(
    actuator_id: str,
    state: Literal["ON", "OFF"],
) -> dict:
    """
    Send a state-change command to the simulator.
    Returns the simulator's JSON response.
    """
    if actuator_id not in KNOWN_ACTUATORS:
        raise ValueError(f"Unknown actuator: {actuator_id}")

    url = f"{settings.simulator_base_url}/api/actuators/{actuator_id}"
    payload = {"state": state}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=5.0)
        response.raise_for_status()
        result = response.json()

    _cache_state(actuator_id, state)
    logger.info("Actuator %s set to %s", actuator_id, state)
    return result


async def get_all_actuators() -> list[dict]:
    """Fetch current state of all actuators from the simulator."""
    url = f"{settings.simulator_base_url}/api/actuators"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=5.0)
        response.raise_for_status()
        data = response.json()

    actuators: list[dict] = []
    for actuator_id, raw_state in data["actuators"].items():
        normalized_state = _normalize_state(raw_state)
        _cache_state(actuator_id, normalized_state)
        actuators.append({
            "actuator_name": actuator_id,
            "state": normalized_state,
            "updated_at": _actuator_state_cache[actuator_id]["updated_at"],
        })

    return actuators
