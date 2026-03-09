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

# In-memory cache of last-known actuator states
_actuator_state_cache: dict[str, str] = {}


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

    _actuator_state_cache[actuator_id] = state
    logger.info("Actuator %s set to %s", actuator_id, state)
    return result


def _normalize_state(raw_state) -> str:
    """Normalize simulator state values to canonical 'ON' / 'OFF' strings."""
    if isinstance(raw_state, bool):
        return "ON" if raw_state else "OFF"
    if isinstance(raw_state, str):
        return "ON" if raw_state.upper() == "ON" else "OFF"
    return "OFF"


async def get_all_actuators() -> list[dict]:
    """Fetch current state of all actuators from the simulator."""
    url = f"{settings.simulator_base_url}/api/actuators"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=5.0)
        response.raise_for_status()
        data = response.json()
        # Transform to list of dicts, normalising state to "ON" / "OFF"
        return [
            {"actuator_name": actuator_id, "state": _normalize_state(state)}
            for actuator_id, state in data["actuators"].items()
        ]
