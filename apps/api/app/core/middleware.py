"""
StudentConnect API Middleware

Custom middleware components for FastAPI.
"""

import time
from typing import Callable, Awaitable
import uuid

from fastapi import FastAPI, Request, Response
import structlog

logger = structlog.get_logger(__name__)


# Context variable for trace_id
from contextvars import ContextVar

trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")


class TraceIDMiddleware:
    """Middleware to add trace_id to each request for distributed tracing."""
    
    async def __call__(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Generate or get trace_id
        trace_id = request.headers.get("x-trace-id", str(uuid.uuid4()))
        
        # Save old context
        old_token = trace_id_var.get()
        
        try:
            # Set trace_id in context
            trace_id_var.set(trace_id)
            
            # Add trace_id to request state
            request.state.trace_id = trace_id
            
            # Process request
            response = await call_next(request)
            
            # Add trace_id to response headers
            response.headers["x-trace-id"] = trace_id
            
            return response
        finally:
            # Reset context
            if old_token is not None:
                trace_id_var.set(old_token)
            else:
                trace_id_var.reset()


class RequestIDMiddleware:
    """Middleware to add unique request ID to each request."""
    
    async def __call__(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        
        return response


class LoggingMiddleware:
    """Middleware for structured request/response logging."""
    
    async def __call__(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start_time = time.time()
        
        # Log request start
        logger.info(
            "Request started",
            method=request.method,
            path=str(request.url),
            query_params=dict(request.query_params),
            request_id=getattr(request.state, "request_id", ""),
            trace_id=getattr(request.state, "trace_id", ""),
        )
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log request completion
            logger.info(
                "Request completed",
                method=request.method,
                path=str(request.url),
                status_code=response.status_code,
                duration=f"{duration:.4f}s",
                request_id=getattr(request.state, "request_id", ""),
                trace_id=getattr(request.state, "trace_id", ""),
            )
            
            return response
        except Exception as exc:
            duration = time.time() - start_time
            
            # Log request failure
            logger.error(
                "Request failed",
                method=request.method,
                path=str(request.url),
                error=str(exc),
                duration=f"{duration:.4f}s",
                request_id=getattr(request.state, "request_id", ""),
                trace_id=getattr(request.state, "trace_id", ""),
                exc_info=True,
            )
            
            raise


def setup_middleware(app: FastAPI) -> None:
    """Register all middleware with the FastAPI application."""
    app.middleware("http")(TraceIDMiddleware())
    app.middleware("http")(RequestIDMiddleware())
    app.middleware("http")(LoggingMiddleware())
