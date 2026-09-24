from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AuditRequest, AuditResponse
from app.agent.orchestrator import orchestrator
from app.data.seed_data import seed_initial_data

router = APIRouter(prefix="/api/audit", tags=["Agent Audit"])

@router.post("", response_model=AuditResponse)
def run_agent_audit(req: AuditRequest, db: Session = Depends(get_db)):
    """
    Executes the full Agentic AI pipeline:
    Perceive -> Detect Recurring & Events -> Decide (Waste & Confidence) -> Guardrail Check -> Act -> Audit Log.
    """
    # Ensure baseline data exists
    seed_initial_data(db, req.user_id)
    result = orchestrator.run_full_audit(db, req.user_id, req.user_prompt)
    return result

@router.post("/reset-and-seed")
def reset_and_seed(user_id: str = "u_301", db: Session = Depends(get_db)):
    """Resets database and reseeds with fresh hackathon demo data."""
    from app.models import Subscription, ActionLog, NegotiationOffer
    db.query(NegotiationOffer).delete()
    db.query(ActionLog).filter(ActionLog.user_id == user_id).delete()
    db.query(Subscription).filter(Subscription.user_id == user_id).delete()
    db.commit()
    seed_initial_data(db, user_id)
    return {"message": "Database reset and seeded with fresh demo data successfully."}
