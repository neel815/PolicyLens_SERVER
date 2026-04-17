"""
Database configuration and connection management for FastAPI backend.
Handles PostgreSQL connection pool and SQLAlchemy session management.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:root%40123@127.0.0.1:5432/policylens"
)

DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 5))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 10))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", 30))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", 3600))

# SQLAlchemy engine configuration
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    pool_recycle=DB_POOL_RECYCLE,
    echo=os.getenv("DEBUG", "false").lower() == "true",
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency function to get database session.
    Usage in FastAPI routes:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database session.
    Usage:
        with get_db_context() as db:
            users = db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database and create all tables."""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all tables from database. Use with caution!"""
    Base.metadata.drop_all(bind=engine)


def check_db_connection():
    """Test database connection."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


# Import all models AFTER Base is created to register them
# Avoid circular imports by importing at the end
from app.models.base import BaseModel
from app.models.user import User
from app.models.policy import Policy
from app.models.claim_simulation import ClaimSimulation

__all__ = ["Base", "engine", "SessionLocal", "get_db", "get_db_context", "init_db", "drop_db", "check_db_connection"]
