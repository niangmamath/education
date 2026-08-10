"""
StudentConnect API Logging Configuration

Structured logging with structlog and JSON formatter.
"""

import logging
import sys
from typing import Any, Dict

import structlog
from pythonjsonlogger import jsonlogger


def setup_logging() -> None:
    """Configure structured logging for the application."""
    # Get log level from environment or use INFO
    from app.core.config import settings
    
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configure standard library logging
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            format_log,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def format_log(logger: structlog.BoundLogger, log_method: str, event_dict: Dict[str, Any]) -> str:
    """Format log entry based on configuration."""
    from app.core.config import settings
    
    if settings.LOG_FORMAT == "json":
        # For JSON format, return event_dict as JSON string directly
        import json
        return json.dumps(event_dict)
    else:
        # Text format
        level = event_dict.get("level", "INFO")
        logger_name = event_dict.get("logger", "studentconnect")
        event = event_dict.get("event", "")
        
        # Format: LEVEL [logger] event [extra fields]
        log_line = f"{level.upper()} [{logger_name}] {event}"
        
        # Add extra fields (excluding standard ones)
        extra_fields = {k: v for k, v in event_dict.items() 
                      if k not in ("level", "logger", "event", "pathname", "lineno")}
        
        if extra_fields:
            extra = " ".join(f"{k}={v}" for k, v in extra_fields.items())
            log_line = f"{log_line} {extra}"
        
        return log_line


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a logger with the given name."""
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()
