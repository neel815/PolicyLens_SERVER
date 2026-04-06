from fastapi import APIRouter, Depends
from pydantic import BaseModel
from controllers.simulate_controller import simulate_claim_controller
from app.utils.jwt_utils import get_current_user_id

router = APIRouter()


class SimulateRequest(BaseModel):
    scenario: str
    analysis: dict


@router.post("/simulate-claim")
async def simulate_claim(
    request: SimulateRequest,
    user_id: int = Depends(get_current_user_id)
):
    return await simulate_claim_controller(request.scenario, request.analysis)
