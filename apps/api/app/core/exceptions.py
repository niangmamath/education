"""
StudentConnect API Exception Handlers

Custom exception classes and FastAPI exception handlers.
"""

from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


# Custom Exception Classes
class StudentConnectException(Exception):
    """Base exception for StudentConnect errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class NotFoundException(StudentConnectException):
    """Resource not found exception."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
        status_code: int = status.HTTP_404_NOT_FOUND,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, status_code, details)


class ValidationException(StudentConnectException):
    """Validation error exception."""
    
    def __init__(
        self,
        message: str = "Validation error",
        code: str = "VALIDATION_ERROR",
        status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, status_code, details)


class AuthenticationException(StudentConnectException):
    """Authentication error exception."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = "AUTHENTICATION_ERROR",
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, status_code, details)


class AuthorizationException(StudentConnectException):
    """Authorization error exception."""
    
    def __init__(
        self,
        message: str = "Permission denied",
        code: str = "AUTHORIZATION_ERROR",
        status_code: int = status.HTTP_403_FORBIDDEN,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, status_code, details)


class ConflictException(StudentConnectException):
    """Conflict error exception (e.g., duplicate resource)."""
    
    def __init__(
        self,
        message: str = "Conflict occurred",
        code: str = "CONFLICT",
        status_code: int = status.HTTP_409_CONFLICT,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, status_code, details)


class RateLimitException(StudentConnectException):
    """Rate limit exceeded exception."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        code: str = "RATE_LIMIT_EXCEEDED",
        status_code: int = status.HTTP_429_TOO_MANY_REQUESTS,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, status_code, details)


# Exception Handlers
def studentconnect_exception_handler(request: Request, exc: StudentConnectException) -> JSONResponse:
    """Handle StudentConnect custom exceptions."""
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


def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors."""
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
                "details": exc.errors(),
            },
        },
    )


def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic/unexpected exceptions."""
    logger.error(
        "Unexpected error",
        error=str(exc),
        type=type(exc).__name__,
        path=str(request.url),
        method=request.method,
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.DEBUG else {},
            },
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI application."""
    app.add_exception_handler(StudentConnectException, studentconnect_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
