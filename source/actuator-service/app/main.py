import asyncio
import logging
from typing import Literal

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.consumer import consume_loop
from app.simulator_client import get_all_actuators, set_actuator_state, KNOWN_ACTUATORS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mars IoT — Actuator Service", version="1.0.0")

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

@app.on_event("startup")
async def on_startup() -> None:
    asyncio.create_task(consume_loop())


# ---------------------------------------------------------------------------
# REST endpoints (manual control from frontend)
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "actuator-service"}


# we expose the list endpoint with a trailing slash to match the
# gateway path `/api/actuators/` and avoid FastAPI redirect noise. the
# underlying function signature is unchanged.
@app.get("/actuators/")
async def list_actuators() -> list[dict]:
    """Return all actuators with their current simulator state."""
    try:
        return await get_all_actuators()
    except Exception as exc:
        logger.exception("Error fetching actuators from simulator")
        # include the raw exception message so gateway/front-end can log it
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/actuators/{actuator_id}")
async def control_actuator(actuator_id: str, body: ActuatorCommand) -> dict:
    """Manually set an actuator state (bypasses Kafka — direct control)."""
    if actuator_id not in KNOWN_ACTUATORS:
        raise HTTPException(status_code=404, detail=f"Actuator '{actuator_id}' not found")
    try:
        result = await set_actuator_state(actuator_id, body.state)
        return {"actuator_id": actuator_id, "state": body.state, "result": result}
    except Exception as exc:
        logger.exception("Failed to set actuator %s", actuator_id)
        raise HTTPException(status_code=502, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.service_port, log_level="info")
