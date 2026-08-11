"""Custom middleware components for StudentConnect."""

from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable
from contextvars import ContextVar

import structlog
from fastapi import FastAPI, Request, Response

logger = structlog.get_logger(__name__)

trace_id_var: ContextVar[str] = ContextVar(
    "trace_id",
    default="",
)


class TraceIDMiddleware:
    """Add a trace identifier to each HTTP request."""

    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        trace_id = request.headers.get(
            "x-trace-id",
            str(uuid.uuid4()),
        )

        token = trace_id_var.set(trace_id)
        request.state.trace_id = trace_id

        try:
            response = await call_next(request)
            response.headers["x-trace-id"] = trace_id
            return response
        finally:
            trace_id_var.reset(token)


class RequestIDMiddleware:
    """Add a unique request identifier to each request."""

    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response


class LoggingMiddleware:
    """Log HTTP requests and responses."""

    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start_time = time.perf_counter()

        logger.info(
            "Request started",
            method=request.method,
            path=str(request.url),
            query_params=dict(request.query_params),
            request_id=getattr(
                request.state,
                "request_id",
                "",
            ),
            trace_id=getattr(
                request.state,
                "trace_id",
                "",
            ),
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            duration = time.perf_counter() - start_time

            logger.exception(
                "Request failed",
                method=request.method,
                path=str(request.url),
                error=str(exc),
                duration=f"{duration:.4f}s",
                request_id=getattr(
                    request.state,
                    "request_id",
                    "",
                ),
                trace_id=getattr(
                    request.state,
                    "trace_id",
                    "",
                ),
            )
            raise

        duration = time.perf_counter() - start_time

        logger.info(
            "Request completed",
            method=request.method,
            path=str(request.url),
            status_code=response.status_code,
            duration=f"{duration:.4f}s",
            request_id=getattr(
                request.state,
                "request_id",
                "",
            ),
            trace_id=getattr(
                request.state,
                "trace_id",
                "",
            ),
        )

        return response


def setup_middleware(app: FastAPI) -> None:
    """Register application middleware."""
    app.middleware("http")(TraceIDMiddleware())
    app.middleware("http")(RequestIDMiddleware())
    app.middleware("http")(LoggingMiddleware())
