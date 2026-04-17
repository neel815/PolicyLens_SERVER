"""
Database models for PolicyLens backend.
All models inherit from BaseModel which provides id, created_at, updated_at.
"""

from .base import BaseModel
from .user import User
from .policy import Policy
from .claim_simulation import ClaimSimulation

__all__ = [
    "BaseModel",
    "User",
    "Policy",
    "ClaimSimulation",
]
