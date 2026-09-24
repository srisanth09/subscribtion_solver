from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ActionLog
from app.schemas import ActionLogSchema

router = APIRouter(prefix="/api/audit-logs", tags=["Audit Logs"])

@router.get("", response_model=List[ActionLogSchema])
def get_audit_logs(user_id: str = "u_301", limit: int = 50, db: Session = Depends(get_db)):
    """Returns chronological timeline of all decisions, autonomous actions, and human interventions."""
    logs = db.query(ActionLog).filter(ActionLog.user_id == user_id).order_by(ActionLog.timestamp.desc()).limit(limit).all()
    return logs
