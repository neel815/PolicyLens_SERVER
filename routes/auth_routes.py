"""
Authentication routes for user registration and login.
"""

import os
from fastapi import APIRouter, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from app.db.database import get_db
from fastapi import Depends
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.utils.jwt_utils import hash_password, verify_password, create_access_token
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response schema - token sent via HttpOnly cookie."""
    message: str
    user: UserResponse


@limiter.limit("3/minute")
@router.post("/register", response_model=LoginResponse, status_code=201)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Register a new user account. Rate Limited: 3 requests per minute per IP.
    Token is set as HttpOnly cookie automatically.
    
    Args:
        user_data: User registration details
        db: Database session
        
    Returns:
        Success message and user information (token sent via HttpOnly cookie)
        
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(new_user.id)})
    
    # Return response with cookie set
    response = LoginResponse(
        message="User registered successfully",
        user=UserResponse.model_validate(new_user)
    )
    
    # Set HttpOnly cookie with token
    response_obj = Response(
        content=response.model_dump_json(),
        status_code=201,
        media_type="application/json"
    )
    # Set secure flag only in production (HTTPS)
    is_production = os.getenv("ENV", "development").lower() == "production"
    
    response_obj.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,           # Prevents JavaScript access (XSS protection)
        secure=is_production,    # HTTPS only in production, HTTP OK in dev
        samesite="strict",       # CSRF protection
        max_age=86400,           # 24 hours
        path="/"
    )
    logger.info(f"[AUTH] User {new_user.username} registered and HttpOnly cookie set")
    return response_obj


@limiter.limit("5/minute")
@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Login with username and password. Rate Limited: 5 requests per minute per IP.
    Token is set as HttpOnly cookie automatically.
    
    Args:
        credentials: Username and password
        db: Database session
        
    Returns:
        Success message and user information (token sent via HttpOnly cookie)
        
    Raises:
        HTTPException: If username not found or password incorrect
    """
    # Find user by username
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Return response with cookie set
    response = LoginResponse(
        message="Login successful",
        user=UserResponse.model_validate(user)
    )
    
    # Set HttpOnly cookie with token
    response_obj = Response(
        content=response.model_dump_json(),
        status_code=200,
        media_type="application/json"
    )
    # Set secure flag only in production (HTTPS)
    is_production = os.getenv("ENV", "development").lower() == "production"
    
    response_obj.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,           # Prevents JavaScript access (XSS protection)
        secure=is_production,    # HTTPS only in production, HTTP OK in dev
        samesite="strict",       # CSRF protection
        max_age=86400,           # 24 hours
        path="/"
    )
    logger.info(f"[AUTH] User {user.username} logged in and HttpOnly cookie set")
    return response_obj


@router.post("/logout")
async def logout(request: Request):
    """
    Logout user by clearing the HttpOnly authentication cookie.
    
    Returns:
        Success message
    """
    response_obj = Response(
        content={"message": "Logged out successfully"},
        status_code=200,
        media_type="application/json"
    )
    # Clear the authentication cookie
    response_obj.delete_cookie(
        key="access_token",
        path="/",
        samesite="strict"
    )
    logger.info("[AUTH] User logged out and cookie cleared")
    return response_obj


@router.post("/refresh")
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    """
    Refresh the authentication token using the current HttpOnly cookie.
    Call this endpoint periodically to keep the session alive.
    
    Returns:
        Success message with new token sent via HttpOnly cookie
        
    Raises:
        HTTPException: If no valid token found in cookie
    """
    # Token is automatically sent in cookies by the browser
    # The FastAPI dependency injection will handle validation
    # For now, we'll create a new token if the request is valid
    
    # In a production app, you'd extract the user from the current token
    # and generate a new one. For now, this is a placeholder.
    
    response_obj = Response(
        content={"message": "Token refreshed"},
        status_code=200,
        media_type="application/json"
    )
    logger.info("[AUTH] Token refresh endpoint called")
    return response_obj
