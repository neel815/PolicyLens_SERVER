"""
Policy model for storing insurance policy analysis results.
"""

from sqlalchemy import Column, String, Integer, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Policy(BaseModel):
    """Policy model for storing insurance policy analysis results per user."""
    __tablename__ = "policies"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(String(50), nullable=False)
    policy_type = Column(String(100), nullable=False)
    
    # Analysis results (stored as JSON)
    covered_events = Column(JSON, nullable=False)
    exclusions = Column(JSON, nullable=False)
    risky_clauses = Column(JSON, nullable=False)
    coverage_score = Column(Integer, nullable=False)
    score_reason = Column(String(500), nullable=True)
    
    # Full AI response (flexible JSONB for future features)
    analysis = Column(JSON, nullable=True)
    
    # Relationship to User
    user = relationship("User", back_populates="policies")

    def __repr__(self):
        return f"<Policy(id={self.id}, user_id={self.user_id}, policy_type='{self.policy_type}')>"
