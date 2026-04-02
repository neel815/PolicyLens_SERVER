"""
Base model for all database models.
Provides common columns and functionality for all entities.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, func
from app.db.database import Base


class BaseModel(Base):
    """
    Abstract base model for all database models.
    Provides id, created_at, and updated_at columns.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
