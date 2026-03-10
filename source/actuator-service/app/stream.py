import asyncio
import json
from datetime import datetime, timezone
from typing import Any


class ActuatorStreamHub:
    def __init__(self) -> None:
        self._subscribers: list[asyncio.Queue[str]] = []

    def subscribe(self) -> asyncio.Queue[str]:
        queue: asyncio.Queue[str] = asyncio.Queue()
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[str]) -> None:
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    async def publish(self, payload: dict[str, Any]) -> None:
        frame = f"event: measurement\ndata:{json.dumps(payload)}\n\n"
        for queue in list(self._subscribers):
            await queue.put(frame)


def to_measurement_event(actuator: str, state: str) -> dict[str, Any]:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": actuator,
        "readings": [
            {"metric": "state", "value": state}
        ],
    }


stream_hub = ActuatorStreamHub()

