import logging
import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import router
from app.db import get_pool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""

    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            pool = await get_pool()
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            logger.info("Database connection test successful!")
            break 
            
        except Exception as e:
            logger.error(f"Database connection test failed (Attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                logger.info("Retrying in 2 seconds...")
                await asyncio.sleep(2)
            else:
                logger.critical("Could not connect to the database after multiple retries. Exiting.")
                raise e
    yield 


app = FastAPI(
    title="Mars Automation Platform — Rule Service", 
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "ms-rulebook"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.service_port, log_level="info")
