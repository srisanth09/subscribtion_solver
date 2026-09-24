from typing import Dict, Any, List, Optional
import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.agent.llm_provider import llm_provider
from app.models import Subscription, NegotiationOffer, MerchantCommunication, ActionLog
from app.agent.action_executor import action_executor

class NegotiationAgent:
    """
    Autonomous Negotiation Mode Agent.
    Drafts, sends, tracks, and evaluates merchant negotiation responses before cancelling eligible subscriptions.
    """

    def initiate_negotiation(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy helper for backward compatibility."""
        merchant = subscription_data.get("merchant", "Service")
        current_amount = float(subscription_data.get("amount", 0.0))
        currency = subscription_data.get("currency", "₹")
        category = subscription_data.get("category", "general")
        request_type = subscription_data.get("request_type", "DISCOUNT_REQUEST")

        discount_pct = 35.0 if request_type == "TIER_DOWNGRADE" else 25.0
        offered_price = round(current_amount * (1.0 - (discount_pct / 100.0)), 2)
        monthly_saving = round(current_amount - offered_price, 2)
        annual_saving = round(monthly_saving * 12.0, 2)

        negotiation_intel = llm_provider.draft_negotiation_pitch(
            merchant=merchant,
            current_price=current_amount,
            currency=currency,
            category=category,
            discount_percent=discount_pct,
            offered_price=offered_price,
            request_type=request_type
        )

        return {
            "merchant": merchant,
            "original_price": current_amount,
            "offered_price": offered_price,
            "discount_percent": discount_pct,
            "monthly_saving": monthly_saving,
            "annual_saving": annual_saving,
            "pitch_letter": negotiation_intel["pitch"],
            "merchant_reply": negotiation_intel["reply"],
            "status": "pending_acceptance",
            "request_type": request_type
        }

    def send_negotiation_to_merchant(
        self,
        db: Session,
        user_id: str,
        subscription: Subscription,
        request_type: str = "DISCOUNT_REQUEST",
        target_discount_pct: float = 25.0,
        channel: str = "REST_API"
    ) -> MerchantCommunication:
        """
        Drafts and dispatches an autonomous negotiation request to the merchant communication channel.
        Tracks request and sets subscription status to 'negotiating'.
        """
        # Guardrail checks
        category_lower = (subscription.category or "").lower().strip()
        protected = ["insurance", "loan_payment", "healthcare", "utility", "education"]
        if any(p in category_lower for p in protected):
            raise HTTPException(
                status_code=403,
                detail=f"Negotiation is not permitted for protected category '{subscription.category}'. Safety guardrails block modification of essential policies."
            )

        if subscription.status == "cancelled":
            raise HTTPException(
                status_code=400,
                detail="Cannot negotiate an already cancelled subscription."
            )

        # Check for existing active communication
        existing_comm = db.query(MerchantCommunication).filter(
            MerchantCommunication.subscription_id == subscription.id,
            MerchantCommunication.status.in_(["SENT", "RECEIVED_BY_MERCHANT"])
        ).first()
        if existing_comm:
            return existing_comm

        is_downgrade = (request_type == "TIER_DOWNGRADE")
        eff_pct = 35.0 if is_downgrade else target_discount_pct
        target_price = round(subscription.amount * (1.0 - (eff_pct / 100.0)), 2)

        # Draft natural language pitch & staged reply via LLM
        intel = llm_provider.draft_negotiation_pitch(
            merchant=subscription.merchant,
            current_price=subscription.amount,
            currency=subscription.currency or "₹",
            category=subscription.category or "general",
            discount_percent=eff_pct,
            offered_price=target_price,
            request_type=request_type
        )

        subject = (
            f"Plan Downgrade Request: {subscription.merchant}"
            if is_downgrade else
            f"Retention Rate Inquiry: {subscription.merchant}"
        )

        comm = MerchantCommunication(
            user_id=user_id,
            subscription_id=subscription.id,
            merchant=subscription.merchant,
            channel=channel,
            request_type=request_type,
            original_price=subscription.amount,
            target_price=target_price,
            target_discount_pct=eff_pct,
            pitch_subject=subject,
            pitch_message=intel["pitch"],
            status="SENT",
            merchant_reply_text=intel["reply"],
            merchant_counter_price=target_price,
            created_at=datetime.datetime.utcnow()
        )
        db.add(comm)

        # Update subscription state
        subscription.status = "negotiating"

        # Also maintain a synced NegotiationOffer record for legacy modal UI compatibility
        existing_offer = db.query(NegotiationOffer).filter(
            NegotiationOffer.subscription_id == subscription.id,
            NegotiationOffer.status == "pending_acceptance"
        ).first()

        if not existing_offer:
            offer = NegotiationOffer(
                subscription_id=subscription.id,
                merchant=subscription.merchant,
                original_price=subscription.amount,
                offered_price=target_price,
                discount_percent=eff_pct,
                monthly_saving=round(subscription.amount - target_price, 2),
                annual_saving=round((subscription.amount - target_price) * 12.0, 2),
                pitch_letter=intel["pitch"],
                merchant_reply=intel["reply"],
                status="pending_acceptance",
                created_at=datetime.datetime.utcnow()
            )
            db.add(offer)

        db.commit()
        db.refresh(comm)
        return comm

    def evaluate_and_apply_merchant_response(
        self,
        db: Session,
        user_id: str,
        communication_id: int,
        outcome: str,
        counter_price: Optional[float] = None,
        response_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Agent evaluates incoming merchant response (ACCEPTED vs REJECTED).
        Handles accepted discount/downgrade or executes fallback cancellation if rejected.
        """
        comm = db.query(MerchantCommunication).filter(
            MerchantCommunication.id == communication_id
        ).first()

        if not comm:
            raise HTTPException(status_code=404, detail="Merchant communication thread not found.")

        sub = db.query(Subscription).filter(Subscription.id == comm.subscription_id).first()
        if not sub:
            raise HTTPException(status_code=404, detail="Associated subscription not found.")

        outcome_norm = outcome.upper().strip()
        now_time = datetime.datetime.utcnow()

        # Idempotency check: if communication already finalized, return current status
        if comm.status in ["MERCHANT_ACCEPTED", "MERCHANT_REJECTED", "MERCHANT_FAILED", "MERCHANT_DECLINED", "MERCHANT_EXPIRED"]:
            return {
                "success": True,
                "status": comm.merchant_outcome or ("ACCEPTED" if "ACCEPTED" in comm.status else "FAILED"),
                "merchant": sub.merchant,
                "resulting_action": comm.resulting_action or ("APPLIED_DISCOUNT" if "ACCEPTED" in comm.status else "ORIGINAL_PRICE_MAINTAINED"),
                "subscription_status": sub.status,
                "new_price": sub.amount,
                "monthly_savings": comm.monthly_saving or 0.0,
                "annual_savings": comm.annual_saving or 0.0,
                "agent_evaluation": comm.agent_evaluation or "",
                "communication": comm
            }

        if outcome_norm == "ACCEPTED":
            new_price = counter_price if (counter_price and counter_price > 0) else comm.target_price
            monthly_saving = round(comm.original_price - new_price, 2)
            annual_saving = round(monthly_saving * 12.0, 2)

            evaluation = llm_provider.evaluate_negotiation_outcome(
                merchant=comm.merchant,
                outcome="ACCEPTED",
                original_price=comm.original_price,
                new_price=new_price,
                savings=monthly_saving,
                currency=sub.currency or "₹",
                resulting_action="APPLIED_DISCOUNT"
            )

            # Update subscription
            sub.amount = new_price
            sub.status = "negotiated"
            sub.action_taken = "NEGOTIATED_DISCOUNT"
            sub.decision_reason = evaluation

            # Update communication record
            comm.status = "MERCHANT_ACCEPTED"
            comm.merchant_outcome = "ACCEPTED"
            comm.merchant_counter_price = new_price
            if response_text:
                comm.merchant_reply_text = response_text
            comm.agent_evaluation = evaluation
            comm.resulting_action = "APPLIED_DISCOUNT"
            comm.monthly_saving = monthly_saving
            comm.annual_saving = annual_saving
            comm.responded_at = now_time
            comm.evaluated_at = now_time

            # Update legacy offer record if linked
            offer = db.query(NegotiationOffer).filter(
                NegotiationOffer.subscription_id == sub.id,
                NegotiationOffer.status.in_(["pending", "pending_acceptance"])
            ).first()
            if offer:
                offer.status = "accepted"

            # Log audit event idempotently
            existing_log = db.query(ActionLog).filter(
                ActionLog.user_id == user_id,
                ActionLog.subscription_id == sub.id,
                ActionLog.action_type == "NEGOTIATION_ACCEPTED"
            ).first()
            if not existing_log:
                action_log = ActionLog(
                    user_id=user_id,
                    subscription_id=sub.id,
                    merchant=sub.merchant,
                    action_type="NEGOTIATION_ACCEPTED",
                    reason=evaluation,
                    waste_score=sub.waste_score or 5,
                    confidence=sub.confidence_score or 0.95,
                    amount=new_price,
                    monthly_saving=monthly_saving,
                    annual_saving=annual_saving,
                    timestamp=now_time,
                    extra_details={
                        "communication_id": comm.id,
                        "original_price": comm.original_price,
                        "new_price": new_price,
                        "discount_percent": comm.target_discount_pct,
                        "request_type": comm.request_type
                    }
                )
                db.add(action_log)
            db.commit()
            db.refresh(sub)
            db.refresh(comm)

            return {
                "success": True,
                "status": "ACCEPTED",
                "merchant": sub.merchant,
                "resulting_action": "APPLIED_DISCOUNT",
                "subscription_status": sub.status,
                "new_price": sub.amount,
                "monthly_savings": monthly_saving,
                "annual_savings": annual_saving,
                "agent_evaluation": evaluation,
                "communication": comm
            }

        else:
            # REJECTED, FAILED, DECLINED, EXPIRED, or NO_OFFER
            rejection_text = response_text or llm_provider.draft_merchant_rejection_reply(
                merchant=comm.merchant,
                current_price=comm.original_price,
                currency=sub.currency or "₹"
            )

            evaluation = llm_provider.evaluate_negotiation_outcome(
                merchant=comm.merchant,
                outcome=outcome_norm,
                original_price=comm.original_price,
                new_price=comm.original_price,
                savings=0.0,
                currency=sub.currency or "₹",
                resulting_action="ORIGINAL_PRICE_MAINTAINED"
            )

            # Subscription price strictly remains the original price
            sub.amount = comm.original_price
            sub.status = "active"
            sub.decision_reason = evaluation

            # Update communication record
            comm.status = f"MERCHANT_{outcome_norm}"
            comm.merchant_outcome = outcome_norm
            comm.merchant_reply_text = rejection_text
            comm.agent_evaluation = evaluation
            comm.resulting_action = "ORIGINAL_PRICE_MAINTAINED"
            comm.monthly_saving = 0.0
            comm.annual_saving = 0.0
            comm.responded_at = now_time
            comm.evaluated_at = now_time

            # Update legacy offer record
            offer = db.query(NegotiationOffer).filter(
                NegotiationOffer.subscription_id == sub.id,
                NegotiationOffer.status.in_(["pending", "pending_acceptance"])
            ).first()
            if offer:
                offer.status = "declined" if outcome_norm == "DECLINED" else ("expired" if outcome_norm == "EXPIRED" else "failed")

            # Determine ActionLog action_type
            action_type = "NEGOTIATION_DECLINED" if outcome_norm == "DECLINED" else "NEGOTIATION_FAILED"

            # Check if ActionLog already recorded
            existing_log = db.query(ActionLog).filter(
                ActionLog.user_id == user_id,
                ActionLog.subscription_id == sub.id,
                ActionLog.action_type == action_type
            ).first()

            if not existing_log:
                db.add(ActionLog(
                    user_id=user_id,
                    subscription_id=sub.id,
                    merchant=sub.merchant,
                    action_type=action_type,
                    reason=f"Negotiation {outcome_norm.lower()}. Subscription maintained at original price of {sub.currency or '₹'}{comm.original_price:,.2f}.",
                    waste_score=sub.waste_score or 0,
                    confidence=sub.confidence_score or 0.95,
                    amount=comm.original_price,
                    monthly_saving=0.0,
                    annual_saving=0.0,
                    timestamp=now_time,
                    extra_details={
                        "communication_id": comm.id,
                        "original_price": comm.original_price,
                        "final_price": comm.original_price,
                        "outcome": outcome_norm
                    }
                ))

            db.commit()
            db.refresh(sub)
            db.refresh(comm)

            return {
                "success": True,
                "status": outcome_norm,
                "merchant": sub.merchant,
                "resulting_action": "ORIGINAL_PRICE_MAINTAINED",
                "subscription_status": sub.status,
                "new_price": comm.original_price,
                "monthly_savings": 0.0,
                "annual_savings": 0.0,
                "agent_evaluation": evaluation,
                "communication": comm
            }

    def simulate_test_merchant(
        self,
        db: Session,
        user_id: str,
        subscription_id: int,
        simulate_outcome: str = "ACCEPTED",
        request_type: str = "DISCOUNT_REQUEST"
    ) -> Dict[str, Any]:
        """
        Complete end-to-end Test Merchant simulation:
        1. Test merchant receives negotiation request
        2. Test merchant generates response (ACCEPTED or REJECTED)
        3. Agent evaluates and handles response correctly
        """
        sub = db.query(Subscription).filter(
            Subscription.id == subscription_id,
            Subscription.user_id == user_id
        ).first()
        if not sub:
            raise HTTPException(status_code=404, detail="Subscription not found")

        # Step 1 & 2: Send request to test merchant
        comm = self.send_negotiation_to_merchant(
            db=db,
            user_id=user_id,
            subscription=sub,
            request_type=request_type
        )

        # Step 3 & 4: Evaluate test merchant response
        result = self.evaluate_and_apply_merchant_response(
            db=db,
            user_id=user_id,
            communication_id=comm.id,
            outcome=simulate_outcome
        )

        return result

    def get_communications(
        self,
        db: Session,
        user_id: str,
        subscription_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[MerchantCommunication]:
        """Lists merchant communications filtered by user, subscription, and status."""
        query = db.query(MerchantCommunication).filter(MerchantCommunication.user_id == user_id)
        if subscription_id:
            query = query.filter(MerchantCommunication.subscription_id == subscription_id)
        if status:
            query = query.filter(MerchantCommunication.status == status)
        return query.order_by(MerchantCommunication.created_at.desc()).all()

negotiation_agent = NegotiationAgent()
