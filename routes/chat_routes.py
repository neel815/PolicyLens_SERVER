"""
Routes for chat with policy endpoints
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from controllers.chat_controller import chat_policy_controller
from app.utils.jwt_utils import get_current_user_id
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    question: str
    policy_id: int


@router.post("/chat-policy")
async def chat_policy(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Chat with an insurance policy.
    
    Args:
        request: ChatRequest with question and policy_id
        user_id: Authenticated user ID
        db: Database session
        
    Returns:
        Chat response with answer, confidence, and metadata
    """
    return await chat_policy_controller(
        request.question,
        request.policy_id,
        user_id,
        db
    )
