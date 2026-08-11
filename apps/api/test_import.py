#!/usr/bin/env python
"""Test script to verify API can be imported."""

import sys

try:
    from app.main import app

    print("[OK] API loaded successfully")
    print(f"[OK] Title: {app.title}")
    print(f"[OK] Version: {app.version}")
    print(f"[OK] Docs URL: {app.docs_url}")

    # List routes
    routes = [route.path for route in app.routes if hasattr(route, "path")]
    print(f"[OK] Routes: {routes}")

    sys.exit(0)
except Exception as e:
    print(f"[ERROR] Error loading API: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
