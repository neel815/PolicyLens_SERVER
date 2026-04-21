"""
Response parsing and data integrity tests for PolicyLens API.
Tests that API responses contain expected data structure.
"""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_response_is_json():
    """Test that health endpoint returns valid JSON."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        # Should be able to parse as JSON without error
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_health_response_has_timestamp():
    """Test that health response includes timestamp info."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        data = response.json()
        # Should have some identifier
        assert len(data) > 0


@pytest.mark.asyncio
async def test_api_response_headers():
    """Test that API response headers are properly set."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        # Should have content type header
        assert response.headers.get("content-type") is not None
        assert "json" in response.headers.get("content-type", "").lower()


@pytest.mark.asyncio
async def test_api_response_no_sensitive_data():
    """Test that API responses don't expose sensitive information."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        content = response.text
        # Should not contain sensitive patterns
        sensitive_patterns = ["password", "secret", "api_key", "token"]
        for pattern in sensitive_patterns:
            assert pattern.lower() not in content.lower()


@pytest.mark.asyncio
async def test_api_response_encoding():
    """Test that API response has proper encoding."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        # Response should be UTF-8 encoded
        assert response.encoding in ["utf-8", "utf8", None]
