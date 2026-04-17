"""
JWT token utilities for authentication.
"""

import os
import bcrypt
import logging
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer

# Setup logging
logger = logging.getLogger(__name__)

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY")
# Allow app to start even without SECRET_KEY, but it will fail when authentication is used
if not SECRET_KEY:
    logger.warning(
        "⚠️  SECRET_KEY not set! Authentication will not work. "
        "Set SECRET_KEY in environment variables."
    )
    SECRET_KEY = "default-insecure-key-for-development-only"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary with token claims (should include 'sub' for user_id)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user_id(request: Request) -> int:
    """
    Dependency to extract and validate JWT token, returning user_id.
    Supports both HttpOnly cookies and Authorization header.
    
    Priority:
    1. Check for token in 'access_token' HttpOnly cookie
    2. Fall back to Authorization: Bearer <token> header
    
    Args:
        request: FastAPI request object to access cookies and headers
        
    Returns:
        user_id from token claims
        
    Raises:
        HTTPException: If token is invalid, expired, or missing
    """
    token = None
    
    # Try to get token from HttpOnly cookie first
    token = request.cookies.get("access_token")
    if token:
        logger.debug(f"[AUTH] Token found in HttpOnly cookie")
    else:
        logger.debug(f"[AUTH] No token in HttpOnly cookie. Available cookies: {list(request.cookies.keys())}")
    
    # Fall back to Authorization header if no cookie
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
            logger.debug(f"[AUTH] Token found in Authorization header")
        else:
            logger.debug(f"[AUTH] No Authorization header found")
    
    if not token:
        logger.warning(f"[AUTH] Authentication failed: No token found in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning(f"[AUTH] Token missing user ID claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.debug(f"[AUTH] User {user_id} authenticated successfully")
        return int(user_id)
    except JWTError as e:
        logger.warning(f"[AUTH] JWT validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
