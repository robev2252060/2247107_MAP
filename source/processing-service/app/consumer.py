import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer

from app.config import settings
from app.normalizer import normalize
from app.rule_engine import evaluate_rules
from app.db import fetch_rules
from app.kafka_producer import publish_normalized_event, publish_actuator_command

logger = logging.getLogger(__name__)

TOPIC_RAW_SENSORS = "mars.raw.sensors"


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
    commands = evaluate_rules(event, rules)

    # 4. Publish actuator commands (consumed by actuator-service)
    for command in commands:
        await publish_actuator_command(command)


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
