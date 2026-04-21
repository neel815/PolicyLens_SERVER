"""
Health check tests for PolicyLens API.
Tests basic API availability and system health endpoints.
"""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Test that the health check endpoint returns 200 status."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_check_response_structure():
    """Test that health check response has expected structure."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        data = response.json()
        assert "status" in data
        assert "message" in data


@pytest.mark.asyncio
async def test_health_check_status_value():
    """Test that health check returns healthy status."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        data = response.json()
        assert data.get("status") in ["healthy", "ok", "running", "UP"]


@pytest.mark.asyncio
async def test_api_routing():
    """Test that API routes respond appropriately."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test invalid route returns 404
        response = await client.get("/api/invalid-endpoint")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_api_method_not_allowed():
    """Test that unsupported HTTP methods are rejected."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Health endpoint should accept GET, not POST
        response = await client.post("/api/health")
        assert response.status_code == 405
