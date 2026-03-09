"""
Pydantic models for Automation Rules.

Rule schema enforces the IF–THEN grammar defined in the specification:
    IF <sensor_id> <operator> <threshold> [unit]
    THEN set <actuator_id> to ON | OFF
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


VALID_OPERATORS = {"<", "<=", "=", ">=", ">"}

VALID_SENSORS = {
    "greenhouse_temperature",
    "entrance_humidity",
    "co2_hall",
    "hydroponic_ph",
    "water_tank_level",
    "corridor_pressure",
    "air_quality_pm25",
    "air_quality_voc",
}

VALID_ACTUATORS = {
    "cooling_fan",
    "entrance_humidifier",
    "hall_ventilation",
    "habitat_heater",
}


class RuleCreate(BaseModel):
    sensor_id: str = Field(..., description="Sensor to watch")
    operator: str = Field(..., description="Comparison operator: <, <=, =, >=, >")
    threshold: float = Field(..., description="Numeric threshold value")
    unit: Optional[str] = Field(None, description="Optional unit string, e.g. '°C'")
    actuator_id: str = Field(..., description="Actuator to control")
    actuator_state: Literal["ON", "OFF"] = Field(..., description="Target actuator state")
    enabled: bool = Field(True, description="Whether the rule is active")
    description: Optional[str] = Field(None, description="Human-readable description")

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v: str) -> str:
        if v not in VALID_OPERATORS:
            raise ValueError(f"operator must be one of {VALID_OPERATORS}")
        return v

    @field_validator("sensor_id")
    @classmethod
    def validate_sensor(cls, v: str) -> str:
        if v not in VALID_SENSORS:
            raise ValueError(f"Unknown sensor_id '{v}'")
        return v

    @field_validator("actuator_id")
    @classmethod
    def validate_actuator(cls, v: str) -> str:
        if v not in VALID_ACTUATORS:
            raise ValueError(f"Unknown actuator_id '{v}'")
        return v


class RuleUpdate(BaseModel):
    operator: Optional[str] = None
    threshold: Optional[float] = None
    unit: Optional[str] = None
    actuator_state: Optional[Literal["ON", "OFF"]] = None
    enabled: Optional[bool] = None
    description: Optional[str] = None

    @field_validator("operator")
    @classmethod
    def validate_operator_update(cls, v: str) -> str:
        if v is not None and v not in VALID_OPERATORS:
            raise ValueError(f"operator must be one of {VALID_OPERATORS}")
        return v


class RuleResponse(RuleCreate):
    id: str = Field(..., alias="_id")

    class Config:
        populate_by_name = True
