"""
Routes for policy management (view, delete, list user policies).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.utils.jwt_utils import get_current_user_id
from services.policy_service import get_user_policies, get_policy_by_id, delete_policy
from app.schemas.policy import PolicyResponse, PolicyListResponse

router = APIRouter(prefix="/policies", tags=["policies"])


@router.get("", response_model=list[PolicyListResponse])
async def list_policies(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    limit: int = 50,
    skip: int = 0
):
    """
    Get all policies for the authenticated user.
    
    Args:
        user_id: Current authenticated user ID
        db: Database session
        limit: Maximum number of policies to return
        skip: Number of policies to skip (for pagination)
        
    Returns:
        List of user's saved policies
    """
    return get_user_policies(user_id, db, limit=limit, skip=skip)


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific policy by ID.
    
    Args:
        policy_id: ID of the policy to retrieve
        user_id: Current authenticated user ID
        db: Database session
        
    Returns:
        Policy details
        
    Raises:
        HTTPException: If policy not found or unauthorized
    """
    return get_policy_by_id(policy_id, user_id, db)


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy_route(
    policy_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a policy.
    
    Args:
        policy_id: ID of the policy to delete
        user_id: Current authenticated user ID
        db: Database session
        
    Raises:
        HTTPException: If policy not found or unauthorized
    """
    delete_policy(policy_id, user_id, db)
