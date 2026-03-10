import asyncio
import logging
from typing import Literal

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.config import settings
from app.consumer import consume_loop
from app.simulator_client import get_all_actuators, set_actuator_state, KNOWN_ACTUATORS
from app.stream import stream_hub

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mars IoT - MS-Actuators", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ActuatorCommand(BaseModel):
    state: Literal["ON", "OFF"]


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

_consumer_task: asyncio.Task | None = None


@app.on_event("startup")
async def on_startup() -> None:
    global _consumer_task
    _consumer_task = asyncio.create_task(consume_loop())

    # Seed stream cache with current actuator states at boot.
    try:
        actuators = await get_all_actuators()
        stream_hub.seed_cache(actuators)
        logger.info("Seeded actuator stream cache with %d actuators", len(actuators))
    except Exception as exc:
        logger.warning("Failed to seed actuator stream cache at startup: %s", exc)


# ---------------------------------------------------------------------------
# REST endpoints (manual control from frontend)
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": settings.service_name}


@app.get("/api/actuators/stream")
async def stream_actuators() -> StreamingResponse:
    async def event_stream():
        queue = stream_hub.subscribe()
        try:
            for frame in stream_hub.replay_snapshot_frames():
                yield frame
            while True:
                frame = await queue.get()
                yield frame
        finally:
            stream_hub.unsubscribe(queue)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/actuators/")
async def list_actuators() -> list[dict]:
    """Return all actuators with their current simulator state."""
    try:
        actuators = await get_all_actuators()
        stream_hub.seed_cache(actuators)
        return actuators
    except Exception as exc:
        logger.exception("Error fetching actuators from simulator")
        # include the raw exception message so gateway/front-end can log it
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/actuators/{actuator_id}")
async def control_actuator(actuator_id: str, body: ActuatorCommand) -> dict:
    """Manually set an actuator state (bypasses Kafka - direct control)."""
    if actuator_id not in KNOWN_ACTUATORS:
        raise HTTPException(status_code=404, detail=f"Actuator '{actuator_id}' not found")
    try:
        result = await set_actuator_state(actuator_id, body.state)
        await stream_hub.publish_state(actuator_id, body.state)
        return {"actuator_id": actuator_id, "state": body.state, "result": result}
    except Exception as exc:
        logger.exception("Failed to set actuator %s", actuator_id)
        raise HTTPException(status_code=502, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.service_port, log_level="info")
