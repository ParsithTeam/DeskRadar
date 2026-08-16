import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .analyzer.zero_shot_category import (
    is_classifier_loaded,
    preload_classifier,
)
from .api.routes.analyzer import router as analyzer_router

logger = logging.getLogger(__name__)


def env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@asynccontextmanager
async def lifespan(_: FastAPI):
    if env_flag("ANALYZER_PRELOAD_MODEL", default=True):
        try:
            await asyncio.to_thread(preload_classifier)
            logger.info("Zero-shot analyzer model loaded successfully")
        except Exception:
            logger.exception(
                "Zero-shot model preload failed; deterministic rule fallback remains active"
            )
    yield


app = FastAPI(
    title="DeskRadar AI Core",
    version="1.0.0",
    description="Standalone Persian service-desk ticket analysis API.",
    lifespan=lifespan,
)
app.include_router(analyzer_router)


@app.get("/health", tags=["System"])
def health() -> dict:
    return {
        "status": "ok",
        "zero_shot_model_loaded": is_classifier_loaded(),
        "rule_fallback_available": True,
    }
