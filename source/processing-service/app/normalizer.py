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


# ---------------------------------------------------------------------------
# Unit standardization helpers
# ---------------------------------------------------------------------------

# Canonical units we want to expose to operators (SI wherever applicable).
# All raw measurements should be converted into these so the dashboard can
# display consistent values and so automation rules are evaluated reliably.
_STANDARD_UNIT_BY_SENSOR: dict[str, str] = {
    "greenhouse_temperature": "°C",
    "entrance_humidity":      "%",
    "co2_hall":               "ppm",
    "hydroponic_ph":          "pH",
    "water_tank_level":       "%",
    "corridor_pressure":      "Pa",
    "air_quality_pm25":       "µg/m³",
    "air_quality_voc":        "ppb",
}


def _to_number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _convert_temperature(value: Any, unit: str | None) -> float | None:
    x = _to_number(value)
    if x is None:
        return None
    if not unit:
        return x

    u = unit.strip().lower()
    if u in ("c", "°c", "celsius"):
        return x
    if u in ("f", "°f", "fahrenheit"):
        return (x - 32) * 5.0 / 9.0
    if u in ("k", "kelvin"):
        return x - 273.15
    return x


def _convert_percent(value: Any, unit: str | None) -> float | None:
    x = _to_number(value)
    if x is None:
        return None
    if not unit:
        return x

    u = unit.strip().lower()
    if u in ("%", "percent", "pct"):
        return x
    if u in ("ratio", "fraction"):
        return x * 100.0
    return x


def _convert_ppm(value: Any, unit: str | None) -> float | None:
    x = _to_number(value)
    if x is None:
        return None
    if not unit:
        return x

    u = unit.strip().lower()
    if u in ("ppm",):
        return x
    if u in ("ppb",):
        return x / 1000.0
    if u in ("%", "percent", "pct"):
        # treat as fraction (0-1) relative to 1 ppm
        return x * 1_000_000.0
    return x


def _convert_pressure(value: Any, unit: str | None) -> float | None:
    x = _to_number(value)
    if x is None:
        return None
    if not unit:
        return x

    u = unit.strip().lower()
    if u in ("pa", "pascal", "pascals"):
        return x
    if u in ("kpa",):
        return x * 1000.0
    if u in ("mpa",):
        return x * 1_000_000.0
    if u in ("bar",):
        return x * 100_000.0
    if u in ("mbar", "hpa"):
        return x * 100.0
    if u in ("mmhg", "torr"):
        return x * 133.322
    if u in ("psi",):
        return x * 6894.757
    return x


def _convert_mass_concentration(value: Any, unit: str | None) -> float | None:
    x = _to_number(value)
    if x is None:
        return None
    if not unit:
        return x

    u = unit.strip().lower().replace(" ", "")
    if u in ("µg/m³", "ug/m3", "ug/m^3", "µg/m3", "ug/m³"):
        return x
    if u in ("mg/m³", "mg/m3", "mg/m^3"):
        return x * 1000.0
    if u in ("g/m³", "g/m3", "g/m^3"):
        return x * 1_000_000.0
    return x


def _standardize_value_and_unit(sensor_id: str, value: Any, unit: str | None) -> tuple[Any, str | None]:
    """Standardize a sensor measurement to a canonical unit and numeric value."""

    target_unit = _STANDARD_UNIT_BY_SENSOR.get(sensor_id)
    if not target_unit:
        return value, unit

    if target_unit == "°C":
        return _convert_temperature(value, unit), target_unit
    if target_unit == "%":
        return _convert_percent(value, unit), target_unit
    if target_unit == "ppm":
        return _convert_ppm(value, unit), target_unit
    if target_unit == "pH":
        return _to_number(value), target_unit
    if target_unit == "Pa":
        return _convert_pressure(value, unit), target_unit
    if target_unit == "µg/m³":
        return _convert_mass_concentration(value, unit), target_unit

    return value, unit


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

    # Ensure all output events use canonical units (SI where possible) so the
    # dashboard and automation rules are consistent across different sensors.
    value, unit = _standardize_value_and_unit(sensor_id, value, unit)

    return {
        "event_id":     str(uuid.uuid4()),
        "sensor_id":    sensor_id,
        "schema_family": schema_family,
        "timestamp":    raw_payload.get("timestamp") or _now_iso(),
        "value":        value,
        "unit":         unit,
        "raw":          raw_payload,
    }
