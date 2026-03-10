import asyncio
import json
from datetime import datetime, timezone
from typing import Any


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ActuatorStreamHub:
    def __init__(self) -> None:
        self._subscribers: list[asyncio.Queue[str]] = []
        self._state_cache: dict[str, dict[str, str]] = {}

    def subscribe(self) -> asyncio.Queue[str]:
        queue: asyncio.Queue[str] = asyncio.Queue()
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[str]) -> None:
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    def seed_cache(self, actuators: list[dict[str, Any]]) -> None:
        for actuator in actuators:
            actuator_id = actuator.get("actuator_name")
            state = actuator.get("state")
            updated_at = actuator.get("updated_at") or _iso_now()
            if actuator_id and state:
                self._state_cache[actuator_id] = {
                    "state": state,
                    "updated_at": updated_at,
                }

    def replay_snapshot_frames(self) -> list[str]:
        frames: list[str] = []
        for actuator_id, cached in self._state_cache.items():
            payload = to_measurement_event(actuator_id, cached["state"], cached["updated_at"])
            frames.append(self._to_frame(payload))
        return frames

    async def publish_state(
        self,
        actuator: str,
        state: str,
        timestamp: str | None = None,
        rule_id: str | None = None,
    ) -> None:
        ts = timestamp or _iso_now()
        self._state_cache[actuator] = {
            "state": state,
            "updated_at": ts,
        }

        payload = to_measurement_event(actuator, state, ts, rule_id)
        frame = self._to_frame(payload)

        for queue in self._subscribers:
            await queue.put(frame)

    def _to_frame(self, payload: dict[str, Any]) -> str:
        return f"event: measurement\ndata:{json.dumps(payload)}\n\n"


def to_measurement_event(
    actuator: str,
    state: str,
    timestamp: str | None = None,
    rule_id: str | None = None,
) -> dict[str, Any]:
    event = {
        "timestamp": timestamp or _iso_now(),
        "source": actuator,
        "readings": [
            {"metric": "state", "value": state}
        ],
    }
    if rule_id:
        event["rule_id"] = rule_id
    return event


stream_hub = ActuatorStreamHub()
