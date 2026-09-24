from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import PromptRequest, PromptResponse
from app.agent.orchestrator import orchestrator
from app.data.seed_data import seed_initial_data

router = APIRouter(prefix="/api/prompt", tags=["AI Prompt Console"])

@router.post("", response_model=PromptResponse)
def handle_user_prompt(req: PromptRequest, db: Session = Depends(get_db)):
    """
    Processes natural language user prompts to audit subscriptions, execute direct actions,
    or answer financial queries and questions.
    """
    seed_initial_data(db, req.user_id)
    result = orchestrator.process_user_prompt(db, req.user_id, req.prompt)
    return result
