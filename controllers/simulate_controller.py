from fastapi import HTTPException
from services.simulate_service import simulate_claim_service
from services.claim_simulation_service import create_claim_simulation
from services.policy_service import get_policy_by_id
from sqlalchemy.orm import Session


async def simulate_claim_controller(
    scenario: str, 
    analysis: dict,
    user_id: int,
    policy_id: int | None = None,
    db: Session | None = None
) -> dict:
    """
    Controller for claim simulation.
    Validates input and delegates to service layer.
    Ensures user owns the policy if policy_id is provided.
    """
    if not scenario or not scenario.strip():
        raise HTTPException(status_code=400, detail="Scenario cannot be empty.")
    
    if len(scenario.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Please describe your scenario in more detail."
        )
    
    if not analysis:
        raise HTTPException(status_code=400, detail="Policy analysis data is required.")
    
    # Verify user owns the policy if policy_id is provided
    if policy_id and db:
        try:
            get_policy_by_id(policy_id, user_id, db)  # This checks ownership
        except HTTPException as e:
            raise HTTPException(status_code=403, detail="Access denied: You do not own this policy.")
    
    try:
        result = simulate_claim_service(scenario.strip(), analysis)
        
        # Save simulation to database if policy_id and db are provided
        if policy_id and db:
            try:
                create_claim_simulation(
                    db=db,
                    policy_id=policy_id,
                    scenario=scenario.strip(),
                    coverage_result=result.get("verdict") in ["Likely Approved", "Partial Coverage"],
                    explanation=result.get("explanation", "")
                )
            except Exception as e:
                # Log error but don't fail the simulation due to storage issues
                print(f"Failed to save simulation: {str(e)}")
        
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
