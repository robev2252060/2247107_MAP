"""
Rule Engine
-----------
Evaluates IF-THEN automation rules against a normalized MarsEvent.

Rule model (from MongoDB):
{
    "sensor_id":    str,   — sensor to watch
    "operator":     str,   — one of: <, <=, =, >, >=
    "threshold":    float, — numeric comparison value
    "unit":         str | None,
    "actuator_id":  str,   — target actuator
    "actuator_state": "ON" | "OFF"
}
"""

import logging
import operator as op
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Operator map
# ---------------------------------------------------------------------------

OPERATORS: dict[str, Any] = {
    "<":  op.lt,
    "<=": op.le,
    "=":  op.eq,
    ">=": op.ge,
    ">":  op.gt,
}


def evaluate_rules(event: dict, rules: list[dict]) -> list[dict]:
    """
    Given a normalized MarsEvent and a list of persisted rules,
    return the list of actuator commands that should be triggered.

    Each returned command dict:
    {
        "actuator_id":    str,
        "actuator_state": "ON" | "OFF",
        "triggered_by_rule": str  (rule _id as string)
    }
    """
    commands: list[dict] = []

    sensor_id = event.get("sensor_id")
    event_value = event.get("value")

    if event_value is None or not isinstance(event_value, (int, float)):
        return commands

    for rule in rules:
        if rule.get("sensor_id") != sensor_id:
            continue

        operator_str = rule.get("operator", "")
        threshold = rule.get("threshold")
        compare_fn = OPERATORS.get(operator_str)

        if compare_fn is None or threshold is None:
            logger.warning("Skipping malformed rule: %s", rule)
            continue

        try:
            if compare_fn(float(event_value), float(threshold)):
                commands.append({
                    "actuator_id":       rule["actuator_id"],
                    "actuator_state":    rule["actuator_state"],
                    "triggered_by_rule": str(rule.get("_id", "")),
                })
                logger.info(
                    "Rule triggered: %s %s %s → %s=%s",
                    sensor_id, operator_str, threshold,
                    rule["actuator_id"], rule["actuator_state"],
                )
        except (TypeError, ValueError) as exc:
            logger.warning("Rule evaluation error: %s", exc)

    return commands
