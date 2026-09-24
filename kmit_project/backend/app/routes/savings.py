import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Subscription, ActionLog, User
from app.schemas import SavingsSummary

router = APIRouter(prefix="/api/savings", tags=["Savings & Reports"])

@router.get("", response_model=SavingsSummary)
def get_savings_metrics(user_id: str = "u_301", db: Session = Depends(get_db)):
    subs = db.query(Subscription).filter(Subscription.user_id == user_id).all()
    
    total_subs = len(subs)
    active_count = sum(1 for s in subs if s.status in ["active", "kept", "negotiated"])
    auto_cancelled_count = sum(1 for s in subs if s.status == "cancelled")
    pending_approval_count = sum(1 for s in subs if s.status == "pending_approval")
    protected_count = sum(1 for s in subs if s.status == "protected" or s.guardrail_status == "BLOCKED_PROTECTED")
    price_hikes_count = sum(1 for s in subs if s.price_hike_detected)
    duplicates_count = sum(1 for s in subs if s.is_duplicate_detected)

    # Realized savings from ActionLog where action is cancelled, user approved, or negotiated
    realized_logs = db.query(ActionLog).filter(
        ActionLog.user_id == user_id,
        ActionLog.action_type.in_(["AUTO_CANCEL", "USER_APPROVED_CANCEL", "PLAN_DOWNGRADE", "NEGOTIATION_ACCEPTED"])
    ).all()
    
    # Ensure each completed action is counted only once
    merchant_to_sub_id = {s.merchant.lower(): s.id for s in subs}
    seen_sub_ids = set()
    seen_merchants = set()
    deduped_realized_logs = []

    sorted_logs = sorted(
        realized_logs,
        key=lambda l: l.timestamp or datetime.datetime.min,
        reverse=True
    )

    for l in sorted_logs:
        sub_id = l.subscription_id or merchant_to_sub_id.get(l.merchant.lower())
        m_norm = l.merchant.lower()
        if sub_id:
            if sub_id in seen_sub_ids:
                continue
            seen_sub_ids.add(sub_id)
            seen_merchants.add(m_norm)
            deduped_realized_logs.append(l)
        else:
            if m_norm in seen_merchants:
                continue
            seen_merchants.add(m_norm)
            deduped_realized_logs.append(l)

    realized_monthly = sum(l.monthly_saving for l in deduped_realized_logs)
    realized_annual = sum(l.annual_saving for l in deduped_realized_logs)


    # Potential savings (includes pending approval subscriptions)
    pending_subs = [s for s in subs if s.status == "pending_approval"]
    potential_pending_monthly = sum(s.amount for s in pending_subs)

    potential_monthly = realized_monthly + potential_pending_monthly
    potential_annual = potential_monthly * 12

    # Monthly waste prevented
    waste_prevented_monthly = realized_monthly
    waste_prevented_annual = realized_annual

    return SavingsSummary(
        currency="₹",
        total_subscriptions=total_subs,
        active_count=active_count,
        auto_cancelled_count=auto_cancelled_count,
        pending_approval_count=pending_approval_count,
        protected_count=protected_count,
        price_hikes_count=price_hikes_count,
        duplicates_count=duplicates_count,
        monthly_waste_prevented=round(waste_prevented_monthly, 2),
        annual_waste_prevented=round(waste_prevented_annual, 2),
        realized_monthly_savings=round(realized_monthly, 2),
        realized_annual_savings=round(realized_annual, 2),
        potential_monthly_savings=round(potential_monthly, 2),
        potential_annual_savings=round(potential_annual, 2)
    )

@router.get("/report")
def get_monthly_savings_report(user_id: str = "u_301", db: Session = Depends(get_db)):
    metrics = get_savings_metrics(user_id, db)
    user = db.query(User).filter(User.id == user_id).first()
    recent_actions = db.query(ActionLog).filter(ActionLog.user_id == user_id).order_by(ActionLog.timestamp.desc()).limit(10).all()
    pending_items = db.query(Subscription).filter(Subscription.user_id == user_id, Subscription.status == "pending_approval").all()

    report_markdown = f"""# 🛡️ MONTHLY SAVINGS & SUBSCRIPTION AUDIT REPORT
**User:** {user.name if user else user_id}  
**Period:** Current Billing Cycle  
**Status:** Audit Active & Verified  

---

### 📊 Executive Summary
* **Total Subscriptions Scanned:** {metrics.total_subscriptions}
* **Realized Monthly Savings:** {metrics.currency}{metrics.realized_monthly_savings:,.2f}
* **Projected Annual Savings:** {metrics.currency}{metrics.realized_annual_savings:,.2f}
* **Autonomous Cancellations Executed:** {metrics.auto_cancelled_count}
* **Items Requiring Human Decision:** {metrics.pending_approval_count}
* **Strictly Protected Items:** {metrics.protected_count}

---

### 🛑 Autonomous Actions Completed
"""
    seen_report_merchants = set()
    for a in recent_actions:
        if a.action_type in ["AUTO_CANCEL", "USER_APPROVED_CANCEL", "PLAN_DOWNGRADE", "NEGOTIATION_ACCEPTED"]:
            if a.merchant not in seen_report_merchants:
                seen_report_merchants.add(a.merchant)
                report_markdown += f"- **{a.merchant}**: Saved {metrics.currency}{a.monthly_saving:,.2f}/mo ({a.action_type}) — *{a.reason}*\n"


    report_markdown += f"""
---

### ⏳ Items Awaiting Your Approval
"""
    if pending_items:
        for p in pending_items:
            report_markdown += f"- **{p.merchant}** ({metrics.currency}{p.amount:,.2f}/mo): {p.decision_reason}\n"
    else:
        report_markdown += "No pending approvals. Your subscription portfolio is clean!\n"

    report_markdown += f"""
---
*Generated autonomously by Subscription & Recurring-Spend Guardian Agent.*
"""

    return {
        "metrics": metrics,
        "report_markdown": report_markdown,
        "recent_actions": [
            {
                "merchant": a.merchant,
                "action": a.action_type,
                "amount": a.amount,
                "monthly_saving": a.monthly_saving,
                "reason": a.reason,
                "timestamp": str(a.timestamp)
            }
            for a in recent_actions
        ]
    }
