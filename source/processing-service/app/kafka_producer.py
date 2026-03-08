import json
import logging
from aiokafka import AIOKafkaProducer
from app.config import settings

logger = logging.getLogger(__name__)

TOPIC_NORMALIZED_EVENTS  = "mars.normalized.events"
TOPIC_ACTUATOR_COMMANDS  = "mars.actuator.commands"

_producer: AIOKafkaProducer | None = None


async def get_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )
        await _producer.start()
        logger.info("Kafka producer started (processing-service)")
    return _producer


async def stop_producer() -> None:
    global _producer
    if _producer is not None:
        await _producer.stop()
        _producer = None


async def publish_normalized_event(event: dict) -> None:
    producer = await get_producer()
    await producer.send(TOPIC_NORMALIZED_EVENTS, key=event["sensor_id"], value=event)


async def publish_actuator_command(command: dict) -> None:
    producer = await get_producer()
    await producer.send(TOPIC_ACTUATOR_COMMANDS, key=command["actuator_id"], value=command)
