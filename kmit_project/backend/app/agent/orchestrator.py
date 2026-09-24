import datetime
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session

from app.models import (
    User, GuardrailConfig, Transaction, EmailLog, Subscription, ActionLog
)
from app.agent.transaction_parser import transaction_parser
from app.agent.email_analyzer import email_analyzer
from app.agent.bundle_detector import bundle_detector
from app.agent.price_hike_detector import price_hike_detector
from app.agent.waste_analyzer import waste_analyzer
from app.agent.confidence_engine import confidence_engine
from app.agent.guardrail_engine import guardrail_engine
from app.agent.action_executor import action_executor
from app.agent.llm_provider import llm_provider
from app.agent.negotiation_agent import negotiation_agent

class AgentOrchestrator:
    """
    The Central Brain:
    Orchestrates the entire multi-stage Agentic AI lifecycle:
    Perceive -> Reason -> Check Guardrails -> Act -> Log Audit Trail.
    """

    def run_full_audit(self, db: Session, user_id: str = "u_301", user_prompt: str = "Scan my subscriptions") -> Dict[str, Any]:
        audit_trace = []
        now_str = datetime.datetime.utcnow().strftime("%H:%M:%S")

        # Step 1: Perceive - Ingest Data
        audit_trace.append({
            "step": "PERCEIVE_INPUT",
            "message": f"Received user prompt: '{user_prompt}' for user {user_id}",
            "status": "SUCCESS",
            "timestamp": now_str,
            "details": {"user_id": user_id, "prompt": user_prompt}
        })

        # Load user guardrails
        guardrail_obj = db.query(GuardrailConfig).filter(GuardrailConfig.user_id == user_id).first()
        if not guardrail_obj:
            guardrail_obj = GuardrailConfig(
                user_id=user_id,
                auto_action_limit=2000.0,
                protected_categories=["insurance", "loan_payment", "healthcare", "utility", "education"],
                min_confidence_threshold=0.85,
                require_approval_for_duplicates=True,
                negotiation_mode=False
            )
            db.add(guardrail_obj)
            db.commit()

        guardrail_dict = {
            "auto_action_limit": guardrail_obj.auto_action_limit,
            "protected_categories": guardrail_obj.protected_categories or [],
            "min_confidence_threshold": guardrail_obj.min_confidence_threshold,
            "require_approval_for_duplicates": guardrail_obj.require_approval_for_duplicates,
            "negotiation_mode": getattr(guardrail_obj, "negotiation_mode", False)
        }

        # Retrieve raw transactions and emails
        raw_txs = db.query(Transaction).filter(Transaction.user_id == user_id).all()
        tx_list = [
            {
                "transaction_id": t.transaction_id,
                "merchant": t.merchant,
                "amount": t.amount,
                "currency": t.currency,
                "date": t.date,
                "category": t.category,
                "description": t.description
            }
            for t in raw_txs
        ]

        raw_emails = db.query(EmailLog).filter(EmailLog.user_id == user_id).all()
        email_list = [
            {
                "sender": e.sender,
                "subject": e.subject,
                "body": e.body,
                "date": e.date,
                "event_type": e.event_type,
                "extracted_data": e.extracted_data
            }
            for e in raw_emails
        ]

        audit_trace.append({
            "step": "DATA_INGESTION",
            "message": f"Retrieved {len(tx_list)} transactions across 12 months and {len(email_list)} billing emails.",
            "status": "SUCCESS",
            "timestamp": now_str,
            "details": {"tx_count": len(tx_list), "email_count": len(email_list)}
        })

        # Step 2: Detect - Recurring Subscriptions & Email Events
        detected_subs = transaction_parser.detect_recurring_charges(tx_list)
        email_intel = email_analyzer.analyze_emails(email_list)

        # Sync and include all subscriptions stored in database (including manually added or edited entries)
        db_subs = db.query(Subscription).filter(Subscription.user_id == user_id).all()
        db_subs_map = {s.merchant.lower(): s for s in db_subs}

        # 1. Update detected subscriptions with manual user overrides from database
        for s in detected_subs:
            m_key = s["merchant"].lower()
            if m_key in db_subs_map:
                db_s = db_subs_map[m_key]
                if db_s.last_used_days_ago is not None:
                    s["last_used_days_ago"] = db_s.last_used_days_ago
                if db_s.amount is not None:
                    s["amount"] = db_s.amount
                if db_s.currency:
                    s["currency"] = db_s.currency
                if db_s.category:
                    s["category"] = db_s.category
                if db_s.cadence:
                    s["cadence"] = db_s.cadence
                if db_s.is_duplicate_detected is not None:
                    s["is_duplicate_detected"] = db_s.is_duplicate_detected
                if db_s.duplicate_counterpart:
                    s["duplicate_counterpart"] = db_s.duplicate_counterpart
                if db_s.is_bundled is not None:
                    s["is_bundled"] = db_s.is_bundled
                if db_s.bundle_provider:
                    s["bundle_provider"] = db_s.bundle_provider
                if db_s.trial_converted is not None:
                    s["trial_converted"] = db_s.trial_converted
                if db_s.old_price is not None:
                    s["old_price"] = db_s.old_price
                    s["price_hike_detected"] = db_s.price_hike_detected
                    s["hike_percentage"] = db_s.hike_percentage

        # 2. Append any subscriptions from database that were not in raw transactions
        existing_merchants = {s["merchant"].lower() for s in detected_subs}
        for db_s in db_subs:
            if db_s.merchant.lower() not in existing_merchants:
                detected_subs.append({
                    "merchant": db_s.merchant,
                    "amount": db_s.amount,
                    "currency": db_s.currency,
                    "cadence": db_s.cadence or "monthly",
                    "category": db_s.category or "general",
                    "last_used_days_ago": db_s.last_used_days_ago or 0,
                    "is_duplicate_detected": db_s.is_duplicate_detected or False,
                    "duplicate_category": db_s.duplicate_category,
                    "duplicate_counterpart": db_s.duplicate_counterpart,
                    "is_bundled": db_s.is_bundled or False,
                    "bundle_provider": db_s.bundle_provider,
                    "bundle_description": db_s.bundle_description,
                    "is_free_trial": db_s.is_free_trial or False,
                    "trial_converted": db_s.trial_converted or False,
                    "old_price": db_s.old_price,
                    "price_hike_detected": db_s.price_hike_detected or False,
                    "hike_percentage": db_s.hike_percentage or 0.0,
                    "transaction_count": 6
                })
                existing_merchants.add(db_s.merchant.lower())

        audit_trace.append({
            "step": "RECURRING_DETECTION",
            "message": f"Identified {len(detected_subs)} active recurring subscription streams from transaction cadences and manual portfolio entries.",
            "status": "SUCCESS",
            "timestamp": now_str,
            "details": {"subscriptions_found": [s["merchant"] for s in detected_subs]}
        })

        # Cross-reference bundles and duplicates
        detected_subs = bundle_detector.check_bundles_and_duplicates(detected_subs)

        # Process each subscription through intelligence and guardrails
        auto_cancelled_count = 0
        escalated_count = 0
        protected_count = 0
        active_kept_count = 0
        potential_monthly_savings = 0.0
        currency = "₹"

        for sub_data in detected_subs:
            merchant = sub_data["merchant"]
            currency = sub_data.get("currency", "₹")
            
            # Price Hike Analysis
            hike_info = price_hike_detector.evaluate_price_hikes(sub_data, email_intel)
            sub_data["price_hike_detected"] = hike_info["price_hike_detected"]
            sub_data["old_price"] = hike_info["old_price"]
            sub_data["hike_percentage"] = hike_info["hike_percentage"]
            
            # Email next billing date
            norm_m = merchant.lower().strip()
            if norm_m in email_intel and email_intel[norm_m].get("next_billing_date"):
                sub_data["next_billing_date"] = email_intel[norm_m]["next_billing_date"]

            # Step 3: Decide - Waste Score & Confidence Score
            waste_score = waste_analyzer.calculate_waste_score(sub_data)
            sub_data["waste_score"] = waste_score

            confidence = confidence_engine.calculate_confidence(sub_data)
            sub_data["confidence_score"] = confidence

            # Step 4: Guardrail Safety Enforcement
            guardrail_res = guardrail_engine.evaluate(sub_data, guardrail_dict)
            sub_data["guardrail_status"] = guardrail_res["status"]
            sub_data["decision"] = guardrail_res["decision"]

            # Generate natural language explanation via LLM reasoner
            explanation = llm_provider.generate_decision_explanation(sub_data, guardrail_res)
            sub_data["decision_reason"] = explanation

            # Upsert into database
            db_sub = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.merchant == merchant
            ).first()

            if not db_sub:
                db_sub = Subscription(user_id=user_id, merchant=merchant)
                db.add(db_sub)
                db.flush()

            # Check if this subscription is already cancelled or already has an AUTO_CANCEL log
            existing_cancel_log = db.query(ActionLog).filter(
                ActionLog.user_id == user_id,
                ActionLog.action_type.in_(["AUTO_CANCEL", "USER_APPROVED_CANCEL"]),
                (ActionLog.subscription_id == db_sub.id) | (ActionLog.merchant == merchant)
            ).first()

            is_already_cancelled = (db_sub.status == "cancelled") or (existing_cancel_log is not None)
            is_already_kept = (db_sub.status == "kept")

            if is_already_cancelled:
                db_sub.status = "cancelled"
                if not db_sub.action_taken:
                    db_sub.action_taken = "AUTO_CANCELLED"
                db_sub.decision = "AUTO_CANCEL"
                db_sub.decision_reason = explanation
                db.commit()

                auto_cancelled_count += 1
                potential_monthly_savings += db_sub.amount

                audit_trace.append({
                    "step": "ALREADY_CANCELLED",
                    "message": f"ALREADY CANCELLED: {merchant} ({currency}{db_sub.amount:,.2f}/mo) was previously cancelled. Skipping duplicate action.",
                    "status": "INFO",
                    "timestamp": now_str,
                    "details": {"merchant": merchant, "saving": db_sub.amount, "already_cancelled": True}
                })
                continue

            if is_already_kept:
                active_kept_count += 1
                audit_trace.append({
                    "step": "SERVICE_RETAINED",
                    "message": f"KEPT ACTIVE: {merchant} ({currency}{db_sub.amount:,.2f}/mo) was intentionally retained by user.",
                    "status": "INFO",
                    "timestamp": now_str,
                    "details": {"merchant": merchant, "user_kept": True}
                })
                continue

            is_already_negotiated = (db_sub.status == "negotiated")
            existing_accepted_log = db.query(ActionLog).filter(
                ActionLog.user_id == user_id,
                (ActionLog.subscription_id == db_sub.id) | (ActionLog.merchant == merchant),
                ActionLog.action_type == "NEGOTIATION_ACCEPTED"
            ).first()

            if is_already_negotiated or existing_accepted_log:
                db_sub.status = "negotiated"
                active_kept_count += 1
                audit_trace.append({
                    "step": "NEGOTIATED_ACTIVE",
                    "message": f"NEGOTIATED ACTIVE: {merchant} is active at negotiated discount rate of {currency}{db_sub.amount:,.2f}/mo.",
                    "status": "INFO",
                    "timestamp": now_str,
                    "details": {"merchant": merchant, "negotiated": True, "discounted_amount": db_sub.amount}
                })
                continue

            existing_neg_log = db.query(ActionLog).filter(
                ActionLog.user_id == user_id,
                (ActionLog.subscription_id == db_sub.id) | (ActionLog.merchant == merchant),
                ActionLog.action_type.in_(["NEGOTIATION_FAILED", "NEGOTIATION_DECLINED"])
            ).first()

            if existing_neg_log:
                active_kept_count += 1
                audit_trace.append({
                    "step": "NEGOTIATION_RETAINED",
                    "message": f"NEGOTIATION RETAINED: {merchant} ({currency}{db_sub.amount:,.2f}/mo) maintained at original price following {existing_neg_log.action_type.lower()}.",
                    "status": "INFO",
                    "timestamp": now_str,
                    "details": {"merchant": merchant, "original_amount": db_sub.amount, "action_type": existing_neg_log.action_type}
                })
                continue

            is_currently_negotiating = (db_sub.status == "negotiating")
            if is_currently_negotiating:
                audit_trace.append({
                    "step": "NEGOTIATION_IN_PROGRESS",
                    "message": f"NEGOTIATING: {merchant} has an active retention offer pending your decision.",
                    "status": "INFO",
                    "timestamp": now_str,
                    "details": {"merchant": merchant, "negotiating": True}
                })
                continue

            db_sub.amount = sub_data["amount"]
            db_sub.currency = currency
            db_sub.cadence = sub_data["cadence"]
            db_sub.category = sub_data["category"]
            db_sub.last_used_days_ago = sub_data["last_used_days_ago"]
            db_sub.waste_score = waste_score
            db_sub.confidence_score = confidence
            db_sub.price_hike_detected = sub_data["price_hike_detected"]
            db_sub.old_price = sub_data["old_price"]
            db_sub.hike_percentage = sub_data["hike_percentage"]
            db_sub.is_duplicate_detected = sub_data.get("is_duplicate_detected", False)
            db_sub.duplicate_category = sub_data.get("duplicate_category")
            db_sub.duplicate_counterpart = sub_data.get("duplicate_counterpart")
            db_sub.is_bundled = sub_data.get("is_bundled", False)
            db_sub.bundle_provider = sub_data.get("bundle_provider")
            db_sub.bundle_description = sub_data.get("bundle_description")
            db_sub.guardrail_status = guardrail_res["status"]
            db_sub.decision = guardrail_res["decision"]
            db_sub.decision_reason = explanation
            db_sub.trial_converted = sub_data.get("trial_converted", False)
            db_sub.next_billing_date = sub_data.get("next_billing_date", "2026-10-01")

            db.commit()
            db.refresh(db_sub)

            # Step 5: Act - Autonomous execution or Human Escalation
            if guardrail_res["decision"] == "AUTO_CANCEL":
                is_neg_mode = guardrail_dict.get("negotiation_mode", False) or ("negotiat" in user_prompt.lower())
                if is_neg_mode:
                    comm = negotiation_agent.send_negotiation_to_merchant(
                        db=db,
                        user_id=user_id,
                        subscription=db_sub,
                        request_type="DISCOUNT_REQUEST"
                    )
                    pot_saving = round(comm.original_price - comm.target_price, 2)
                    potential_monthly_savings += pot_saving
                    audit_trace.append({
                        "step": "NEGOTIATION_MODE_ENGAGED",
                        "message": f"NEGOTIATION MODE: Contacted merchant {merchant} with a discount request (target: {currency}{comm.target_price:,.2f}/mo) before cancelling. Awaiting merchant reply.",
                        "status": "INFO",
                        "timestamp": now_str,
                        "details": {
                            "merchant": merchant,
                            "original_price": comm.original_price,
                            "target_price": comm.target_price,
                            "communication_id": comm.id
                        }
                    })
                else:
                    # Safe auto-cancel (e.g., StreamFlix, Gym)
                    action_executor.execute_auto_cancel(
                        db=db,
                        user_id=user_id,
                        sub=db_sub,
                        reason=explanation,
                        confidence=confidence,
                        waste_score=waste_score
                    )
                    auto_cancelled_count += 1
                    potential_monthly_savings += db_sub.amount
                    audit_trace.append({
                        "step": "AUTO_CANCEL_EXECUTED",
                        "message": f"AUTO-CANCELLED: {merchant} ({currency}{db_sub.amount:,.2f}/mo). Waste: {waste_score}/100, Confidence: {confidence:.0%}. Reason: {explanation}",
                        "status": "SUCCESS",
                        "timestamp": now_str,
                        "details": {"merchant": merchant, "saving": db_sub.amount}
                    })

            elif guardrail_res["status"] == "BLOCKED_PROTECTED":
                # Protected category (e.g., HealthGuard Insurance, Loan EMI)
                action_executor.execute_escalation(
                    db=db,
                    user_id=user_id,
                    sub=db_sub,
                    reason=explanation,
                    confidence=confidence,
                    waste_score=waste_score,
                    guardrail_status=guardrail_res["status"]
                )
                protected_count += 1
                audit_trace.append({
                    "step": "GUARDRAIL_BLOCKED_PROTECTED",
                    "message": f"BLOCKED: {merchant} ({currency}{db_sub.amount:,.2f}/mo) belongs to protected category '{db_sub.category}'. Autonomous cancellation prohibited.",
                    "status": "PROTECTED",
                    "timestamp": now_str,
                    "details": {"merchant": merchant, "category": db_sub.category}
                })

            elif guardrail_res["decision"] == "ESCALATE_APPROVAL":
                # Needs Human Review (e.g., TuneWave vs MusicBox, or Over Limit)
                action_executor.execute_escalation(
                    db=db,
                    user_id=user_id,
                    sub=db_sub,
                    reason=explanation,
                    confidence=confidence,
                    waste_score=waste_score,
                    guardrail_status=guardrail_res["status"]
                )
                escalated_count += 1
                potential_monthly_savings += db_sub.amount
                audit_trace.append({
                    "step": "ESCALATED_TO_HUMAN",
                    "message": f"ESCALATED: {merchant} ({currency}{db_sub.amount:,.2f}/mo) flagged for human review. Reason: {explanation}",
                    "status": "WARNING",
                    "timestamp": now_str,
                    "details": {"merchant": merchant, "reason": explanation}
                })

            elif guardrail_res["decision"] == "KEEP":
                db_sub.status = "active"
                db_sub.action_taken = "ACTIVE_KEPT"
                db.commit()
                active_kept_count += 1
                audit_trace.append({
                    "step": "SERVICE_RETAINED",
                    "message": f"KEPT ACTIVE: {merchant} ({currency}{db_sub.amount:,.2f}/mo) is actively used ({db_sub.last_used_days_ago} days ago).",
                    "status": "INFO",
                    "timestamp": now_str,
                    "details": {"merchant": merchant}
                })

        potential_annual_savings = round(potential_monthly_savings * 12, 2)

        audit_trace.append({
            "step": "AUDIT_COMPLETED",
            "message": f"Audit complete! {auto_cancelled_count} auto-cancelled, {escalated_count} awaiting approval, {protected_count} protected. Total potential monthly savings: {currency}{potential_monthly_savings:,.2f}.",
            "status": "SUCCESS",
            "timestamp": now_str,
            "details": {
                "monthly_savings": potential_monthly_savings,
                "annual_savings": potential_annual_savings
            }
        })

        return {
            "user_id": user_id,
            "status": "COMPLETED",
            "message": "Guardian subscription audit successfully executed.",
            "total_subscriptions_scanned": len(detected_subs),
            "auto_cancelled_count": auto_cancelled_count,
            "escalated_count": escalated_count,
            "protected_count": protected_count,
            "active_kept_count": active_kept_count,
            "potential_monthly_savings": round(potential_monthly_savings, 2),
            "potential_annual_savings": potential_annual_savings,
            "currency": currency,
            "audit_trace": audit_trace
        }

    def process_user_prompt(self, db: Session, user_id: str, prompt: str) -> Dict[str, Any]:
        """
        Classifies user prompt intent and executes either:
        1. Full/Targeted Agent Audit with custom instructions.
        2. Direct subscription action (e.g. 'cancel streamflix', 'negotiate cloudstorage').
        3. Financial Q&A / Telemetry inquiry (e.g. 'what is my total spend?', 'explain price hikes').
        """
        p_clean = prompt.strip()
        p_lower = p_clean.lower()
        now_str = datetime.datetime.utcnow().strftime("%H:%M:%S")

        # Negotiation Mode Toggle Commands
        if "enable negotiation mode" in p_lower or "turn on negotiation mode" in p_lower:
            guardrail_obj = db.query(GuardrailConfig).filter(GuardrailConfig.user_id == user_id).first()
            if guardrail_obj:
                guardrail_obj.negotiation_mode = True
                db.commit()
            return {
                "user_id": user_id,
                "prompt": prompt,
                "intent": "CONFIG_UPDATE",
                "reply": "Negotiation Mode enabled! The agent will now contact merchants with a generated downgrade or discount request before cancelling eligible subscriptions.",
                "action_taken": "NEGOTIATION_MODE_ENABLED",
                "monthly_savings": 0.0,
                "annual_savings": 0.0,
                "currency": "₹"
            }
        elif "disable negotiation mode" in p_lower or "turn off negotiation mode" in p_lower:
            guardrail_obj = db.query(GuardrailConfig).filter(GuardrailConfig.user_id == user_id).first()
            if guardrail_obj:
                guardrail_obj.negotiation_mode = False
                db.commit()
            return {
                "user_id": user_id,
                "prompt": prompt,
                "intent": "CONFIG_UPDATE",
                "reply": "Negotiation Mode disabled! The agent will execute immediate autonomous cancellations under guardrail limits.",
                "action_taken": "NEGOTIATION_MODE_DISABLED",
                "monthly_savings": 0.0,
                "annual_savings": 0.0,
                "currency": "₹"
            }

        # 1. Direct Cancel Command
        if p_lower.startswith("cancel "):
            target_name = p_clean[7:].strip()
            sub = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.merchant.ilike(f"%{target_name}%")
            ).first()
            if sub:
                action_executor.execute_auto_cancel(
                    db=db,
                    user_id=user_id,
                    sub=sub,
                    reason=f"User prompted explicit cancellation: '{prompt}'",
                    confidence=1.0,
                    waste_score=sub.waste_score or 100
                )
                reply = f"Successfully cancelled {sub.merchant}. You save {sub.currency}{sub.amount:,.2f}/month ({sub.currency}{sub.amount*12:,.2f}/year). Action logged to immutable audit trail."
                return {
                    "user_id": user_id,
                    "prompt": prompt,
                    "intent": "DIRECT_ACTION",
                    "reply": reply,
                    "action_taken": "CANCELLED",
                    "monthly_savings": sub.amount,
                    "annual_savings": sub.amount * 12,
                    "currency": sub.currency,
                    "data": {"merchant": sub.merchant, "amount": sub.amount}
                }

        # 2. Direct Negotiate Command
        if p_lower.startswith("negotiate "):
            target_name = p_clean[10:].strip()
            sub = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.merchant.ilike(f"%{target_name}%")
            ).first()
            if sub:
                # Check guardrails
                guardrail_obj = db.query(GuardrailConfig).filter(GuardrailConfig.user_id == user_id).first()
                protected_cats = [
                    c.lower().strip() 
                    for c in (guardrail_obj.protected_categories if guardrail_obj else ["insurance", "loan_payment", "healthcare", "utility", "education"])
                ]
                sub_cat = (sub.category or "").lower().strip()
                if sub_cat in protected_cats or any(p in sub_cat for p in protected_cats):
                    return {
                        "user_id": user_id,
                        "prompt": prompt,
                        "intent": "GUARDRAIL_BLOCKED",
                        "reply": f"Negotiation blocked for {sub.merchant}: '{sub.category}' is a strictly protected category (e.g. insurance, loans, utility). Automated modifications are prohibited.",
                        "action_taken": "BLOCKED",
                        "monthly_savings": 0.0,
                        "annual_savings": 0.0,
                        "currency": sub.currency,
                        "data": {"merchant": sub.merchant, "category": sub.category}
                    }

                from app.agent.negotiation_agent import negotiation_agent
                from app.models import NegotiationOffer

                # Check if pending offer exists
                offer = db.query(NegotiationOffer).filter(
                    NegotiationOffer.subscription_id == sub.id,
                    NegotiationOffer.status.in_(["pending", "pending_acceptance"])
                ).order_by(NegotiationOffer.created_at.desc()).first()

                if not offer:
                    offer_intel = negotiation_agent.initiate_negotiation({
                        "merchant": sub.merchant,
                        "amount": sub.amount,
                        "currency": sub.currency,
                        "category": sub.category
                    })
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

                pot_monthly = offer.monthly_saving or round(offer.original_price - offer.offered_price, 2)
                pot_annual = offer.annual_saving or round(pot_monthly * 12.0, 2)
                reply = (
                    f"Generated retention negotiation for {sub.merchant}.\n"
                    f"• Original Price: {sub.currency}{offer.original_price:,.2f}/mo\n"
                    f"• Proposed Discounted Price: {sub.currency}{offer.offered_price:,.2f}/mo ({offer.discount_percent:.0f}% discount)\n"
                    f"• Potential Savings: {sub.currency}{pot_monthly:,.2f}/mo ({sub.currency}{pot_annual:,.2f}/year)\n"
                    f"Review the offer on your dashboard and click 'Accept Offer' to apply this discount."
                )
                return {
                    "user_id": user_id,
                    "prompt": prompt,
                    "intent": "DIRECT_ACTION",
                    "reply": reply,
                    "action_taken": "NEGOTIATION_DRAFTED",
                    "monthly_savings": 0.0,
                    "annual_savings": 0.0,
                    "currency": sub.currency,
                    "data": {
                        "offer_id": offer.id,
                        "merchant": sub.merchant,
                        "offered_price": offer.offered_price,
                        "potential_monthly_savings": pot_monthly,
                        "potential_annual_savings": pot_annual
                    }
                }

        # 3. Audit Execution Intent
        audit_keywords = ["audit", "scan", "check all", "clean", "run", "input 1", "input 2", "input 3", "detect", "review all", "optimize"]
        is_audit = any(kw in p_lower for kw in audit_keywords)

        if is_audit or len(p_lower) < 10:
            audit_res = self.run_full_audit(db, user_id=user_id, user_prompt=prompt)
            summary_reply = llm_provider.generate_prompt_audit_summary(prompt, audit_res)
            return {
                "user_id": user_id,
                "prompt": prompt,
                "intent": "AUDIT_EXECUTION",
                "reply": summary_reply,
                "action_taken": "AUDIT_COMPLETED",
                "monthly_savings": audit_res["potential_monthly_savings"],
                "annual_savings": audit_res["potential_annual_savings"],
                "currency": audit_res["currency"],
                "audit_trace": audit_res["audit_trace"],
                "data": audit_res
            }

        # 4. Financial Query / Informational Inquiry Intent
        all_subs = db.query(Subscription).filter(Subscription.user_id == user_id).all()
        subs_data = [
            {
                "merchant": s.merchant,
                "amount": s.amount,
                "category": s.category,
                "status": s.status,
                "last_used_days_ago": s.last_used_days_ago,
                "waste_score": s.waste_score,
                "confidence_score": s.confidence_score,
                "price_hike_detected": s.price_hike_detected,
                "old_price": s.old_price,
                "hike_percentage": s.hike_percentage,
                "is_duplicate_detected": s.is_duplicate_detected,
                "duplicate_counterpart": s.duplicate_counterpart,
                "decision_reason": s.decision_reason
            }
            for s in all_subs
        ]

        monthly_cancelled = sum(s.amount for s in all_subs if s.status == "cancelled")
        guardrail_obj = db.query(GuardrailConfig).filter(GuardrailConfig.user_id == user_id).first()
        g_dict = {
            "auto_action_limit": guardrail_obj.auto_action_limit if guardrail_obj else 2000.0,
            "protected_categories": guardrail_obj.protected_categories if guardrail_obj else [],
            "min_confidence_threshold": guardrail_obj.min_confidence_threshold if guardrail_obj else 0.85,
            "require_approval_for_duplicates": guardrail_obj.require_approval_for_duplicates if guardrail_obj else True
        }

        context = {
            "currency": "₹",
            "subscriptions": subs_data,
            "savings": {
                "total_monthly_savings": monthly_cancelled,
                "total_annual_savings": monthly_cancelled * 12
            },
            "guardrails": g_dict
        }

        query_reply = llm_provider.answer_financial_query(prompt, context)
        return {
            "user_id": user_id,
            "prompt": prompt,
            "intent": "QUERY_ANSWER",
            "reply": query_reply,
            "action_taken": "INFORMATIONAL",
            "monthly_savings": monthly_cancelled,
            "annual_savings": monthly_cancelled * 12,
            "currency": "₹",
            "data": context
        }

orchestrator = AgentOrchestrator()

