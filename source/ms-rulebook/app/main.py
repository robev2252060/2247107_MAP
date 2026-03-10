import logging

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

app = FastAPI(title="Mars IoT — Rule Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Test database connection on startup."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        logger.info("Database connection test successful")
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        raise


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "ms-rulebook"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.service_port, log_level="info")
