import asyncio
import json
import logging
from datetime import datetime, timezone
from aiokafka import AIOKafkaConsumer

from app.config import settings
from app.normalizer import normalize
from app.rule_engine import evaluate_rules
from app.db import fetch_rules
from app.kafka_producer import publish_normalized_event, publish_actuator_command, publish_rule_event

logger = logging.getLogger(__name__)

TOPIC_RAW_SENSORS = "mars.raw.sensors"

# Track which rules are currently triggered: rule_id → bool
_rule_active_state: dict[str, bool] = {}


async def process_message(raw_msg: dict) -> None:
    """Full pipeline: normalize → publish → evaluate rules → publish commands."""
    sensor_id = raw_msg.get("sensor_id", "unknown")
    raw_payload = raw_msg.get("raw_payload", {})

    # 1. Normalize
    event = normalize(sensor_id, raw_payload)

    # 2. Publish normalized event (consumed by state-service)
    await publish_normalized_event(event)

    # 3. Evaluate automation rules
    rules = await fetch_rules(sensor_id)
    triggered_rule_ids = {c["triggered_by_rule"] for c in evaluate_rules(event, rules)}

    # 4. Detect transitions and publish rule events + actuator commands
    for rule in rules:
        rule_id = str(rule.get("_id", ""))
        was_active = _rule_active_state.get(rule_id, False)
        is_active = rule_id in triggered_rule_ids

        if is_active != was_active:
            _rule_active_state[rule_id] = is_active
            await publish_rule_event({
                "rule_id":        rule_id,
                "sensor_id":      rule["sensor_id"],
                "actuator_id":    rule["actuator_id"],
                "actuator_state": rule["actuator_state"],
                "operator":       rule["operator"],
                "threshold":      rule["threshold"],
                "unit":           rule.get("unit"),
                "description":    rule.get("description"),
                "triggered":      is_active,
                "timestamp":      datetime.now(timezone.utc).isoformat(),
            })
            logger.info(
                "Rule %s transition: %s → %s",
                rule_id, was_active, is_active,
            )

        if is_active:
            await publish_actuator_command({
                "actuator_id":       rule["actuator_id"],
                "actuator_state":    rule["actuator_state"],
                "triggered_by_rule": rule_id,
            })


async def consume_loop() -> None:
    consumer = AIOKafkaConsumer(
        TOPIC_RAW_SENSORS,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
    )

    await consumer.start()
    logger.info("Processing consumer started — listening on %s", TOPIC_RAW_SENSORS)

    try:
        async for msg in consumer:
            try:
                await process_message(msg.value)
            except Exception as exc:
                logger.exception("Error processing message: %s", exc)
    finally:
        await consumer.stop()
