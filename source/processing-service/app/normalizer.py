"""
Normalizer
----------
Converts raw simulator payloads into the unified MarsEvent schema defined
in input.md / SCHEMA_CONTRACT.

Unified event schema (MarsEvent):
{
    "event_id":     str   — UUID v4
    "sensor_id":    str   — matches simulator sensor name
    "schema_family":str   — e.g. "rest.scalar.v1"
    "timestamp":    str   — ISO-8601 UTC
    "value":        float | dict  — primary numeric value OR structured object
    "unit":         str | None    — SI unit string, null if not applicable
    "raw":          dict  — original unmodified simulator payload
}
"""

import uuid
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Schema family → normalization strategy mapping
# ---------------------------------------------------------------------------

SENSOR_SCHEMA_MAP: dict[str, str] = {
    "greenhouse_temperature": "rest.scalar.v1",
    "entrance_humidity":      "rest.scalar.v1",
    "co2_hall":               "rest.scalar.v1",
    "hydroponic_ph":          "rest.chemistry.v1",
    "water_tank_level":       "rest.level.v1",
    "corridor_pressure":      "rest.scalar.v1",
    "air_quality_pm25":       "rest.particulate.v1",
    "air_quality_voc":        "rest.chemistry.v1",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_scalar(raw: dict) -> tuple[float | None, str | None]:
    """Extract value + unit from rest.scalar.v1 payloads."""
    value = raw.get("value")
    unit = raw.get("unit")
    return value, unit


def _normalize_chemistry(raw: dict) -> tuple[float | dict | None, str | None]:
    """Extract value + unit from rest.chemistry.v1 payloads."""
    value = raw.get("value")
    unit = raw.get("unit")
    return value, unit


def _normalize_level(raw: dict) -> tuple[float | None, str | None]:
    """Extract value + unit from rest.level.v1 payloads."""
    value = raw.get("value") or raw.get("level")
    unit = raw.get("unit", "%")
    return value, unit


def _normalize_particulate(raw: dict) -> tuple[float | None, str | None]:
    """Extract value + unit from rest.particulate.v1 payloads."""
    value = raw.get("value") or raw.get("concentration")
    unit = raw.get("unit", "µg/m³")
    return value, unit


_NORMALIZER_DISPATCH: dict[str, Any] = {
    "rest.scalar.v1":      _normalize_scalar,
    "rest.chemistry.v1":   _normalize_chemistry,
    "rest.level.v1":       _normalize_level,
    "rest.particulate.v1": _normalize_particulate,
}


def normalize(sensor_id: str, raw_payload: dict) -> dict:
    """
    Produce a MarsEvent dict from a raw sensor payload.
    Returns None-safe defaults when a field is absent in the raw payload.
    """
    schema_family = SENSOR_SCHEMA_MAP.get(sensor_id, "unknown")
    dispatch = _NORMALIZER_DISPATCH.get(schema_family)

    if dispatch:
        value, unit = dispatch(raw_payload)
    else:
        value, unit = raw_payload.get("value"), raw_payload.get("unit")

    return {
        "event_id":     str(uuid.uuid4()),
        "sensor_id":    sensor_id,
        "schema_family": schema_family,
        "timestamp":    raw_payload.get("timestamp") or _now_iso(),
        "value":        value,
        "unit":         unit,
        "raw":          raw_payload,
    }
