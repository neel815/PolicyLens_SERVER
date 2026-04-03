"""
Routes for policy analysis endpoints
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from controllers.analyze_controller import analyze_policy_controller

router = APIRouter(tags=["analysis"])


@router.post("/analyze")
async def analyze_policy(file: UploadFile = File(...)):
    """
    Analyze an insurance policy PDF.
    
    Args:
        file: PDF file to analyze
        
    Returns:
        Analysis results with covered events, exclusions, risky clauses, and coverage score
    """
    try:
        return await analyze_policy_controller(file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
