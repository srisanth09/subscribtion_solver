import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Subscription, ActionLog, NegotiationOffer

class ActionExecutor:
    """
    Executes and records actions (auto-cancel, pause, downgrade, negotiate, human approval).
    Maintains an immutable audit log of all financial decisions.
    """

    def execute_auto_cancel(self, db: Session, user_id: str, sub: Subscription, reason: str, confidence: float, waste_score: int) -> ActionLog:
        # Check whether subscription is already cancelled or an ActionLog already exists
        existing_log = db.query(ActionLog).filter(
            ActionLog.user_id == user_id,
            ActionLog.action_type.in_(["AUTO_CANCEL", "USER_APPROVED_CANCEL"]),
            (ActionLog.subscription_id == sub.id) | (ActionLog.merchant == sub.merchant)
        ).first()

        if sub.status == "cancelled" or existing_log:
            sub.status = "cancelled"
            if not sub.action_taken:
                sub.action_taken = "AUTO_CANCELLED"
            db.commit()
            return existing_log

        sub.status = "cancelled"
        sub.action_taken = "AUTO_CANCELLED"
        sub.decision_reason = reason
        
        monthly_saving = sub.amount
        annual_saving = sub.amount * 12

        action_log = ActionLog(
            user_id=user_id,
            subscription_id=sub.id,
            merchant=sub.merchant,
            action_type="AUTO_CANCEL",
            reason=reason,
            waste_score=waste_score,
            confidence=confidence,
            amount=sub.amount,
            monthly_saving=monthly_saving,
            annual_saving=annual_saving,
            timestamp=datetime.datetime.utcnow(),
            extra_details={
                "cadence": sub.cadence,
                "days_inactive": sub.last_used_days_ago,
                "cancellation_payload": {
                    "method": "API_SIMULATION",
                    "cancellation_ref": f"CAN-{sub.id}-{int(datetime.datetime.utcnow().timestamp())}",
                    "merchant_ack": "Subscription recurring mandate revoked successfully."
                }
            }
        )
        db.add(action_log)
        db.commit()
        db.refresh(action_log)
        return action_log

    def execute_escalation(self, db: Session, user_id: str, sub: Subscription, reason: str, confidence: float, waste_score: int, guardrail_status: str) -> ActionLog:
        action_type = "ESCALATE_APPROVAL" if guardrail_status != "BLOCKED_PROTECTED" else "BLOCKED_GUARDRAIL"

        # Check if identical escalation action log already exists for this subscription
        existing_log = db.query(ActionLog).filter(
            ActionLog.user_id == user_id,
            ActionLog.action_type == action_type,
            (ActionLog.subscription_id == sub.id) | (ActionLog.merchant == sub.merchant)
        ).first()

        sub.status = "pending_approval" if guardrail_status != "BLOCKED_PROTECTED" else "protected"
        sub.guardrail_status = guardrail_status
        sub.decision_reason = reason
        sub.decision = "ESCALATE_APPROVAL"
        db.commit()

        if existing_log:
            return existing_log

        action_log = ActionLog(
            user_id=user_id,
            subscription_id=sub.id,
            merchant=sub.merchant,
            action_type=action_type,
            reason=reason,
            waste_score=waste_score,
            confidence=confidence,
            amount=sub.amount,
            monthly_saving=0.0,
            annual_saving=0.0,
            timestamp=datetime.datetime.utcnow(),
            extra_details={
                "guardrail_status": guardrail_status,
                "potential_monthly_saving": sub.amount
            }
        )
        db.add(action_log)
        db.commit()
        db.refresh(action_log)
        return action_log

    def execute_user_approval(self, db: Session, user_id: str, sub: Subscription, decision: str, user_note: Optional[str] = None) -> ActionLog:
        """
        Handles human-in-the-loop decision: user approves cancellation or decides to keep the service.
        """
        if decision == "approve_cancel":
            sub.status = "cancelled"
            sub.action_taken = "USER_APPROVED_CANCELLATION"
            action_type = "USER_APPROVED_CANCEL"
            monthly_saving = sub.amount
            annual_saving = sub.amount * 12
            reason = f"User approved cancellation recommendation. Note: {user_note or 'No extra note'}"
        elif decision == "keep":
            sub.status = "kept"
            sub.action_taken = "USER_KEPT"
            action_type = "USER_KEPT"
            monthly_saving = 0.0
            annual_saving = 0.0
            reason = f"User chose to retain subscription despite overlap or inactivity. Note: {user_note or 'Intentionally kept'}"
        elif decision == "downgrade":
            sub.status = "downgraded"
            sub.action_taken = "DOWNGRADED"
            action_type = "PLAN_DOWNGRADE"
            # Estimate 30% savings on downgrade
            monthly_saving = round(sub.amount * 0.3, 2)
            annual_saving = monthly_saving * 12
            sub.amount = round(sub.amount * 0.7, 2)
            reason = f"User initiated downgrade to lower functional tier. Saving {sub.currency}{monthly_saving}/month."
        else:
            raise ValueError(f"Unknown action {decision}")

        action_log = ActionLog(
            user_id=user_id,
            subscription_id=sub.id,
            merchant=sub.merchant,
            action_type=action_type,
            reason=reason,
            waste_score=sub.waste_score,
            confidence=sub.confidence_score,
            amount=sub.amount,
            monthly_saving=monthly_saving,
            annual_saving=annual_saving,
            timestamp=datetime.datetime.utcnow(),
            extra_details={"user_note": user_note}
        )
        db.add(action_log)
        db.commit()
        db.refresh(action_log)
        return action_log

action_executor = ActionExecutor()
