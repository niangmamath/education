"""Custom exceptions and handlers for StudentConnect."""

from __future__ import annotations

from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings

logger = structlog.get_logger(__name__)


class StudentConnectException(Exception):
    """Base exception for StudentConnect errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class NotFoundException(StudentConnectException):
    """Resource not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
        status_code: int = status.HTTP_404_NOT_FOUND,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message,
            code,
            status_code,
            details,
        )


class ValidationException(StudentConnectException):
    """Business validation failure."""

    def __init__(
        self,
        message: str = "Validation error",
        code: str = "VALIDATION_ERROR",
        status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message,
            code,
            status_code,
            details,
        )


class AuthenticationException(StudentConnectException):
    """Authentication failure."""

    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = "AUTHENTICATION_ERROR",
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message,
            code,
            status_code,
            details,
        )


class AuthorizationException(StudentConnectException):
    """Authorization failure."""

    def __init__(
        self,
        message: str = "Permission denied",
        code: str = "AUTHORIZATION_ERROR",
        status_code: int = status.HTTP_403_FORBIDDEN,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message,
            code,
            status_code,
            details,
        )


class ConflictException(StudentConnectException):
    """Resource conflict."""

    def __init__(
        self,
        message: str = "Conflict occurred",
        code: str = "CONFLICT",
        status_code: int = status.HTTP_409_CONFLICT,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message,
            code,
            status_code,
            details,
        )


class RateLimitException(StudentConnectException):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        code: str = "RATE_LIMIT_EXCEEDED",
        status_code: int = status.HTTP_429_TOO_MANY_REQUESTS,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message,
            code,
            status_code,
            details,
        )


def studentconnect_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle StudentConnect exceptions."""
    if not isinstance(exc, StudentConnectException):
        return generic_exception_handler(request, exc)

    logger.error(
        "StudentConnect exception",
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
        path=str(request.url),
        method=request.method,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


def validation_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle request validation errors."""
    if not isinstance(exc, RequestValidationError):
        return generic_exception_handler(request, exc)

    logger.warning(
        "Validation error",
        errors=exc.errors(),
        path=str(request.url),
        method=request.method,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation error",
                # A field validator raising ValueError puts that exception object
                # in the error context, which plain JSON cannot render; without
                # the encoder the response collapses into a 500.
                "details": jsonable_encoder(exc.errors()),
            },
        },
    )


def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.exception(
        "Unexpected error",
        error=str(exc),
        exception_type=type(exc).__name__,
        path=str(request.url),
        method=request.method,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": ({"exception": str(exc)} if settings.DEBUG else {}),
            },
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register the application exception handlers."""
    app.add_exception_handler(
        StudentConnectException,
        studentconnect_exception_handler,
    )
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )
    app.add_exception_handler(
        Exception,
        generic_exception_handler,
    )
