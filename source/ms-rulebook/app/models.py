"""
Pydantic models for Automation Rules.

Rule schema enforces the IF–THEN grammar defined in the specification:
    IF <sensor_source>.<sensor_metric> <operator> <threshold_value>
    THEN set <target_actuator> to <target_state>
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class RuleCreate(BaseModel):
    sensor_source: str = Field(..., description="Sensor source to watch (e.g., 'rest:greenhouse_temperature')")
    sensor_metric: str = Field(..., description="Specific metric to monitor (e.g., 'temperature')")
    operator: Literal["<", "<=", "=", ">=", ">"] = Field(..., description="Comparison operator")
    threshold_value: float = Field(..., description="Numeric threshold value")
    target_actuator: str = Field(..., description="Actuator to control")
    target_state: Literal["ON", "OFF"] = Field(..., description="Target actuator state")
    enabled: bool = Field(True, description="Whether the rule is active")
    description: Optional[str] = Field(None, description="Human-readable description")


class RuleUpdate(BaseModel):
    sensor_source: str = Field(..., description="Sensor source to watch")
    sensor_metric: str = Field(..., description="Specific metric to monitor")
    operator: Literal["<", "<=", "=", ">=", ">"] = Field(..., description="Comparison operator")
    threshold_value: float = Field(..., description="Numeric threshold value")
    target_actuator: str = Field(..., description="Actuator to control")
    target_state: Literal["ON", "OFF"] = Field(..., description="Target actuator state")
    enabled: bool = Field(True, description="Whether the rule is active")
    description: Optional[str] = Field(None, description="Human-readable description")


class RuleResponse(RuleCreate):
    id: str = Field(..., description="Unique rule identifier")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True
