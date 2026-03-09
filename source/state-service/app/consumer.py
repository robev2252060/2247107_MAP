import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer

from app.config import settings
from app.state_store import store

logger = logging.getLogger(__name__)

TOPIC_NORMALIZED_EVENTS = "mars.normalized.events"
TOPIC_RULE_EVENTS       = "mars.rule.events"


async def consume_loop() -> None:
    consumer = AIOKafkaConsumer(
        TOPIC_NORMALIZED_EVENTS,
        TOPIC_RULE_EVENTS,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
    )

    await consumer.start()
    logger.info(
        "State consumer started — listening on %s, %s",
        TOPIC_NORMALIZED_EVENTS, TOPIC_RULE_EVENTS,
    )

    try:
        async for msg in consumer:
            try:
                if msg.topic == TOPIC_NORMALIZED_EVENTS:
                    store.update(msg.value)
                elif msg.topic == TOPIC_RULE_EVENTS:
                    store.publish_rule_event(msg.value)
            except Exception as exc:
                logger.exception("Error processing message: %s", exc)
    finally:
        await consumer.stop()
