import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestMainApp:
    """Test main application functionality."""

    def test_app_creation(self):
        """Test that the FastAPI app is created correctly."""
        assert app.title == "Sales Call Analytics API"
        assert app.version == "1.0.0"
        assert "microservice" in app.description

    def test_middleware_setup(self):
        """Test that CORS middleware is properly configured."""
        # Check if CORS middleware is in the middleware stack
        middleware_classes = [
            middleware.cls.__name__ for middleware in app.user_middleware
        ]
        assert "CORSMiddleware" in middleware_classes

    def test_router_inclusion(self):
        """Test that API router is included."""
        # Check if our API routes are included
        route_paths = [route.path for route in app.routes]
        assert "/api/v1/calls" in route_paths
        assert "/api/v1/analytics/agents" in route_paths

    def test_lifespan_events(self):
        """Test that lifespan events are configured."""
        assert app.router.lifespan_context is not None
