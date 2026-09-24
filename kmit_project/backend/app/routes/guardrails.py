from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import GuardrailConfig
from app.schemas import GuardrailConfigSchema, GuardrailUpdate

router = APIRouter(prefix="/api/guardrails", tags=["Guardrails"])

@router.get("", response_model=GuardrailConfigSchema)
def get_user_guardrails(user_id: str = "u_301", db: Session = Depends(get_db)):
    config = db.query(GuardrailConfig).filter(GuardrailConfig.user_id == user_id).first()
    if not config:
        config = GuardrailConfig(
            user_id=user_id,
            auto_action_limit=2000.0,
            protected_categories=["insurance", "loan_payment", "healthcare", "utility", "education"],
            min_confidence_threshold=0.85,
            require_approval_for_duplicates=True,
            negotiation_mode=False
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

@router.put("", response_model=GuardrailConfigSchema)
def update_user_guardrails(update_data: GuardrailUpdate, user_id: str = "u_301", db: Session = Depends(get_db)):
    config = db.query(GuardrailConfig).filter(GuardrailConfig.user_id == user_id).first()
    if not config:
        config = GuardrailConfig(user_id=user_id)
        db.add(config)

    if update_data.auto_action_limit is not None:
        config.auto_action_limit = update_data.auto_action_limit
    if update_data.protected_categories is not None:
        config.protected_categories = update_data.protected_categories
    if update_data.min_confidence_threshold is not None:
        config.min_confidence_threshold = update_data.min_confidence_threshold
    if update_data.require_approval_for_duplicates is not None:
        config.require_approval_for_duplicates = update_data.require_approval_for_duplicates
    if update_data.negotiation_mode is not None:
        config.negotiation_mode = update_data.negotiation_mode

    db.commit()
    db.refresh(config)
    return config
