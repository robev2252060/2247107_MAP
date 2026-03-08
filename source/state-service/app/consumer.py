import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer

from app.config import settings
from app.state_store import store

logger = logging.getLogger(__name__)

TOPIC_NORMALIZED_EVENTS = "mars.normalized.events"


async def consume_loop() -> None:
    consumer = AIOKafkaConsumer(
        TOPIC_NORMALIZED_EVENTS,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
    )

    await consumer.start()
    logger.info("State consumer started — listening on %s", TOPIC_NORMALIZED_EVENTS)

    try:
        async for msg in consumer:
            try:
                store.update(msg.value)
            except Exception as exc:
                logger.exception("Error updating state: %s", exc)
    finally:
        await consumer.stop()
