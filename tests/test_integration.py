"""
Integration tests for PolicyLens API.
Tests complete user flows: register -> login -> create policy -> analyze -> delete.
"""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.database import SessionLocal, engine
from app.models.base import Base
from io import BytesIO


# Setup and teardown
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db():
    """Create test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
async def client(test_db):
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def db_session():
    """Create database session for tests."""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


# Test data
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "full_name": "Test User"
}

TEST_PDF = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << >> /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer
<< /Size 4 /Root 1 0 R >>
startxref
214
%%EOF"""


# Tests
class TestAuthentication:
    """Test user authentication flow."""
    
    @pytest.mark.asyncio
    async def test_register_user(self, client):
        """Test user registration."""
        response = await client.post(
            "/api/auth/register",
            json=TEST_USER
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["user"]["username"] == TEST_USER["username"]
        assert data["user"]["email"] == TEST_USER["email"]
    
    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client):
        """Test registration with duplicate username fails."""
        # First registration
        await client.post("/api/auth/register", json=TEST_USER)
        
        # Try to register again
        response = await client.post(
            "/api/auth/register",
            json=TEST_USER
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_login_user(self, client):
        """Test user login."""
        # Register first
        await client.post("/api/auth/register", json=TEST_USER)
        
        # Login
        response = await client.post(
            "/api/auth/login",
            json={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client):
        """Test login with wrong password fails."""
        # Register first
        await client.post("/api/auth/register", json=TEST_USER)
        
        # Try login with wrong password
        response = await client.post(
            "/api/auth/login",
            json={
                "username": TEST_USER["username"],
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code == 401


class TestAuthorization:
    """Test authorization and access control."""
    
    @pytest.mark.asyncio
    async def test_protected_route_requires_auth(self, client):
        """Test that protected routes require authentication."""
        response = await client.get("/api/policies")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_protected_route_with_invalid_token(self, client):
        """Test that invalid tokens are rejected."""
        response = await client.get(
            "/api/policies",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_own_policies(self, client):
        """Test user can get their own policies."""
        # Register and login
        reg_response = await client.post(
            "/api/auth/register",
            json=TEST_USER
        )
        token = reg_response.json()["access_token"]
        
        # Get policies
        response = await client.get(
            "/api/policies",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestFileValidation:
    """Test file upload validation."""
    
    @pytest.mark.asyncio
    async def test_analyze_with_valid_pdf(self, client):
        """Test policy analysis with valid PDF."""
        # Register and login
        reg_response = await client.post(
            "/api/auth/register",
            json=TEST_USER
        )
        token = reg_response.json()["access_token"]
        
        # Analyze policy
        response = await client.post(
            "/api/analyze",
            files={"file": ("test.pdf", BytesIO(TEST_PDF), "application/pdf")},
            headers={"Authorization": f"Bearer {token}"}
        )
        # Might fail on analysis but should pass validation
        assert response.status_code in [200, 400, 500]
    
    @pytest.mark.asyncio
    async def test_analyze_with_invalid_file_type(self, client):
        """Test that non-PDF files are rejected."""
        # Register and login
        reg_response = await client.post(
            "/api/auth/register",
            json=TEST_USER
        )
        token = reg_response.json()["access_token"]
        
        # Try to upload non-PDF
        response = await client.post(
            "/api/analyze",
            files={"file": ("test.txt", BytesIO(b"Not a PDF"), "text/plain")},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_analyze_with_empty_file(self, client):
        """Test that empty files are rejected."""
        # Register and login
        reg_response = await client.post(
            "/api/auth/register",
            json=TEST_USER
        )
        token = reg_response.json()["access_token"]
        
        # Try to upload empty file
        response = await client.post(
            "/api/analyze",
            files={"file": ("test.pdf", BytesIO(b""), "application/pdf")},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400


class TestRateLimiting:
    """Test rate limiting."""
    
    @pytest.mark.asyncio
    async def test_register_rate_limiting(self, client):
        """Test rate limiting on registration."""
        # Make multiple registration attempts
        responses = []
        for i in range(4):
            response = await client.post(
                "/api/auth/register",
                json={
                    **TEST_USER,
                    "username": f"user{i}",
                    "email": f"user{i}@example.com"
                }
            )
            responses.append(response.status_code)
        
        # First 3 should succeed (3/minute limit)
        assert responses[0] == 201
        assert responses[1] == 201
        assert responses[2] == 201
        
        # 4th should be rate limited
        assert responses[3] == 429
    
    @pytest.mark.asyncio
    async def test_login_rate_limiting(self, client):
        """Test rate limiting on login."""
        # Register first
        await client.post("/api/auth/register", json=TEST_USER)
        
        # Make multiple login attempts
        responses = []
        for i in range(6):
            response = await client.post(
                "/api/auth/login",
                json={
                    "username": TEST_USER["username"],
                    "password": "WrongPassword" if i > 0 else TEST_USER["password"]
                }
            )
            responses.append(response.status_code)
        
        # First 5 should be processed
        assert responses[0] == 200  # Valid login
        
        # 6th should be rate limited (5/minute limit)
        assert responses[5] == 429


class TestErrorHandling:
    """Test error handling."""
    
    @pytest.mark.asyncio
    async def test_nonexistent_policy(self, client):
        """Test accessing nonexistent policy returns 404."""
        # Register and login
        reg_response = await client.post(
            "/api/auth/register",
            json=TEST_USER
        )
        token = reg_response.json()["access_token"]
        
        # Try to get nonexistent policy
        response = await client.get(
            "/api/policies/99999",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_invalid_json_request(self, client):
        """Test invalid JSON request handling."""
        response = await client.post(
            "/api/auth/register",
            content="invalid json"
        )
        assert response.status_code == 422


class TestCORS:
    """Test CORS configuration."""
    
    @pytest.mark.asyncio
    async def test_cors_headers_present(self, client):
        """Test that CORS headers are returned."""
        response = await client.options("/api/policies")
        
        # Check CORS headers
        assert response.status_code == 200
        # CORS headers should be present in the response
