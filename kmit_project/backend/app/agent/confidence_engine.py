from typing import Dict, Any

class ConfidenceEngine:
    """
    Computes a Confidence Score (0.0 - 1.0) indicating how certain the AI agent
    is that its assessment and recommended action are unequivocally correct.
    """

    def calculate_confidence(self, subscription: Dict[str, Any]) -> float:
        days_inactive = subscription.get("last_used_days_ago", 0)
        is_duplicate = subscription.get("is_duplicate_detected", False)
        is_bundled = subscription.get("is_bundled", False)
        category = subscription.get("category", "").lower()
        tx_count = subscription.get("transaction_count", 1)

        # Baseline confidence based on transaction consistency
        confidence = 0.80
        if tx_count >= 3:
            confidence += 0.10

        # Unambiguous extreme inactivity (> 120 days)
        if days_inactive >= 120:
            confidence += 0.08

        # Crucial Ambiguity Factor:
        # If there are duplicate/overlapping services in the same category where both have recent activity (< 90 days),
        # the agent cannot assume user preference, so confidence is lowered to 0.65 to ensure human approval.
        # If inactive >= 90 days, it is unambiguous abandoned waste (high confidence).
        if is_duplicate and days_inactive < 90:
            confidence = min(confidence, 0.65)

        # If bundle coverage is detected, moderate confidence (user might prefer standalone app)
        if is_bundled and not is_duplicate:
            confidence = min(confidence, 0.75)

        # Actively used services have high confidence to KEEP
        if days_inactive <= 7:
            confidence = 0.96

        # Protected categories have 0.99 confidence in being protected
        if category in ["insurance", "loan_payment", "healthcare", "utility", "education"]:
            confidence = 0.99

        return round(max(0.1, min(0.99, confidence)), 2)

confidence_engine = ConfidenceEngine()
