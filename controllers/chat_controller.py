"""Controller for chat with policy - handles request validation and processing"""

import traceback
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from services.chat_service import chat_policy_service
from services.policy_service import get_policy_by_id


async def chat_policy_controller(
    question: str,
    policy_id: int,
    user_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Process chat request for a policy.
    
    Args:
        question: User's question about the policy
        policy_id: ID of the policy to chat about
        user_id: ID of authenticated user
        db: Database session
        
    Returns:
        {"success": True, "data": {answer, confidence, found_in_policy, related_section}}
        
    Raises:
        HTTPException: If validation or chat fails
    """
    try:
        # Step 1: Validate question
        if not question or not question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
        if len(question.strip()) < 3:
            raise HTTPException(status_code=400, detail="Question is too short.")
        
        # Step 2: Fetch policy from DB
        policy = get_policy_by_id(policy_id, user_id, db)
        
        # Step 3: Build analysis dict
        analysis = {
            "policy_type": policy.policy_type,
            "coverage_score": policy.coverage_score,
            "covered_events": policy.covered_events,
            "exclusions": policy.exclusions,
            "risky_clauses": policy.risky_clauses,
            "score_reason": policy.score_reason or ""
        }
        
        # Step 4: Call service
        result = chat_policy_service(question.strip(), analysis)
        
        return {
            "success": True,
            "data": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"❌ Chat Error: {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
