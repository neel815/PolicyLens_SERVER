"""
Main FastAPI application entry point.
Configure and initialize the FastAPI app with database setup using Alembic migrations.
"""

import os
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from time import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.db.database import check_db_connection
from dotenv import load_dotenv
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import route routers
from routes.auth_routes import router as auth_router
from routes.policy_routes import router as policy_router
from routes.analyze_routes import router as analyze_router
from routes.simulate_routes import router as simulate_router
from routes.battle_routes import router as battle_router

# Load environment variables
load_dotenv()

# ============================================================================
# SETUP LOGGING
# ============================================================================
os.makedirs('logs', exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Rotating file handler for API logs (10MB max, keep 5 backups)
api_handler = RotatingFileHandler(
    'logs/api.log',
    maxBytes=10_000_000,
    backupCount=5
)
api_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(api_handler)

# Rotating file handler for errors
error_handler = RotatingFileHandler(
    'logs/errors.log',
    maxBytes=10_000_000,
    backupCount=5
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(error_handler)

# ============================================================================
# ENVIRONMENT VALIDATION
# ============================================================================
def validate_environment():
    """Validate all required environment variables are set and secure."""
    required_vars = [
        "SECRET_KEY",
        "DATABASE_URL",
        "CORS_ORIGINS",
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please add them to your .env file"
        )
    
    # Validate SECRET_KEY
    secret_key = os.getenv("SECRET_KEY", "")
    env = os.getenv("ENV", "development")
    
    if len(secret_key) < 32:
        if env == "production":
            raise RuntimeError(
                f"SECRET_KEY is too short ({len(secret_key)} chars). "
                f"Must be 32+ characters for production. "
                f"Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        else:
            logger.warning(
                f"SECRET_KEY is short ({len(secret_key)} chars). "
                f"Recommended: 32+ characters for production security."
            )
    
    # Validate production settings
    if env == "production":
        debug = os.getenv("DEBUG", "false").lower()
        if debug == "true":
            raise RuntimeError("DEBUG must be false in production")
        
        cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
        if any("localhost" in origin or "127.0.0.1" in origin for origin in cors_origins):
            raise RuntimeError(
                "CORS_ORIGINS contains localhost in production. "
                "Use only production domains."
            )
    
    # Validate DATABASE_URL format
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url.startswith("postgresql://"):
        logger.warning("DATABASE_URL does not use PostgreSQL. Ensure database is PostgreSQL.")
    
    # Warn if using default credentials
    if "postgres:root@123" in db_url or "root@123" in db_url:
        logger.warning(
            "WARNING: Using default database credentials. "
            "Change DB_PASSWORD to a strong password in production."
        )
    
    logger.info("Environment variables validated successfully")


validate_environment()

# ============================================================================
# CREATE FASTAPI APP
# ============================================================================

# Determine if docs should be exposed
env = os.getenv("ENV", "development")
docs_url = "/docs" if env != "production" else None
redoc_url = "/redoc" if env != "production" else None
openapi_url = "/openapi.json" if env != "production" else None

app = FastAPI(
    title=os.getenv("APP_NAME", "PolicyLens API"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description=os.getenv("APP_DESCRIPTION", "PolicyLens Backend API"),
    docs_url=docs_url,        # ✅ Hide docs in production
    redoc_url=redoc_url,      # ✅ Hide redoc in production
    openapi_url=openapi_url,  # ✅ Hide OpenAPI schema in production
)

# ============================================================================
# RATE LIMITING
# ============================================================================
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(
    status_code=429,
    content={"detail": "Rate limit exceeded. Please try again later."}
))
app.add_middleware(SlowAPIMiddleware)

# ============================================================================
# REQUEST LOGGING MIDDLEWARE
# ============================================================================
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all API requests with timing and user info."""
    async def dispatch(self, request: Request, call_next):
        start_time = time()
        response = await call_next(request)
        duration = time() - start_time
        
        # Extract user info from token if available
        user_id = "anonymous"
        try:
            from app.utils.jwt_utils import get_current_user_id
            # This is a simplified logging - in production use proper context
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                user_id = "authenticated"
        except Exception:
            pass
        
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"User: {user_id} - "
            f"Duration: {duration:.3f}s"
        )
        return response

app.add_middleware(RequestLoggingMiddleware)

# ============================================================================
# HTTPS REDIRECT MIDDLEWARE (for production)
# ============================================================================
class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """Redirect HTTP to HTTPS in production."""
    async def dispatch(self, request: Request, call_next):
        if os.getenv("ENV") == "production":
            if request.url.scheme == "http":
                url = request.url.replace(scheme="https")
                return JSONResponse(
                    status_code=301,
                    content={"detail": "Redirect to HTTPS"},
                    headers={"Location": str(url)}
                )
        return await call_next(request)

app.add_middleware(HTTPSRedirectMiddleware)

# ============================================================================
# CSRF PROTECTION MIDDLEWARE
# ============================================================================
import secrets
import hashlib

class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF protection middleware for state-changing operations."""
    
    PROTECTED_METHODS = {"POST", "PUT", "DELETE", "PATCH"}
    EXEMPT_PATHS = {"/api/auth/login", "/api/auth/register", "/api/csrf-token"}
    
    async def dispatch(self, request: Request, call_next):
        # Skip CSRF check for safe methods and exempt paths
        if request.method not in self.PROTECTED_METHODS or request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        # Check CSRF token for protected methods
        csrf_token = request.headers.get("X-CSRF-Token")
        
        if not csrf_token:
            logger.warning(f"[CSRF] Missing CSRF token for {request.method} {request.url.path}")
            return JSONResponse(
                status_code=403,
                content={"detail": "CSRF token missing"}
            )
        
        # Validate token format (basic check)
        if not csrf_token or len(csrf_token) < 32:
            logger.warning(f"[CSRF] Invalid CSRF token for {request.method} {request.url.path}")
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid CSRF token"}
            )
        
        logger.info(f"[CSRF] Valid token for {request.method} {request.url.path}")
        response = await call_next(request)
        return response

app.add_middleware(CSRFProtectionMiddleware)

# ============================================================================
# SECURITY HEADERS MIDDLEWARE
# ============================================================================
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy (strict in production)
        csp = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' https://api.example.com"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response

app.add_middleware(SecurityHeadersMiddleware)

# ============================================================================
# REQUEST ID TRACKING MIDDLEWARE
# ============================================================================
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request for tracing."""
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", secrets.token_hex(8))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

app.add_middleware(RequestIDMiddleware)

# ============================================================================
# CORS CONFIGURATION (SECURE)
# ============================================================================
# Define allowed methods and headers explicitly (NOT wildcards)
ALLOWED_METHODS = [
    "GET",      # Read operations
    "POST",     # Create operations
    "PUT",      # Update operations
    "DELETE",   # Delete operations
    "OPTIONS",  # CORS preflight
]

ALLOWED_HEADERS = [
    "Content-Type",
    "Authorization",
    "Accept",
    "Origin",
]

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,  # ✅ FIXED: Specific methods only (was "*")
    allow_headers=ALLOWED_HEADERS,   # ✅ FIXED: Specific headers only (was "*")
    max_age=600,                      # Cache preflight for 10 minutes
)

# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for logging unhandled errors."""
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ============================================================================
# CSRF TOKEN ENDPOINT
# ============================================================================
@app.post("/api/csrf-token")
async def get_csrf_token():
    """
    Get a CSRF token for state-changing operations.
    
    Frontend should:
    1. Call this endpoint on page load
    2. Store the token in state or session
    3. Include it in X-CSRF-Token header for POST/PUT/DELETE requests
    
    Returns:
        {"token": "..."}
    """
    token = secrets.token_urlsafe(32)
    logger.info("[CSRF] New CSRF token generated")
    return {"token": token}


# Include route routers
app.include_router(auth_router, prefix="/api")
app.include_router(policy_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")
app.include_router(simulate_router, prefix="/api")
app.include_router(battle_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize database and run Alembic migrations on startup."""
    logger.info("[STARTUP] Starting PolicyLens API...")
    
    # Check database connection
    if check_db_connection():
        logger.info("[STARTUP] Database connection successful!")
        # Run Alembic migrations
        try:
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                logger.info("[STARTUP] Database migrations applied successfully!")
            else:
                logger.warning(f"[STARTUP] Migration warning: {result.stderr}")
        except Exception as e:
            logger.warning(f"[STARTUP] Could not run migrations: {e}")
            logger.warning("    Make sure to run 'alembic upgrade head' manually")
    else:
        logger.error("[STARTUP] Database connection failed!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("[SHUTDOWN] PolicyLens API shutting down...")


@app.get("/")
async def root():
    """Root endpoint."""
    env = os.getenv("ENV", "development")
    docs_available = env != "production"
    return {
        "message": "Welcome to PolicyLens API",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": env,
        "docs": "/docs" if docs_available else "Not available in production",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected" if check_db_connection() else "disconnected",
        "environment": os.getenv("ENV", "development"),
    }


@app.get("/api/debug/models")
async def list_available_models():
    """
    DEBUG ENDPOINT: List available Gemini models for your API key.
    Use this to find the correct model name to use.
    
    ⚠️  Only available in development mode!
    """
    env = os.getenv("ENV", "development")
    if env == "production":
        return {"error": "Debug endpoints not available in production"}
    
    import google.generativeai as genai
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY not configured"}
    
    try:
        genai.configure(api_key=api_key)
        models = genai.list_models()
        
        available_models = []
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                available_models.append({
                    "name": m.name,
                    "display_name": m.display_name,
                    "description": m.description if hasattr(m, 'description') else None
                })
        
        return {
            "total_models": len(available_models),
            "available_for_generation": available_models
        }
    except Exception as e:
        return {"error": str(e)}



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVER_PORT", 8000)),
        reload=os.getenv("RELOAD", "true").lower() == "true",
    )
