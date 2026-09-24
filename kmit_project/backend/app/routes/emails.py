from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import EmailLog
from app.schemas import EmailSchema

router = APIRouter(prefix="/api/emails", tags=["Emails"])

@router.get("", response_model=List[EmailSchema])
def get_emails(user_id: str = "u_301", db: Session = Depends(get_db)):
    """Retrieves all scanned billing, renewal, and price hike emails."""
    return db.query(EmailLog).filter(EmailLog.user_id == user_id).order_by(EmailLog.date.desc()).all()
