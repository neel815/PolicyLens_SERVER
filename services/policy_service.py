"""
Policy service for database operations.
"""

from sqlalchemy.orm import Session
from app.models.policy import Policy
from app.schemas.policy import PolicyCreate, PolicyResponse, PolicyListResponse
from fastapi import HTTPException


def create_policy(user_id: int, policy_data: PolicyCreate, db: Session) -> PolicyResponse:
    """
    Create and save a new policy analysis to the database.
    
    Args:
        user_id: ID of the user who owns this policy
        policy_data: Policy analysis data to save
        db: Database session
        
    Returns:
        Created policy with ID
    """
    try:
        new_policy = Policy(
            user_id=user_id,
            file_name=policy_data.file_name,
            file_size=policy_data.file_size,
            policy_type=policy_data.policy_type,
            covered_events=policy_data.analysis.covered_events,
            exclusions=policy_data.analysis.exclusions,
            risky_clauses=policy_data.analysis.risky_clauses,
            coverage_score=policy_data.analysis.coverage_score,
            score_reason=policy_data.analysis.score_reason,
        )
        
        db.add(new_policy)
        db.commit()
        db.refresh(new_policy)
        
        return PolicyResponse.model_validate(new_policy)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save policy: {str(e)}")


def get_user_policies(user_id: int, db: Session, limit: int = 50, skip: int = 0) -> list[PolicyListResponse]:
    """
    Get all policies for a user.
    
    Args:
        user_id: ID of the user
        db: Database session
        limit: Maximum number of policies to return
        skip: Number of policies to skip (for pagination)
        
    Returns:
        List of user's policies
    """
    policies = db.query(Policy).filter(
        Policy.user_id == user_id
    ).order_by(
        Policy.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [PolicyListResponse.model_validate(p) for p in policies]


def get_policy_by_id(policy_id: int, user_id: int, db: Session) -> PolicyResponse:
    """
    Get a specific policy by ID (with user authorization check).
    
    Args:
        policy_id: ID of the policy
        user_id: ID of the user requesting (for authorization)
        db: Database session
        
    Returns:
        Policy details
        
    Raises:
        HTTPException: If policy not found or unauthorized
    """
    policy = db.query(Policy).filter(
        (Policy.id == policy_id) & (Policy.user_id == user_id)
    ).first()
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    return PolicyResponse.model_validate(policy)


def delete_policy(policy_id: int, user_id: int, db: Session) -> dict:
    """
    Delete a policy (with user authorization check).
    
    Args:
        policy_id: ID of the policy to delete
        user_id: ID of the user requesting (for authorization)
        db: Database session
        
    Returns:
        Confirmation message
        
    Raises:
        HTTPException: If policy not found or unauthorized
    """
    policy = db.query(Policy).filter(
        (Policy.id == policy_id) & (Policy.user_id == user_id)
    ).first()
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    try:
        db.delete(policy)
        db.commit()
        return {"message": "Policy deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete policy: {str(e)}")
