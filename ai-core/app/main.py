"""
ServiceDesk Radar — AI Core
app/main.py

Unified FastAPI application entrypoint.
Wires HTTP endpoints for:
  - Unified Composite Analysis (Analyzer NLP + Infrastructure Semantic Intelligence) -> POST /analyze
  - Standalone Analyzer API -> POST /analyzer/analyze
  - Standalone Infrastructure API -> POST /analyze-ticket
  - System Health & Readiness -> GET /health
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.concurrency import run_in_threadpool

from app.analyzer.analyzer_service import analyze_ticket as analyze_ticket_analyzer
from app.analyzer.zero_shot_category import is_classifier_loaded, preload_classifier
from app.api.routes.analyzer import router as analyzer_router
from app.infrastructure import initialize_infrastructure, run_infrastructure
from app.infrastructure.schemas import (
    InfrastructureHealthStatus,
    InfrastructureRequest,
    InfrastructureResult,
)
from app.schemas.unified import UnifiedAnalyzeRequest, UnifiedAnalyzeResponse

logger = logging.getLogger(__name__)


def env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


import importlib


def _maybe_initialize_analyzer() -> None:
    """
    Initialize the Analyzer only if its module is installed. Its presence,
    absence, or failure must never affect the Infrastructure service.
    """
    try:
        analyzer = importlib.import_module("app.analyzer")
    except ModuleNotFoundError:
        logger.info("Analyzer module not present; running Infrastructure only.")
        return

    initialize_analyzer = getattr(analyzer, "initialize_analyzer", None)
    if not callable(initialize_analyzer):
        logger.info("Analyzer has no initializer; running Infrastructure only.")
        return

    try:
        initialize_analyzer()
        logger.info("Analyzer initialized.")
    except Exception:  # noqa: BLE001 - Analyzer failure must not break Infrastructure
        logger.exception("Analyzer initialization failed; Infrastructure unaffected.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup sequence for AI Core:
      1. Initialize Infrastructure (EmbeddingModel singleton, KB articles, Vector cache).
      2. Preload Zero-Shot Classifier for Analyzer (with rule-engine fallback safety).
    """
    logger.info("Initializing AI Core subsystems...")

    # 1. Initialize Infrastructure
    app.state.infra_health = initialize_infrastructure()
    logger.info(
        "Infrastructure initialized: status=%s model_loaded=%s articles=%s tickets=%s qdrant=%s",
        app.state.infra_health.status,
        app.state.infra_health.model_loaded,
        app.state.infra_health.articles_indexed,
        app.state.infra_health.tickets_in_pool,
        app.state.infra_health.qdrant_mode,
    )

    # 2. Check for Analyzer initializer hook
    _maybe_initialize_analyzer()

    # 3. Preload Analyzer Zero-Shot Model if enabled
    if env_flag("ANALYZER_PRELOAD_MODEL", default=True):
        try:
            await run_in_threadpool(preload_classifier)
            logger.info("Analyzer zero-shot classification model loaded successfully.")
        except Exception:
            logger.exception(
                "Analyzer zero-shot model preload failed; rule-fallback system remains active."
            )

    yield


app = FastAPI(
    title="ServiceDesk Radar — AI Core",
    version="1.0.0",
    description=(
        "Unified Persian-first IT ServiceDesk AI Core providing Natural Language "
        "Understanding (Analyzer) and Semantic Vector Intelligence (Infrastructure)."
    ),
    lifespan=lifespan,
)

# Include sub-routers for modular standalone access
app.include_router(analyzer_router)


# ==============================================================================
# Unified Composite Endpoint (Primary Backend Integration Target)
# ==============================================================================
@app.post(
    "/analyze",
    response_model=UnifiedAnalyzeResponse,
    summary="Unified Ticket Analysis (Analyzer + Infrastructure)",
    tags=["Unified AI"],
)
async def analyze_ticket_unified(payload: UnifiedAnalyzeRequest) -> UnifiedAnalyzeResponse:
    """
    Unified entrypoint for the Backend orchestrator:
      1. Performs Persian NLP analysis (Category, Intent, Urgency, Sentiment, Summary, Suggested Reply).
      2. Performs Semantic Infrastructure analysis (Similar Tickets, KB Retrieval, Incident Candidate & Dedup).
      3. Returns a single composite payload: `{ analysis, intelligence, meta }`.
    """
    t0 = time.perf_counter()

    # Step 1: Persian NLP Analysis (Analyzer)
    text = payload.to_analysis_text()
    analysis_dict: dict[str, Any] = await run_in_threadpool(
        analyze_ticket_analyzer,
        text,
        payload.ticket_id,
        debug=payload.debug,
    )

    # Step 2: Determine category for Infrastructure (Payload category overrides detected category)
    detected_category = payload.category or analysis_dict.get("category")
    if detected_category in ("unknown", "null", ""):
        detected_category = None

    # Step 3: Semantic Infrastructure Intelligence
    infra_request = InfrastructureRequest(
        ticket_id=payload.ticket_id or 1,
        title=payload.title,
        description=payload.description,
        category=detected_category,
        old_tickets=payload.old_tickets,
        open_incidents=payload.open_incidents,
    )
    infra_result: InfrastructureResult = run_infrastructure(infra_request)

    # Step 4: Metadata & Status Assembly
    total_latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    status = "completed"
    error = None
    if infra_result.error or analysis_dict.get("analysis_status") != "completed":
        if infra_result.error and analysis_dict.get("analysis_status") == "completed":
            status = "partial"
            error = infra_result.error
        else:
            status = "failed"
            error = analysis_dict.get("error") or infra_result.error

    meta = {
        "status": status,
        "embedding_model_version": infra_result.embedding_model_version,
        "analyzer_model_version": analysis_dict.get("analyzer_model_version")
        or analysis_dict.get("model_version")
        or "unknown",
        "latency_ms": total_latency_ms,
        "analyzed_at": utc_now_iso(),
        "error": error,
    }

    return UnifiedAnalyzeResponse(
        ticket_id=payload.ticket_id,
        status=status,
        analysis=analysis_dict,
        intelligence=infra_result,
        meta=meta,
    )


# ==============================================================================
# Standalone Infrastructure Endpoint (Backward Compatibility)
# ==============================================================================
@app.post(
    "/analyze-ticket",
    response_model=InfrastructureResult,
    summary="Analyze a ticket (infrastructure intelligence block only)",
    tags=["Infrastructure"],
)
def analyze_ticket_infra(payload: InfrastructureRequest) -> InfrastructureResult:
    """
    Return similar tickets, the most relevant article, and an incident
    candidate for the given ticket. Always HTTP 200; controlled failures are
    reported in the result's `error` field.
    """
    return run_infrastructure(payload)


# ==============================================================================
# Health Check Endpoint
# ==============================================================================
@app.get(
    "/health",
    summary="Comprehensive AI Core Readiness",
    tags=["System"],
)
def health_check(request: Request, response: Response) -> dict[str, Any]:
    """
    Report comprehensive readiness for both Infrastructure and Analyzer models.
    HTTP 200 when usable (ok/degraded), 503 when fatal config/model errors occur.
    """
    status: InfrastructureHealthStatus = getattr(
        request.app.state,
        "infra_health",
        None,
    )

    if status is None:
        response.status_code = 503
        return {
            "status": "error",
            "error_reason": "infrastructure_not_initialized",
            "model_loaded": False,
            "zero_shot_model_loaded": False,
        }

    response.status_code = 200 if status.status in ("ok", "degraded") else 503

    return {
        "status": status.status,
        "model_loaded": status.model_loaded,
        "model_version": status.model_version,
        "articles_indexed": status.articles_indexed,
        "tickets_in_pool": status.tickets_in_pool,
        "qdrant_available": status.qdrant_available,
        "qdrant_mode": status.qdrant_mode,
        "startup_latency_ms": status.startup_latency_ms,
        "error_reason": status.error_reason,
        "zero_shot_model_loaded": is_classifier_loaded(),
        "rule_fallback_available": True,
        "timestamp": utc_now_iso(),
    }
