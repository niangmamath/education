"""
StudentConnect API Health Check Tests

Tests for health check endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


# Create test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_live_endpoint(self):
        """Test the liveness probe endpoint."""
        response = client.get("/health/live")

        assert response.status_code == 200
        assert response.json() == {"status": "live"}

    def test_ready_endpoint(self):
        """Test the readiness probe endpoint."""
        response = client.get("/health/ready")

        assert response.status_code == 200
        assert response.json() == {"status": "ready"}

    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


class TestOpenAPI:
    """Test OpenAPI documentation endpoints."""

    def test_openapi_json(self):
        """Test OpenAPI JSON endpoint."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_docs_endpoint(self):
        """Test Swagger UI docs endpoint."""
        response = client.get("/docs")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


class TestResponseHeaders:
    """Test response headers for trace_id and request_id."""

    def test_trace_id_header(self):
        """Test that trace_id is present in response headers."""
        response = client.get("/health/live")

        assert response.status_code == 200
        assert "x-trace-id" in response.headers
        assert len(response.headers["x-trace-id"]) > 0

    def test_request_id_header(self):
        """Test that request_id is present in response headers."""
        response = client.get("/health/live")

        assert response.status_code == 200
        assert "x-request-id" in response.headers
        assert len(response.headers["x-request-id"]) > 0


class TestCORS:
    """Test CORS configuration."""

    def test_cors_simple_request_from_allowed_origin(self):
        """An allowed browser origin receives CORS headers."""
        response = client.get(
            "/health/live",
            headers={"Origin": "http://localhost:3000"},
        )

        assert response.status_code == 200
        assert (
            response.headers.get("access-control-allow-origin")
            == "http://localhost:3000"
        )
        assert response.headers.get("access-control-allow-credentials") == "true"

    def test_cors_preflight_from_allowed_origin(self):
        """An allowed browser preflight request succeeds."""
        response = client.options(
            "/health/live",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert (
            response.headers.get("access-control-allow-origin")
            == "http://localhost:3000"
        )
        assert "GET" in response.headers.get(
            "access-control-allow-methods",
            "",
        )

    def test_cors_does_not_authorize_unknown_origin(self):
        """An unknown browser origin is not authorized."""
        response = client.get(
            "/health/live",
            headers={"Origin": "https://example.invalid"},
        )

        assert response.status_code == 200
        assert (
            response.headers.get("access-control-allow-origin")
            != "https://example.invalid"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
