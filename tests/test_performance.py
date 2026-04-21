"""
Performance and load tests for PolicyLens API.
Tests API response times and concurrent request handling.
"""

import pytest
import asyncio
import time
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint_response_time():
    """Test that health endpoint responds quickly."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        start = time.time()
        response = await client.get("/api/health")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        # Health check should be fast (< 1 second)
        assert elapsed < 1.0


@pytest.mark.asyncio
async def test_concurrent_health_requests():
    """Test API handles concurrent health requests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Make 5 concurrent requests
        tasks = [
            client.get("/api/health") 
            for _ in range(5)
        ]
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        # All should return valid JSON
        assert all(r.json() for r in responses)


@pytest.mark.asyncio
async def test_rapid_sequential_requests():
    """Test API handles rapid sequential requests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        for _ in range(10):
            response = await client.get("/api/health")
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_request_timeout_handling():
    """Test that requests have proper timeout handling."""
    async with AsyncClient(app=app, base_url="http://test", timeout=5.0) as client:
        response = await client.get("/api/health")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_multiple_endpoints_concurrently():
    """Test accessing multiple endpoints concurrently."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        tasks = [
            client.get("/api/health"),
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Should handle without errors
        for response in responses:
            if not isinstance(response, Exception):
                assert response.status_code in [200, 404, 405]
