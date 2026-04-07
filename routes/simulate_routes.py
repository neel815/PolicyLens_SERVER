from fastapi import APIRouter, Depends
from pydantic import BaseModel
from controllers.simulate_controller import simulate_claim_controller
from app.utils.jwt_utils import get_current_user_id
from app.db.database import get_db
from sqlalchemy.orm import Session
from services.claim_simulation_service import get_policy_simulations

router = APIRouter()


class SimulateRequest(BaseModel):
    scenario: str
    analysis: dict
    policy_id: int | None = None


@router.post("/simulate-claim")
async def simulate_claim(
    request: SimulateRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    return await simulate_claim_controller(
        request.scenario, 
        request.analysis,
        request.policy_id,
        db
    )


@router.get("/policies/{policy_id}/simulations")
async def get_simulations(
    policy_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all simulations for a specific policy."""
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
