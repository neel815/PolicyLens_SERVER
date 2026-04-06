"""
Routes for policy analysis endpoints
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.utils.jwt_utils import get_current_user_id
from controllers.analyze_controller import analyze_policy_controller

router = APIRouter(tags=["analysis"])


@router.post("/analyze")
async def analyze_policy(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Analyze an insurance policy PDF.
    
    Args:
        file: PDF file to analyze
        user_id: Authenticated user ID
        db: Database session
        
    Returns:
        Analysis results with covered events, exclusions, risky clauses, and coverage score
    """
    try:
        return await analyze_policy_controller(file, user_id, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
