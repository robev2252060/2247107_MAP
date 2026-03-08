"""
StateStore
----------
Thread-safe in-memory store for latest sensor state.
Exposes an asyncio.Queue-based broadcast mechanism so SSE subscribers
receive updates the moment a new event is committed.
"""

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


class StateStore:
    def __init__(self) -> None:
        # sensor_id → latest MarsEvent dict
        self._state: dict[str, dict] = {}
        # Set of subscriber queues for SSE broadcast
        self._subscribers: set[asyncio.Queue] = set()

    def update(self, event: dict) -> None:
        """Commit a new MarsEvent and broadcast to all SSE subscribers."""
        sensor_id: str = event.get("sensor_id", "unknown")
        self._state[sensor_id] = event
        logger.debug("State updated for sensor %s", sensor_id)
        self._broadcast(event)

    def _broadcast(self, event: dict) -> None:
        dead: set[asyncio.Queue] = set()
        for q in self._subscribers:
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                dead.add(q)
        self._subscribers -= dead

    def get_all(self) -> dict[str, dict]:
        return dict(self._state)

    def get_one(self, sensor_id: str) -> dict | None:
        return self._state.get(sensor_id)

    def subscribe(self) -> asyncio.Queue:
        """Register a new SSE subscriber; returns its dedicated Queue."""
        q: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subscribers.add(q)
        logger.debug("SSE subscriber added (total=%d)", len(self._subscribers))
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self._subscribers.discard(q)
        logger.debug("SSE subscriber removed (total=%d)", len(self._subscribers))


# Singleton instance shared across the FastAPI application
store = StateStore()
