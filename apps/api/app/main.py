"""
StudentConnect API - Main Application Entry Point

FastAPI modular monolith application for StudentConnect backend.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import dispose_engine
from app.core.exceptions import setup_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import setup_middleware
from app.api.v1 import internal
from app.core.routing import api_router

# Setup logging before application starts
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting StudentConnect API", version=settings.API_VERSION)
    logger.info("Environment", env=settings.ENVIRONMENT)

    yield

    # Shutdown. Returning the pooled connections while the loop is still running
    # is what keeps asyncpg from being left with sockets bound to a dead loop.
    await dispose_engine()
    logger.info("Shutting down StudentConnect API")


# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url=f"{settings.API_DOCS_URL}/docs",
    redoc_url=f"{settings.API_DOCS_URL}/redoc",
    openapi_url=f"{settings.API_DOCS_URL}/openapi.json",
    lifespan=lifespan,
)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Setup custom middleware
setup_middleware(app)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Unprefixed: the content origin's nginx proxies `/t/<ticket>/…` unchanged to
# these routes, so they live at that same path rather than under
# API_V1_PREFIX. See app/api/v1/internal.py and app/core/routing.py.
app.include_router(internal.router, tags=["internal"])


# Health check endpoints (outside of versioned API)
@app.get("/health/live")
async def health_live() -> dict[str, str]:
    """
    Liveness probe endpoint.

    Returns a simple response to indicate the server is running.
    This endpoint does not check external dependencies.
    """
    return {"status": "live"}


@app.get("/health/ready")
async def health_ready() -> dict[str, str]:
    """
    Readiness probe endpoint.

    Returns a response to indicate the server is ready to receive traffic.
    This endpoint should check external dependencies in production.
    """
    # In production, this would check database, Redis, etc.
    # For now, just return ready since we don't have external dependencies in dev
    return {"status": "ready"}


# Root endpoint
@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint returning API information."""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "docs": f"{settings.API_DOCS_URL}/docs",
    }


# Request logging middleware for debugging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log HTTP requests for debugging purposes."""
    logger.debug(
        "Request started",
        method=request.method,
        path=request.url.path,
        query_params=dict(request.query_params),
    )

    response = await call_next(request)

    logger.debug(
        "Request completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )

    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.ENVIRONMENT == "development",
        log_config=None,  # We use structlog
    )
