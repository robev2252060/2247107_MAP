import json
import logging
from aiokafka import AIOKafkaConsumer

from app.config import settings
from app.simulator_client import set_actuator_state
from app.stream import stream_hub, to_measurement_event

logger = logging.getLogger(__name__)


async def consume_loop() -> None:
    consumer = AIOKafkaConsumer(
        settings.kafka_automation_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
    )

    await consumer.start()
    logger.info("Actuator consumer started - listening on %s", settings.kafka_automation_topic)

    try:
        async for msg in consumer:
            command = msg.value
            actuator_id = command.get("actuator") or command.get("actuator_id")
            actuator_state = command.get("state") or command.get("actuator_state")

            if not actuator_id or actuator_state not in {"ON", "OFF"}:
                logger.warning("Malformed actuator command: %s", command)
                continue

            try:
                await set_actuator_state(actuator_id, actuator_state)
                await stream_hub.publish(to_measurement_event(actuator_id, actuator_state))
            except Exception as exc:
                logger.exception("Failed to execute actuator command %s: %s", command, exc)
    finally:
        await consumer.stop()
