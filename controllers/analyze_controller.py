"""Controller for policy analysis - handles request validation and processing"""

import traceback
from fastapi import UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from validators.file_validator import validate_pdf_upload
from services.analyze_service import analyze_policy_service
from services.policy_service import create_policy
from app.schemas.policy import PolicyCreate, PolicyAnalysisData
from app.utils.jwt_utils import get_current_user_id


async def analyze_policy_controller(
    file: UploadFile, 
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> dict:
    """
    Process policy analysis request.
    
    Validates file, extracts PDF bytes, calls analysis service, and saves to database.
    
    Args:
        file: Uploaded PDF file
        user_id: ID of authenticated user
        db: Database session
        
    Returns:
        {"success": True, "data": {analysis results with policy_id}}
        
    Raises:
        HTTPException: If validation or analysis fails
    """
    try:
        # Step 1: Validate file
        await validate_pdf_upload(file)
        
        # Step 2: Read file bytes
        pdf_bytes = await file.read()
        
        # Step 3: Reset file pointer
        await file.seek(0)
        
        # Step 4: Analyze policy (sync function)
        result = analyze_policy_service(pdf_bytes)
        
        # Step 5: Save to database
        analysis_data = PolicyAnalysisData(
            covered_events=result["covered_events"],
            exclusions=result["exclusions"],
            risky_clauses=result["risky_clauses"],
            coverage_score=result["coverage_score"],
            score_reason=result.get("score_reason", "")
        )
        
        # Extract full AI response for analysis column
        full_ai_response = result.get("_full_ai_response", None)
        
        policy_create = PolicyCreate(
            file_name=file.filename,
            file_size=f"{len(pdf_bytes) / (1024 * 1024):.1f} MB",
            policy_type=result.get("policy_type", "Insurance"),
            analysis=analysis_data
        )
        
        saved_policy = create_policy(user_id, policy_create, db, full_ai_response=full_ai_response)
        
        # Step 6: Return success response with policy ID (exclude internal fields)
        response_data = {
            k: v for k, v in result.items() 
            if not k.startswith("_")
        }
        response_data["policy_id"] = saved_policy.id
        
        return {
            "success": True,
            "data": response_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"❌ Analysis Error: {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Analysis failed: {error_msg}")
