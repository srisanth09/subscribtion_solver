from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MerchantCommunication, Subscription
from app.schemas import (
    MerchantCommunicationSchema,
    SendNegotiationRequest,
    MerchantResponseRequest,
    TestMerchantSimulateRequest
)
from app.agent.negotiation_agent import negotiation_agent

router = APIRouter(prefix="/api/merchants", tags=["Merchant Communication"])

@router.get("/communications", response_model=List[MerchantCommunicationSchema])
def list_merchant_communications(
    user_id: str = "u_301",
    subscription_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lists tracked merchant communication threads."""
    return negotiation_agent.get_communications(
        db=db,
        user_id=user_id,
        subscription_id=subscription_id,
        status=status
    )

@router.post("/communication/send", response_model=MerchantCommunicationSchema)
def send_negotiation_request(
    req: SendNegotiationRequest,
    db: Session = Depends(get_db)
):
    """
    Agent drafts and dispatches a discount/downgrade negotiation request to the merchant.
    Tracks outgoing message and sets subscription status to 'negotiating'.
    """
    sub = db.query(Subscription).filter(
        Subscription.id == req.subscription_id,
        Subscription.user_id == req.user_id
    ).first()

    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found.")

    comm = negotiation_agent.send_negotiation_to_merchant(
        db=db,
        user_id=req.user_id,
        subscription=sub,
        request_type=req.request_type,
        target_discount_pct=req.target_discount_pct
    )
    return comm

@router.post("/communication/{comm_id}/respond")
def handle_merchant_response(
    comm_id: int,
    req: MerchantResponseRequest,
    db: Session = Depends(get_db)
):
    """
    Webhook / callback endpoint for merchant responses.
    Agent evaluates the response and:
    - If ACCEPTED: applies the discount/downgrade, updates status to 'negotiated', logs NEGOTIATION_ACCEPTED.
    - If REJECTED: evaluates failure and triggers fallback auto-cancellation of the wasteful subscription.
    """
    result = negotiation_agent.evaluate_and_apply_merchant_response(
        db=db,
        user_id=req.user_id,
        communication_id=comm_id,
        outcome=req.outcome,
        counter_price=req.counter_price,
        response_text=req.response_text
    )
    return result

@router.post("/test-merchant/simulate")
def simulate_test_merchant_negotiation(
    req: TestMerchantSimulateRequest,
    db: Session = Depends(get_db)
):
    """
    Simulates a test merchant receiving a negotiation request and returning an accepted or rejected offer.
    The agent evaluates the incoming response and applies the correct follow-up action.
    """
    result = negotiation_agent.simulate_test_merchant(
        db=db,
        user_id=req.user_id,
        subscription_id=req.subscription_id,
        simulate_outcome=req.simulate_outcome,
        request_type=req.request_type
    )
    return result

@router.get("/test-merchant/pending", response_model=List[MerchantCommunicationSchema])
def get_pending_merchant_requests(
    user_id: str = "u_301",
    db: Session = Depends(get_db)
):
    """Retrieves all negotiation requests currently awaiting response from merchants."""
    return negotiation_agent.get_communications(
        db=db,
        user_id=user_id,
        status="SENT"
    )
