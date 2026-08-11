"""Compatibility entry point for StudentConnect API.

The canonical FastAPI application is defined in app.main.
"""

from app.main import app

__all__ = ["app"]
