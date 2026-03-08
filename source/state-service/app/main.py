import asyncio
import json
import logging

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.config import settings
from app.consumer import consume_loop
from app.state_store import store

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mars IoT — State Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Startup / shutdown
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def on_startup() -> None:
    asyncio.create_task(consume_loop())


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "state-service"}


@app.get("/sensors")
async def get_all_sensors() -> dict:
    """Return latest state for all sensors."""
    return store.get_all()


@app.get("/sensors/{sensor_id}")
async def get_sensor(sensor_id: str) -> dict:
    """Return latest state for a single sensor."""
    state = store.get_one(sensor_id)
    if state is None:
        raise HTTPException(status_code=404, detail=f"Sensor '{sensor_id}' not found")
    return state


# ---------------------------------------------------------------------------
# SSE endpoint — real-time push to dashboard
# ---------------------------------------------------------------------------

@app.get("/sensors/stream/sse")
async def sse_stream():
    """
    Server-Sent Events stream.
    Emits a 'sensor_update' event every time any sensor state changes.
    """
    async def event_generator():
        q = store.subscribe()
        try:
            # Send current full snapshot on connect
            snapshot = store.get_all()
            yield f"event: snapshot\ndata: {json.dumps(snapshot)}\n\n"

            while True:
                event = await q.get()
                yield f"event: sensor_update\ndata: {json.dumps(event)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            store.unsubscribe(q)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering
        },
    )


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.service_port, log_level="info")
