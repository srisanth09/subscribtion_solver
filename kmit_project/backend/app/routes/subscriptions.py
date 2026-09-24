import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Subscription, NegotiationOffer, Transaction, GuardrailConfig, User, ActionLog
from app.schemas import SubscriptionSchema, SubscriptionUserAction, NegotiationOfferSchema, SubscriptionCreate
from app.agent.action_executor import action_executor
from app.agent.negotiation_agent import negotiation_agent
from app.agent.waste_analyzer import waste_analyzer
from app.agent.confidence_engine import confidence_engine
from app.agent.guardrail_engine import guardrail_engine
from app.agent.llm_provider import llm_provider

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])

@router.get("", response_model=List[SubscriptionSchema])
def get_subscriptions(
    user_id: str = "u_301",
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Subscription).filter(Subscription.user_id == user_id)
    if status:
        query = query.filter(Subscription.status == status)
    if category:
        query = query.filter(Subscription.category == category)
    return query.order_by(Subscription.waste_score.desc()).all()

@router.post("", response_model=SubscriptionSchema)
def create_subscription(data: SubscriptionCreate, db: Session = Depends(get_db)):
    """
    Manually creates a new subscription and runs it through the Agentic AI pipeline:
    Computes Waste Score, Confidence Score, Price Hike, Guardrail Status, and Reasoning.
    """
    # 1. Ensure user exists
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        user = User(id=data.user_id, name="Demo User", currency=data.currency)
        db.add(user)
        db.commit()

    # 2. Compute price hike metrics if previous_price is provided
    price_hike_detected = False
    old_price = data.previous_price
    hike_percentage = 0.0
    if old_price is not None and old_price > 0 and data.amount > old_price:
        price_hike_detected = True
        hike_percentage = round(((data.amount - old_price) / old_price) * 100, 1)

    # 3. Analyze through Waste & Confidence Engines
    sub_payload = {
        "merchant": data.merchant,
        "amount": data.amount,
        "currency": data.currency,
        "cadence": data.cadence,
        "category": data.category,
        "last_used_days_ago": data.last_used_days_ago,
        "transaction_count": 6,
        "is_duplicate_detected": data.is_duplicate,
        "duplicate_category": data.category if data.is_duplicate else None,
        "duplicate_counterpart": data.duplicate_counterpart,
        "is_bundled": data.is_bundled,
        "bundle_provider": data.bundle_provider,
        "bundle_description": data.bundle_description,
        "is_free_trial": data.is_free_trial,
        "trial_converted": data.trial_converted,
        "price_hike_detected": price_hike_detected,
        "old_price": old_price,
        "hike_percentage": hike_percentage
    }

    waste_score = waste_analyzer.calculate_waste_score(sub_payload)
    sub_payload["waste_score"] = waste_score

    confidence = confidence_engine.calculate_confidence(sub_payload)
    sub_payload["confidence_score"] = confidence

    # 4. Guardrail Evaluation
    guardrail_obj = db.query(GuardrailConfig).filter(GuardrailConfig.user_id == data.user_id).first()
    guardrail_dict = {
        "auto_action_limit": guardrail_obj.auto_action_limit if guardrail_obj else 2000.0,
        "protected_categories": guardrail_obj.protected_categories if guardrail_obj else ["insurance", "loan_payment", "healthcare", "utility", "education"],
        "min_confidence_threshold": guardrail_obj.min_confidence_threshold if guardrail_obj else 0.85,
        "require_approval_for_duplicates": guardrail_obj.require_approval_for_duplicates if guardrail_obj else True
    }

    guardrail_res = guardrail_engine.evaluate(sub_payload, guardrail_dict)
    explanation = llm_provider.generate_decision_explanation(sub_payload, guardrail_res)

    # Determine initial status
    if guardrail_res["status"] == "BLOCKED_PROTECTED":
        initial_status = "protected"
    elif guardrail_res["decision"] == "ESCALATE_APPROVAL":
        initial_status = "pending_approval"
    else:
        initial_status = "active"

    # 5. Check if subscription with same merchant already exists for user
    db_sub = db.query(Subscription).filter(
        Subscription.user_id == data.user_id,
        Subscription.merchant == data.merchant
    ).first()

    if not db_sub:
        db_sub = Subscription(user_id=data.user_id, merchant=data.merchant)
        db.add(db_sub)

    db_sub.amount = data.amount
    db_sub.currency = data.currency
    db_sub.cadence = data.cadence
    db_sub.category = data.category
    db_sub.last_used_days_ago = data.last_used_days_ago
    db_sub.waste_score = waste_score
    db_sub.confidence_score = confidence
    db_sub.status = initial_status
    db_sub.is_free_trial = data.is_free_trial
    db_sub.trial_converted = data.trial_converted
    db_sub.price_hike_detected = price_hike_detected
    db_sub.old_price = old_price
    db_sub.hike_percentage = hike_percentage
    db_sub.is_duplicate_detected = data.is_duplicate
    db_sub.duplicate_category = data.category if data.is_duplicate else None
    db_sub.duplicate_counterpart = data.duplicate_counterpart
    db_sub.is_bundled = data.is_bundled
    db_sub.bundle_provider = data.bundle_provider
    db_sub.bundle_description = data.bundle_description
    db_sub.guardrail_status = guardrail_res["status"]
    db_sub.decision = guardrail_res["decision"]
    db_sub.decision_reason = explanation
    db_sub.next_billing_date = data.transaction_date or datetime.date.today().isoformat()

    # 6. Insert corresponding financial transaction record
    tx_id = f"TX-MANUAL-{data.merchant.upper()[:4]}-{int(datetime.datetime.utcnow().timestamp())}"
    tx_date = data.transaction_date or datetime.date.today().isoformat()
    db_tx = Transaction(
        transaction_id=tx_id,
        user_id=data.user_id,
        merchant=data.merchant,
        amount=data.amount,
        currency=data.currency,
        date=tx_date,
        category=data.category,
        description=f"User added {data.cadence} subscription: {data.merchant}"
    )
    db.add(db_tx)

    db.commit()
    db.refresh(db_sub)
    return db_sub


@router.get("/{sub_id}", response_model=SubscriptionSchema)
def get_subscription_detail(sub_id: int, db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter(Subscription.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub

@router.post("/{sub_id}/action")
def perform_subscription_action(sub_id: int, action_data: SubscriptionUserAction, db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter(Subscription.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    action_log = action_executor.execute_user_approval(
        db=db,
        user_id=sub.user_id,
        sub=sub,
        decision=action_data.action,
        user_note=action_data.user_note
    )
    return {
        "message": f"Action '{action_data.action}' executed successfully.",
        "subscription_status": sub.status,
        "action_log_id": action_log.id,
        "monthly_saving": action_log.monthly_saving
    }

@router.post("/{sub_id}/negotiate")
def start_merchant_negotiation(sub_id: int, db: Session = Depends(get_db)):
    """
    Initiates AI-powered merchant retention negotiation for a subscription.
    Enforces guardrails (prohibits protected categories like insurance/loans).
    Prevents duplicate pending offers on repeat calls.
    """
    sub = db.query(Subscription).filter(Subscription.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if sub.status == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot negotiate an already cancelled subscription.")

    # Guardrail Check: Block protected/high-risk categories
    guardrail_obj = db.query(GuardrailConfig).filter(GuardrailConfig.user_id == sub.user_id).first()
    protected_cats = [
        c.lower().strip() 
        for c in (guardrail_obj.protected_categories if guardrail_obj else ["insurance", "loan_payment", "healthcare", "utility", "education"])
    ]
    sub_cat = (sub.category or "").lower().strip()
    if sub_cat in protected_cats or any(p in sub_cat for p in protected_cats):
        raise HTTPException(
            status_code=403, 
            detail=f"Negotiation is not permitted for protected category '{sub.category}'. Safety guardrails block automated modification of essential policies."
        )

    # Check for existing active/pending offer to avoid duplicate records on refresh
    existing_offer = db.query(NegotiationOffer).filter(
        NegotiationOffer.subscription_id == sub.id,
        NegotiationOffer.status.in_(["pending", "pending_acceptance"])
    ).order_by(NegotiationOffer.created_at.desc()).first()

    if existing_offer:
        sub.status = "negotiating"
        db.commit()
        return {
            "message": "Active negotiation offer retrieved.",
            "offer": existing_offer
        }

    # Run negotiation agent
    offer_intel = negotiation_agent.initiate_negotiation({
        "merchant": sub.merchant,
        "amount": sub.amount,
        "currency": sub.currency,
        "category": sub.category
    })

    # Save offer
    offer = NegotiationOffer(
        subscription_id=sub.id,
        merchant=sub.merchant,
        original_price=offer_intel["original_price"],
        offered_price=offer_intel["offered_price"],
        discount_percent=offer_intel["discount_percent"],
        monthly_saving=offer_intel["monthly_saving"],
        annual_saving=offer_intel["annual_saving"],
        pitch_letter=offer_intel["pitch_letter"],
        merchant_reply=offer_intel["merchant_reply"],
        status="pending_acceptance"
    )
    db.add(offer)
    sub.status = "negotiating"
    db.commit()
    db.refresh(offer)

    return {
        "message": "Negotiation pitch dispatched to merchant.",
        "offer": offer
    }

@router.post("/{sub_id}/negotiate/{offer_id}/accept")
@router.post("/{sub_id}/accept-offer")
def accept_negotiated_offer(sub_id: int, offer_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Accepts the merchant discount offer.
    Applies the discounted price, sets status to 'negotiated', creates an audit log,
    and contributes realized monthly and annual savings idempotently.
    """
    sub = db.query(Subscription).filter(Subscription.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if offer_id:
        offer = db.query(NegotiationOffer).filter(NegotiationOffer.id == offer_id).first()
    else:
        offer = db.query(NegotiationOffer).filter(
            NegotiationOffer.subscription_id == sub.id
        ).order_by(NegotiationOffer.created_at.desc()).first()

    if not offer:
        raise HTTPException(status_code=404, detail="Negotiation offer not found")

    # Idempotent check: if already accepted, return existing results without double-counting
    if offer.status == "accepted":
        monthly_saving = offer.monthly_saving or round(offer.original_price - offer.offered_price, 2)
        annual_saving = offer.annual_saving or round(monthly_saving * 12.0, 2)
        return {
            "message": f"Discount already accepted! Monthly fee reduced to {sub.currency}{offer.offered_price:,.2f}.",
            "monthly_savings": monthly_saving,
            "annual_savings": annual_saving,
            "subscription_status": sub.status,
            "original_price": offer.original_price,
            "final_price": sub.amount
        }

    if offer.status in ["failed", "declined", "rejected", "expired", "no_offer"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot accept offer because negotiation has status '{offer.status}'."
        )

    if offer.status not in ["pending", "pending_acceptance"]:
        raise HTTPException(status_code=400, detail=f"Offer is not pending (current status: {offer.status}).")

    old_price = offer.original_price or sub.amount
    new_price = offer.offered_price
    monthly_saving = offer.monthly_saving or round(old_price - new_price, 2)
    annual_saving = offer.annual_saving or round(monthly_saving * 12.0, 2)

    sub.amount = new_price
    sub.status = "negotiated"
    offer.status = "accepted"

    # Log savings in immutable ActionLog idempotently
    existing_log = db.query(ActionLog).filter(
        ActionLog.user_id == sub.user_id,
        ActionLog.subscription_id == sub.id,
        ActionLog.action_type == "NEGOTIATION_ACCEPTED"
    ).first()

    if not existing_log:
        log = ActionLog(
            user_id=sub.user_id,
            subscription_id=sub.id,
            merchant=sub.merchant,
            action_type="NEGOTIATION_ACCEPTED",
            reason=f"Accepted merchant retention discount of {offer.discount_percent:.0f}%. Reduced rate from {sub.currency}{old_price:,.2f} to {sub.currency}{new_price:,.2f}/month.",
            waste_score=sub.waste_score or 0,
            confidence=0.95,
            amount=new_price,
            monthly_saving=monthly_saving,
            annual_saving=annual_saving,
            timestamp=datetime.datetime.utcnow(),
            extra_details={
                "original_price": old_price,
                "new_price": new_price,
                "discount_percent": offer.discount_percent,
                "offer_id": offer.id
            }
        )
        db.add(log)
        db.commit()
        log_id = log.id
    else:
        db.commit()
        log_id = existing_log.id

    return {
        "message": f"Discount accepted! Monthly fee reduced to {sub.currency}{new_price:,.2f}.",
        "monthly_savings": monthly_saving,
        "annual_savings": annual_saving,
        "subscription_status": sub.status,
        "original_price": old_price,
        "final_price": new_price,
        "action_log_id": log_id
    }

@router.post("/{sub_id}/negotiate/{offer_id}/decline")
@router.post("/{sub_id}/decline-offer")
def decline_negotiated_offer(sub_id: int, offer_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Declines the merchant discount offer.
    Maintains original subscription price strictly, logs the decline without adding savings.
    """
    sub = db.query(Subscription).filter(Subscription.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if offer_id:
        offer = db.query(NegotiationOffer).filter(NegotiationOffer.id == offer_id).first()
    else:
        offer = db.query(NegotiationOffer).filter(
            NegotiationOffer.subscription_id == sub.id
        ).order_by(NegotiationOffer.created_at.desc()).first()

    if not offer:
        raise HTTPException(status_code=404, detail="Negotiation offer not found")

    if offer.status == "declined":
        return {
            "message": "Negotiation offer was already declined.",
            "subscription_status": sub.status,
            "monthly_savings": 0.0,
            "annual_savings": 0.0,
            "original_price": offer.original_price or sub.amount,
            "final_price": sub.amount
        }

    if offer.status == "accepted":
        raise HTTPException(status_code=400, detail="Cannot decline an offer that has already been accepted.")

    # Price must strictly remain original price
    if offer.original_price is not None:
        sub.amount = offer.original_price
    offer.status = "declined"
    sub.status = "active"

    # Check for existing ActionLog
    existing_log = db.query(ActionLog).filter(
        ActionLog.user_id == sub.user_id,
        ActionLog.subscription_id == sub.id,
        ActionLog.action_type == "NEGOTIATION_DECLINED"
    ).first()

    if not existing_log:
        log = ActionLog(
            user_id=sub.user_id,
            subscription_id=sub.id,
            merchant=sub.merchant,
            action_type="NEGOTIATION_DECLINED",
            reason=f"Declined merchant retention discount offer of {offer.discount_percent:.0f}%. Maintained original monthly rate of {sub.currency}{sub.amount:,.2f}.",
            waste_score=sub.waste_score or 0,
            confidence=0.95,
            amount=sub.amount,
            monthly_saving=0.0,
            annual_saving=0.0,
            timestamp=datetime.datetime.utcnow(),
            extra_details={
                "original_price": offer.original_price,
                "offered_price": offer.offered_price,
                "final_price": sub.amount,
                "discount_percent": offer.discount_percent,
                "offer_id": offer.id
            }
        )
        db.add(log)
        db.commit()
        log_id = log.id
    else:
        db.commit()
        log_id = existing_log.id

    return {
        "message": f"Negotiation offer declined. Subscription maintained at original price ({sub.currency}{sub.amount:,.2f}/mo).",
        "subscription_status": sub.status,
        "monthly_savings": 0.0,
        "annual_savings": 0.0,
        "original_price": offer.original_price or sub.amount,
        "final_price": sub.amount,
        "action_log_id": log_id
    }

@router.post("/{sub_id}/negotiate/{offer_id}/fail")
@router.post("/{sub_id}/fail-offer")
def fail_negotiated_offer(
    sub_id: int, 
    offer_id: Optional[int] = None, 
    reason: str = "Merchant declined retention concession / negotiation failed",
    db: Session = Depends(get_db)
):
    """
    Handles failed negotiation (e.g. merchant rejected concession or no discount offered).
    Maintains original subscription price strictly, sets status to 'active',
    logs NEGOTIATION_FAILED with 0 realized savings.
    """
    sub = db.query(Subscription).filter(Subscription.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if offer_id:
        offer = db.query(NegotiationOffer).filter(NegotiationOffer.id == offer_id).first()
    else:
        offer = db.query(NegotiationOffer).filter(
            NegotiationOffer.subscription_id == sub.id
        ).order_by(NegotiationOffer.created_at.desc()).first()

    if not offer:
        raise HTTPException(status_code=404, detail="Negotiation offer not found")

    if offer.status == "failed":
        return {
            "message": "Negotiation was already marked as failed.",
            "subscription_status": sub.status,
            "monthly_savings": 0.0,
            "annual_savings": 0.0,
            "original_price": offer.original_price or sub.amount,
            "final_price": sub.amount
        }

    if offer.status == "accepted":
        raise HTTPException(status_code=400, detail="Cannot fail an offer that has already been accepted.")

    # Price must strictly remain original price
    if offer.original_price is not None:
        sub.amount = offer.original_price
    offer.status = "failed"
    sub.status = "active"

    # Check for existing ActionLog
    existing_log = db.query(ActionLog).filter(
        ActionLog.user_id == sub.user_id,
        ActionLog.subscription_id == sub.id,
        ActionLog.action_type == "NEGOTIATION_FAILED"
    ).first()

    if not existing_log:
        log = ActionLog(
            user_id=sub.user_id,
            subscription_id=sub.id,
            merchant=sub.merchant,
            action_type="NEGOTIATION_FAILED",
            reason=f"Negotiation failed: {reason}. Maintained original monthly rate of {sub.currency}{sub.amount:,.2f}.",
            waste_score=sub.waste_score or 0,
            confidence=0.95,
            amount=sub.amount,
            monthly_saving=0.0,
            annual_saving=0.0,
            timestamp=datetime.datetime.utcnow(),
            extra_details={
                "original_price": offer.original_price,
                "final_price": sub.amount,
                "status": "failed",
                "offer_id": offer.id
            }
        )
        db.add(log)
        db.commit()
        log_id = log.id
    else:
        db.commit()
        log_id = existing_log.id

    return {
        "message": f"Negotiation failed. Subscription maintained at original price ({sub.currency}{sub.amount:,.2f}/mo).",
        "subscription_status": sub.status,
        "monthly_savings": 0.0,
        "annual_savings": 0.0,
        "original_price": offer.original_price or sub.amount,
        "final_price": sub.amount,
        "action_log_id": log_id
    }

@router.post("/{sub_id}/negotiate/{offer_id}/expire")
@router.post("/{sub_id}/expire-offer")
def expire_negotiated_offer(
    sub_id: int, 
    offer_id: Optional[int] = None, 
    db: Session = Depends(get_db)
):
    """
    Handles expired negotiation offer.
    Maintains original subscription price strictly, sets status to 'active',
    logs NEGOTIATION_FAILED with 0 realized savings.
    """
    sub = db.query(Subscription).filter(Subscription.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if offer_id:
        offer = db.query(NegotiationOffer).filter(NegotiationOffer.id == offer_id).first()
    else:
        offer = db.query(NegotiationOffer).filter(
            NegotiationOffer.subscription_id == sub.id
        ).order_by(NegotiationOffer.created_at.desc()).first()

    if not offer:
        raise HTTPException(status_code=404, detail="Negotiation offer not found")

    if offer.status == "expired":
        return {
            "message": "Negotiation offer was already marked as expired.",
            "subscription_status": sub.status,
            "monthly_savings": 0.0,
            "annual_savings": 0.0,
            "original_price": offer.original_price or sub.amount,
            "final_price": sub.amount
        }

    if offer.status == "accepted":
        raise HTTPException(status_code=400, detail="Cannot expire an offer that has already been accepted.")

    # Price must strictly remain original price
    if offer.original_price is not None:
        sub.amount = offer.original_price
    offer.status = "expired"
    sub.status = "active"

    # Check for existing ActionLog
    existing_log = db.query(ActionLog).filter(
        ActionLog.user_id == sub.user_id,
        ActionLog.subscription_id == sub.id,
        ActionLog.action_type == "NEGOTIATION_FAILED"
    ).first()

    if not existing_log:
        log = ActionLog(
            user_id=sub.user_id,
            subscription_id=sub.id,
            merchant=sub.merchant,
            action_type="NEGOTIATION_FAILED",
            reason=f"Negotiation offer expired. Maintained original monthly rate of {sub.currency}{sub.amount:,.2f}.",
            waste_score=sub.waste_score or 0,
            confidence=0.95,
            amount=sub.amount,
            monthly_saving=0.0,
            annual_saving=0.0,
            timestamp=datetime.datetime.utcnow(),
            extra_details={
                "original_price": offer.original_price,
                "final_price": sub.amount,
                "status": "expired",
                "offer_id": offer.id
            }
        )
        db.add(log)
        db.commit()
        log_id = log.id
    else:
        db.commit()
        log_id = existing_log.id

    return {
        "message": f"Negotiation offer expired. Subscription maintained at original price ({sub.currency}{sub.amount:,.2f}/mo).",
        "subscription_status": sub.status,
        "monthly_savings": 0.0,
        "annual_savings": 0.0,
        "original_price": offer.original_price or sub.amount,
        "final_price": sub.amount,
        "action_log_id": log_id
    }
