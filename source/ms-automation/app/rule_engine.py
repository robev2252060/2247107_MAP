"""
Rule Engine
-----------
Evaluates IF-THEN automation rules against a MeasurementEvent.

Rule model (from PostgreSQL):
{
    "id":               int,
    "sensor_source":    str,   — sensor source to watch
    "sensor_metric":    str,   — specific metric to monitor
    "operator":         str,   — one of: <, <=, =, >, >=
    "threshold_value":  float, — numeric comparison value
    "target_actuator":  str,   — target actuator
    "target_state":     str    — "ON" | "OFF"
}

MeasurementEvent model:
{
    "timestamp":  str (ISO 8601),
    "source":     str,
    "status":     str | None,
    "readings":   [{"metric": str, "value": number|str, "unit": str | None}]
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

TELEMETRY_PREFIX = "mars/telemetry/"


def to_final_source_identifier(source: str | None) -> str | None:
    if not source:
        return source
    return source[len(TELEMETRY_PREFIX):] if source.startswith(TELEMETRY_PREFIX) else source


def evaluate_rules_against_measurement(event: dict, rules: list[dict]) -> list[dict]:
    """
    Given a MeasurementEvent and a list of rules,
    return the list of rule evaluations.

    Each returned evaluation dict:
    {
        "rule_id":           int,
        "sensor_source":     str,
        "sensor_metric":     str,
        "measurement_value": float,
        "operator":          str,
        "threshold_value":   float,
        "target_actuator":   str,
        "target_state":      str,
        "triggered":         bool
    }
    """
    evaluations: list[dict] = []

    source = to_final_source_identifier(event.get("source"))
    readings = event.get("readings", [])

    if not source or not readings:
        return evaluations

    # Build metric -> value map
    metric_values = {}
    for reading in readings:
        metric = reading.get("metric")
        value = reading.get("value")
        if metric and value is not None:
            try:
                metric_values[metric] = float(value)
            except (TypeError, ValueError):
                pass

    # Evaluate each rule
    for rule in rules:
        rule_source = to_final_source_identifier(rule.get("sensor_source"))
        rule_metric = rule.get("sensor_metric")

        # Rule must match source (using final identifier only)
        if rule_source != source:
            continue

        # Check if we have the metric
        if rule_metric not in metric_values:
            continue

        measurement_value = metric_values[rule_metric]
        operator_str = rule.get("operator")
        threshold = rule.get("threshold_value")

        compare_fn = OPERATORS.get(operator_str)
        if compare_fn is None or threshold is None:
            logger.warning("Skipping malformed rule: %s", rule)
            continue

        try:
            triggered = compare_fn(measurement_value, float(threshold))

            evaluations.append({
                "rule_id":           rule["id"],
                "sensor_source":     rule_source,
                "sensor_metric":     rule_metric,
                "measurement_value": measurement_value,
                "operator":          operator_str,
                "threshold_value":   threshold,
                "target_actuator":   rule["target_actuator"],
                "target_state":      rule["target_state"],
                "triggered":         triggered,
            })

        except (TypeError, ValueError) as exc:
            logger.warning("Rule evaluation error: %s", exc)

    return evaluations
