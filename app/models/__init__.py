"""
Database models for PolicyLens backend.
All models inherit from BaseModel which provides id, created_at, updated_at.
"""

from .base import BaseModel
from .user import User

__all__ = [
    "BaseModel",
    "User",
]
