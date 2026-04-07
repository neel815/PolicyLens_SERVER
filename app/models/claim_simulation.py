"""
ClaimSimulation model for storing policy simulation/claim test results.
"""

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class ClaimSimulation(BaseModel):
    """ClaimSimulation model for storing simulation results for policies."""
    __tablename__ = "claim_simulations"

    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False, index=True)
    scenario = Column(Text, nullable=False)
    coverage_result = Column(Boolean, nullable=False)
    explanation = Column(Text, nullable=False)
    
    # Relationship to Policy
    policy = relationship("Policy", back_populates="simulations")

    def __repr__(self):
        return f"<ClaimSimulation(id={self.id}, policy_id={self.policy_id}, coverage={self.coverage_result})>"
