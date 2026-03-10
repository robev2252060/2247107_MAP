import asyncio
import json
import logging
from datetime import datetime, timezone
from aiokafka import AIOKafkaConsumer

from app.config import settings
from app.rule_engine import evaluate_rules_against_measurement
from app.db import fetch_rules_for_source
from app.kafka_producer import publish_actuator_state

logger = logging.getLogger(__name__)

# Track which rules are currently triggered: rule_id → bool
_rule_active_state: dict[str, bool] = {}


async def process_measurement_event(event: dict) -> None:
    """
    Process a MeasurementEvent from Kafka:
    1. Extract source from event
    2. Fetch active rules for that source
    3. Evaluate rules against the event's readings
    4. Publish actuator states on transitions
    """
    source = event.get("source")
    if not source:
        logger.debug("MeasurementEvent missing source, skipping")
        return

    timestamp = event.get("timestamp", datetime.now(timezone.utc).isoformat())

    # Fetch rules for this source
    rules = await fetch_rules_for_source(source)
    if not rules:
        return

    # Evaluate rules
    triggered_rules = evaluate_rules_against_measurement(event, rules)

    # Process rule state transitions and publish actuator states
    for evaluation in triggered_rules:
        rule_id = str(evaluation["rule_id"])
        is_triggered = evaluation["triggered"]
        was_triggered = _rule_active_state.get(rule_id, False)

        # State transition detected
        if is_triggered != was_triggered:
            _rule_active_state[rule_id] = is_triggered

            logger.info(
                "Rule %s %s: %s.%s=%s %s %s → %s=%s",
                rule_id,
                "triggered" if is_triggered else "cleared",
                evaluation["sensor_source"],
                evaluation["sensor_metric"],
                evaluation["measurement_value"],
                evaluation["operator"],
                evaluation["threshold_value"],
                evaluation["target_actuator"],
                evaluation["target_state"]
            )

            # Publish actuator state
            if is_triggered:
                await publish_actuator_state({
                    "actuator": evaluation["target_actuator"],
                    "state": evaluation["target_state"],
                    "triggered_by_rule": rule_id,
                    "timestamp": timestamp,
                })


async def consume_loop() -> None:
    consumer = AIOKafkaConsumer(
        settings.kafka_measurements_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
    )

    await consumer.start()
    logger.info("MS-Automation consumer started — listening on %s", settings.kafka_measurements_topic)

    try:
        async for msg in consumer:
            try:
                await process_measurement_event(msg.value)
            except Exception as exc:
                logger.exception("Error processing measurement event: %s", exc)
    finally:
        await consumer.stop()
