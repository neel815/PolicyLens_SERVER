"""
Service for managing claim simulations.
"""

from sqlalchemy.orm import Session
from app.models.claim_simulation import ClaimSimulation


def create_claim_simulation(
    db: Session,
    policy_id: int,
    scenario: str,
    coverage_result: bool,
    explanation: str
) -> ClaimSimulation:
    """
    Create a new claim simulation record.
    
    Args:
        db: Database session
        policy_id: ID of the policy being simulated
        scenario: The claim scenario
        coverage_result: Whether the claim is covered or not
        explanation: AI-generated explanation of the result
        
    Returns:
        ClaimSimulation: The created simulation record
    """
    simulation = ClaimSimulation(
        policy_id=policy_id,
        scenario=scenario,
        coverage_result=coverage_result,
        explanation=explanation
    )
    db.add(simulation)
    db.commit()
    db.refresh(simulation)
    return simulation


def get_policy_simulations(db: Session, policy_id: int) -> list[ClaimSimulation]:
    """
    Get all simulations for a specific policy.
    
    Args:
        db: Database session
        policy_id: ID of the policy
        
    Returns:
        list[ClaimSimulation]: List of simulations for the policy
    """
    return db.query(ClaimSimulation).filter(
        ClaimSimulation.policy_id == policy_id
    ).order_by(ClaimSimulation.created_at.desc()).all()


def delete_simulation(db: Session, simulation_id: int) -> bool:
    """
    Delete a simulation record.
    
    Args:
        db: Database session
        simulation_id: ID of the simulation to delete
        
    Returns:
        bool: True if deletion was successful
    """
    simulation = db.query(ClaimSimulation).filter(
        ClaimSimulation.id == simulation_id
    ).first()
    
    if simulation:
        db.delete(simulation)
        db.commit()
        return True
    return False
