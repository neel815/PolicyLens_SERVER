"""
Pydantic schemas for Policy model validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PolicyAnalysisData(BaseModel):
    """Analysis data for a policy."""
    covered_events: List[str]
    exclusions: List[str]
    risky_clauses: List[str]
    coverage_score: int = Field(..., ge=0, le=10)
    score_reason: Optional[str] = None


class PolicyCreate(BaseModel):
    """Schema for creating a new policy analysis."""
    file_name: str
    file_size: str
    policy_type: str
    analysis: PolicyAnalysisData


class PolicyResponse(BaseModel):
    """Schema for policy response."""
    id: int
    user_id: int
    file_name: str
    file_size: str
    policy_type: str
    covered_events: List[str]
    exclusions: List[str]
    risky_clauses: List[str]
    coverage_score: int
    score_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PolicyListResponse(BaseModel):
    """Schema for listing policies."""
    id: int
    file_name: str
    file_size: str
    policy_type: str
    coverage_score: int
    created_at: datetime

    class Config:
        from_attributes = True
