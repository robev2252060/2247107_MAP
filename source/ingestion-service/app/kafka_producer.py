import json
import logging
from aiokafka import AIOKafkaProducer
from app.config import settings

logger = logging.getLogger(__name__)

# Kafka topic where raw sensor payloads are published
TOPIC_RAW_SENSORS = "mars.raw.sensors"

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
        logger.info("Kafka producer started")
    return _producer


async def stop_producer() -> None:
    global _producer
    if _producer is not None:
        await _producer.stop()
        _producer = None
        logger.info("Kafka producer stopped")


async def publish_raw_event(sensor_id: str, payload: dict) -> None:
    """Publish a raw sensor reading to mars.raw.sensors."""
    producer = await get_producer()
    message = {
        "sensor_id": sensor_id,
        "raw_payload": payload,
    }
    await producer.send(TOPIC_RAW_SENSORS, key=sensor_id, value=message)
    logger.debug("Published raw event for sensor %s", sensor_id)
