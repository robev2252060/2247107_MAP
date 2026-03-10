import json
import logging
from aiokafka import AIOKafkaProducer
from app.config import settings

logger = logging.getLogger(__name__)

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
        logger.info("Kafka producer started (ms-automation)")
    return _producer


async def stop_producer() -> None:
    global _producer
    if _producer is not None:
        await _producer.stop()
        _producer = None
        logger.info("Kafka producer stopped")


async def publish_actuator_state(state: dict) -> None:
    """
    Publish actuator state to actuators.automation topic.

    Expected state dict:
    {
        "actuator": str,
        "state": str ("ON" | "OFF"),
        "triggered_by_rule": str,
        "timestamp": str
    }
    """
    producer = await get_producer()
    await producer.send(
        settings.kafka_actuators_topic,
        key=state.get("actuator"),
        value=state
    )
    logger.debug(f"Published actuator state: {state['actuator']}={state['state']}")
