"""
Routes for policy battle endpoints
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.utils.jwt_utils import get_current_user_id
from controllers.battle_controller import battle_controller
from slowapi.util import get_remote_address
from slowapi import Limiter

router = APIRouter(tags=["battle"])
limiter = Limiter(key_func=get_remote_address)


@limiter.limit("10/minute")
@router.post("/battle")
async def battle_policies(
    file1: UploadFile = File(None),
    file2: UploadFile = File(None),
    policy1_id: int = Form(None),
    policy2_id: int = Form(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Battle two insurance policies against each other.
    
    Rate Limited: 10 requests per minute per IP address.
    
    Args:
        file1: First PDF file (optional if policy1_id provided)
        file2: Second PDF file (optional if policy2_id provided)
        policy1_id: ID of first saved policy (optional if file1 provided)
        policy2_id: ID of second saved policy (optional if file2 provided)
        user_id: Authenticated user ID
        db: Database session
        
    Returns:
        Battle results with 6 rounds and final verdict
    """
    try:
        return await battle_controller(
            file1, file2, policy1_id, policy2_id, user_id, db
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
