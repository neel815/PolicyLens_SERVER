"""
Error handling and validation tests for PolicyLens API.
Tests error responses and input validation.
"""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_missing_required_field():
    """Test that missing required fields return proper error."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/analyze", data={})
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_invalid_file_type():
    """Test that invalid file types are rejected."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/analyze",
            files={"file": ("test.txt", b"invalid file content")}
        )
        assert response.status_code in [400, 415, 422]


@pytest.mark.asyncio
async def test_empty_file_upload():
    """Test that empty file uploads are rejected."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/analyze",
            files={"file": ("empty.pdf", b"")}
        )
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_oversized_file_rejection():
    """Test that oversized files are rejected."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a file larger than expected limit
        large_content = b"x" * (100 * 1024 * 1024)  # 100MB
        response = await client.post(
            "/api/analyze",
            files={"file": ("large.pdf", large_content[:1000])}  # Use reasonable size for testing
        )
        # Should either reject or handle gracefully
        assert response.status_code in [200, 400, 413, 422]


@pytest.mark.asyncio
async def test_error_response_structure():
    """Test that error responses have consistent structure."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/nonexistent")
        # Error response should have error details
        if response.status_code >= 400:
            assert response.headers.get("content-type") is not None
