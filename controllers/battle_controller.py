"""Controller for policy battle - handles request validation and processing"""

import traceback
from fastapi import UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from validators.file_validator import validate_pdf_upload
from services.analyze_service import analyze_policy_service
from services.battle_service import battle_service
from services.policy_service import get_policy_by_id


async def battle_controller(
    file1: UploadFile,
    file2: UploadFile,
    policy1_id: int,
    policy2_id: int,
    user_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Process policy battle request.
    
    Accepts either:
    - Two uploaded PDF files
    - Two saved policy IDs
    - Mixed: one file + one saved policy
    
    Args:
        file1: First PDF file (optional)
        file2: Second PDF file (optional)
        policy1_id: First saved policy ID (optional)
        policy2_id: Second saved policy ID (optional)
        user_id: ID of authenticated user
        db: Database session
        
    Returns:
        {"success": True, "data": {battle results}}
        
    Raises:
        HTTPException: If validation or battle fails
    """
    try:
        # Get policy 1 data
        analysis1 = None
        name1 = None
        
        if file1 and file1.filename:
            await validate_pdf_upload(file1)
            bytes1 = await file1.read()
            analysis1 = analyze_policy_service(bytes1)
            name1 = file1.filename
        elif policy1_id:
            policy = get_policy_by_id(policy1_id, user_id, db)
            analysis1 = {
                "covered_events": policy.covered_events,
                "exclusions": policy.exclusions,
                "risky_clauses": policy.risky_clauses,
                "coverage_score": policy.coverage_score,
                "policy_type": policy.policy_type,
                "score_reason": policy.score_reason or ""
            }
            name1 = policy.file_name
        else:
            raise HTTPException(status_code=400, detail="Policy 1 is required")
        
        # Get policy 2 data
        analysis2 = None
        name2 = None
        
        if file2 and file2.filename:
            await validate_pdf_upload(file2)
            bytes2 = await file2.read()
            analysis2 = analyze_policy_service(bytes2)
            name2 = file2.filename
        elif policy2_id:
            policy = get_policy_by_id(policy2_id, user_id, db)
            analysis2 = {
                "covered_events": policy.covered_events,
                "exclusions": policy.exclusions,
                "risky_clauses": policy.risky_clauses,
                "coverage_score": policy.coverage_score,
                "policy_type": policy.policy_type,
                "score_reason": policy.score_reason or ""
            }
            name2 = policy.file_name
        else:
            raise HTTPException(status_code=400, detail="Policy 2 is required")
        
        # Validate both policies were resolved
        if not analysis1 or not name1 or not analysis2 or not name2:
            raise HTTPException(
                status_code=400,
                detail="Both policies must be resolvable"
            )
        
        # Run battle
        result = battle_service(analysis1, name1, analysis2, name2)
        
        return {
            "success": True,
            "data": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"❌ Battle Error: {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
