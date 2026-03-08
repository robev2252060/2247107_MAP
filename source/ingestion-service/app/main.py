import asyncio
import logging

import uvicorn
from fastapi import FastAPI

from app.config import settings
from app.kafka_producer import stop_producer
from app.poller import polling_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mars IoT — Ingestion Service", version="1.0.0")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "ingestion-service"}


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Ingestion service starting up")
    # Launch the polling loop as a background task
    asyncio.create_task(polling_loop())


@app.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info("Ingestion service shutting down")
    await stop_producer()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.service_port,
        log_level="info",
    )
