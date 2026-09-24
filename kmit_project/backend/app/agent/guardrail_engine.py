from typing import Dict, Any, List

class GuardrailEngine:
    """
    Deterministic Safety & Policy Enforcement Engine.
    Guarantees the AI agent never takes high-risk financial actions autonomously.
    """

    def evaluate(self, subscription: Dict[str, Any], guardrail_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a candidate subscription against active user guardrails.
        
        Returns:
            status: "PASSED", "BLOCKED_PROTECTED", "BLOCKED_LIMIT", "BLOCKED_AMBIGUOUS_DUPLICATE", "BLOCKED_LOW_CONFIDENCE"
            decision: "AUTO_CANCEL", "ESCALATE_APPROVAL", "KEEP", "AUTO_DOWNGRADE"
            reason: Plain English explanation of the guardrail ruling
        """
        merchant = subscription.get("merchant", "Service")
        category = subscription.get("category", "").lower().strip()
        amount = subscription.get("amount", 0.0)
        days_inactive = subscription.get("last_used_days_ago", 0)
        waste_score = subscription.get("waste_score", 0)
        confidence = subscription.get("confidence_score", 0.0)
        is_duplicate = subscription.get("is_duplicate_detected", False)

        auto_action_limit = guardrail_config.get("auto_action_limit", 2000.0)
        protected_categories = [c.lower().strip() for c in guardrail_config.get("protected_categories", [])]
        min_confidence = guardrail_config.get("min_confidence_threshold", 0.85)
        require_approval_for_duplicates = guardrail_config.get("require_approval_for_duplicates", True)

        # -------------------------------------------------------------
        # Rule 1: Protected Categories (HIGHEST PRIORITY)
        # -------------------------------------------------------------
        if category in protected_categories or any(p in category for p in protected_categories):
            return {
                "status": "BLOCKED_PROTECTED",
                "decision": "ESCALATE_APPROVAL",
                "reason_code": "PROTECTED_CATEGORY",
                "message": f"Category '{category}' is designated as strictly protected (e.g., insurance, loan, healthcare). Autonomous action is prohibited.",
                "passed": False
            }

        # -------------------------------------------------------------
        # Rule 2: Actively Used Subscriptions
        # -------------------------------------------------------------
        if days_inactive <= 7 and not is_duplicate and not subscription.get("price_hike_detected"):
            return {
                "status": "PASSED",
                "decision": "KEEP",
                "reason_code": "ACTIVELY_USED",
                "message": f"Service was actively used {days_inactive} days ago. Providing regular utility.",
                "passed": True
            }

        # -------------------------------------------------------------
        # Rule 3: Duplicate / Overlapping Service (INPUT 2 SCENARIO)
        # If both services were used within 90 days, agent cannot assume user preference -> ESCALATE.
        # If inactive >= 90 days, it is clear abandoned waste rather than preference dilemma -> Proceed to waste scoring.
        # -------------------------------------------------------------
        if is_duplicate and require_approval_for_duplicates and days_inactive < 90:
            counterpart = subscription.get("duplicate_counterpart", "an alternate active service")
            return {
                "status": "BLOCKED_AMBIGUOUS_DUPLICATE",
                "decision": "ESCALATE_APPROVAL",
                "reason_code": "DUPLICATE_OVERLAP",
                "message": f"Multiple services detected in '{category}' (competes with {counterpart}). Human judgment required to determine user preference.",
                "passed": False
            }

        # -------------------------------------------------------------
        # Rule 4: Spending Limit (INPUT 1 vs Exceeded Limit)
        # -------------------------------------------------------------
        if amount > auto_action_limit:
            return {
                "status": "BLOCKED_LIMIT",
                "decision": "ESCALATE_APPROVAL",
                "reason_code": "EXCEEDS_LIMIT",
                "message": f"Recurring charge ({subscription.get('currency', '₹')}{amount:,.2f}) exceeds autonomous spending ceiling of {subscription.get('currency', '₹')}{auto_action_limit:,.2f}.",
                "passed": False
            }

        # -------------------------------------------------------------
        # Rule 5: Confidence Threshold
        # -------------------------------------------------------------
        if confidence < min_confidence:
            return {
                "status": "BLOCKED_LOW_CONFIDENCE",
                "decision": "ESCALATE_APPROVAL",
                "reason_code": "LOW_CONFIDENCE",
                "message": f"Agent decision confidence ({confidence:.0%}) is below the required safety threshold ({min_confidence:.0%}). Escalated for safety.",
                "passed": False
            }

        # -------------------------------------------------------------
        # Rule 6: High Waste Score & Under Limit -> AUTO-CANCEL (INPUT 1 SCENARIO)
        # -------------------------------------------------------------
        if waste_score >= 70:
            return {
                "status": "PASSED",
                "decision": "AUTO_CANCEL",
                "reason_code": "CLEAR_WASTE_SAFE",
                "message": f"Unused for {days_inactive} days, high waste score ({waste_score}/100), and cost is strictly under the auto-action limit.",
                "passed": True
            }

        # Default moderate waste
        return {
            "status": "PASSED",
            "decision": "ESCALATE_APPROVAL",
            "reason_code": "MODERATE_WASTE",
            "message": f"Moderate waste score ({waste_score}/100). Flagged for user visibility.",
            "passed": True
        }

guardrail_engine = GuardrailEngine()
