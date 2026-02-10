"""
Chat routes for Career STU API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from agent.career_stu import create_agent

router = APIRouter()

# In-memory store for agent instances (for MVP)
# In production, use Redis or similar
agent_store = {}


class ChatRequest(BaseModel):
    learner_id: str
    message: str
    reset: Optional[bool] = False


class ChatResponse(BaseModel):
    learner_id: str
    response: str
    current_mode: str


@router.post("/message", response_model=ChatResponse)
def send_message(request: ChatRequest):
    """
    Send a message to Career STU and get a response

    Args:
        learner_id: Learner's unique ID
        message: User's message
        reset: Whether to reset conversation history

    Returns:
        Assistant's response and current mode
    """
    try:
        # Get or create agent for this learner
        if request.learner_id not in agent_store or request.reset:
            agent = create_agent(request.learner_id)
            agent_store[request.learner_id] = agent
        else:
            agent = agent_store[request.learner_id]

        # Get response
        response = agent.chat(request.message)

        # Get current mode
        current_mode = agent.get_current_mode()

        return ChatResponse(
            learner_id=request.learner_id,
            response=response,
            current_mode=current_mode
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
def reset_conversation(learner_id: str):
    """
    Reset conversation history for a learner

    Args:
        learner_id: Learner's unique ID

    Returns:
        Success message
    """
    if learner_id in agent_store:
        agent_store[learner_id].reset_conversation()

    return {"message": f"Conversation reset for learner {learner_id}"}


@router.get("/mode/{learner_id}")
def get_current_mode(learner_id: str):
    """
    Get the current mode for a learner

    Args:
        learner_id: Learner's unique ID

    Returns:
        Current mode (INTAKE, GOAL_DISCOVERY, PATHWAY, LEARNING)
    """
    try:
        if learner_id not in agent_store:
            agent = create_agent(learner_id)
            agent_store[learner_id] = agent
        else:
            agent = agent_store[learner_id]

        current_mode = agent.get_current_mode()

        return {
            "learner_id": learner_id,
            "current_mode": current_mode
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
