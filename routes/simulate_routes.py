from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel, Field
from controllers.simulate_controller import simulate_claim_controller
from app.utils.jwt_utils import get_current_user_id
from app.db.database import get_db
from sqlalchemy.orm import Session
from services.claim_simulation_service import get_policy_simulations
from slowapi.util import get_remote_address
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


class SimulateRequest(BaseModel):
    """Claim simulation request with input validation."""
    scenario: str = Field(..., min_length=10, max_length=5000, description="Claim scenario details")
    analysis: dict
    policy_id: int | None = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenario": "Customer was involved in a car accident. describe what happened...",
                "analysis": {},
                "policy_id": 123
            }
        }


@limiter.limit("10/minute")
@router.post("/simulate-claim")
async def simulate_claim(
    request: SimulateRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    req: Request = None
):
    return await simulate_claim_controller(
        request.scenario, 
        request.analysis,
        user_id,
        request.policy_id,
        db
    )


@limiter.limit("20/minute")
@router.get("/policies/{policy_id}/simulations")
async def get_simulations(
    policy_id: int,
    request: Request,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all simulations for a specific policy (user must own policy)."""
    # Verify user owns this policy
    from services.policy_service import get_policy_by_id
    try:
        get_policy_by_id(policy_id, user_id, db)
    except HTTPException:
        raise HTTPException(status_code=403, detail="Access denied: You do not own this policy.")
    
    simulations = get_policy_simulations(db, policy_id)
    return [
        {
            "id": sim.id,
            "policy_id": sim.policy_id,
            "scenario": sim.scenario,
            "coverage_result": sim.coverage_result,
            "explanation": sim.explanation,
            "created_at": sim.created_at.isoformat() if sim.created_at else None
        }
        for sim in simulations
    ]
