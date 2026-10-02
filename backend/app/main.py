"""
CivixRecord-OS Civic Meeting Intelligence Platform
Production FastAPI Backend Application
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

from backend.app.core.config import settings
from backend.app.api.v1.endpoints import meetings, motions, streaming, bylaws
from backend.app.services.transcription_worker import TranscriptionWorker

# Configure application logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("civixrecord.app")

# Prometheus Metrics Definitions
HTTP_REQUESTS_TOTAL = Counter(
    "civix_http_requests_total",
    "Total HTTP requests handled by CivixRecord API",
    ["method", "endpoint", "status_code"],
)
AUDIO_CHUNKS_PROCESSED = Counter(
    "civix_audio_chunks_processed_total",
    "Total audio chunks processed by transcription engine",
)
ACTIVE_MEETING_SESSIONS = Counter(
    "civix_active_meetings_total",
    "Total meetings registered on CivixRecord",
)
PROCESSING_LATENCY = Histogram(
    "civix_audio_processing_latency_seconds",
    "Audio chunk processing latency in seconds",
)

# Shared background transcription worker instance
transcription_worker = TranscriptionWorker()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Initializes background transcription workers, audio queues, and IPC channels on startup,
    and performs graceful shutdown on exit.
    """
    logger.info("Initializing CivixRecord-OS backend services...")
    # Start background transcription worker
    await transcription_worker.start()
    logger.info("CivixRecord-OS transcription worker started.")
    
    yield
    
    logger.info("Shutting down CivixRecord-OS backend services...")
    # Graceful shutdown of transcription worker
    await transcription_worker.stop()
    logger.info("CivixRecord-OS shutdown complete.")


def create_app() -> FastAPI:
    """Factory creating and configuring the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Autonomous civic meeting recording, procedural motion parsing, and bylaw intelligence engine.",
        lifespan=lifespan,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API Routers
    app.include_router(
        meetings.router,
        prefix=f"{settings.API_V1_STR}/meetings",
        tags=["Meetings"],
    )
    app.include_router(
        motions.router,
        prefix=f"{settings.API_V1_STR}/motions",
        tags=["Motions"],
    )
    app.include_router(
        streaming.router,
        prefix=f"{settings.API_V1_STR}/streaming",
        tags=["Streaming"],
    )
    app.include_router(
        bylaws.router,
        prefix=f"{settings.API_V1_STR}/bylaws",
        tags=["Bylaws & Procedure"],
    )

    # Prometheus Metrics Endpoint
    @app.get("/metrics", tags=["Observability"])
    def prometheus_metrics() -> Response:
        """Exposes Prometheus application metrics for scraping."""
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST,
        )

    # Health & Readiness Probes
    @app.get("/healthz", tags=["Observability"])
    def health_check():
        """Liveness check probe."""
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "project": settings.PROJECT_NAME,
        }

    @app.get("/readyz", tags=["Observability"])
    def readiness_check():
        """Readiness check probe."""
        return {
            "status": "ready",
            "worker_running": transcription_worker.running,
        }

    return app


app = create_app()
