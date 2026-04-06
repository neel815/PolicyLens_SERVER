from fastapi import HTTPException
from services.simulate_service import simulate_claim_service


async def simulate_claim_controller(scenario: str, analysis: dict) -> dict:
    """
    Controller for claim simulation.
    Validates input and delegates to service layer.
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
    
    try:
        result = simulate_claim_service(scenario.strip(), analysis)
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
