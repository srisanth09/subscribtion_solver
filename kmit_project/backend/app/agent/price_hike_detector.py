from typing import Dict, Any, List

class PriceHikeDetector:
    """
    Detects price increases against historical transactions or billing emails,
    and predicts upcoming price hikes based on annual adjustment cycles.
    """
    
    def evaluate_price_hikes(self, subscription: Dict[str, Any], email_intel: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consolidates price hike information from transaction history and email alerts.
        """
        merchant_norm = subscription["merchant"].lower().strip()
        intel = email_intel.get(merchant_norm, {})
        
        email_hike = intel.get("price_hike")
        tx_hike = subscription.get("price_hike_detected", False)
        
        price_hike_detected = tx_hike or bool(email_hike)
        old_price = subscription.get("old_price")
        hike_pct = subscription.get("hike_percentage", 0.0)
        
        if email_hike:
            old_price = email_hike.get("old_price", old_price)
            hike_pct = email_hike.get("percentage", hike_pct)

        # Stretch: Price-Hike Prediction
        # If subscription has been stable for ~11 months without price change, flag upcoming risk
        predicted_hike_risk = False
        prediction_reason = None
        if subscription.get("transaction_count", 0) >= 11 and not price_hike_detected:
            if subscription["merchant"].lower() in ["netflix", "canva pro", "disney+", "adobe"]:
                predicted_hike_risk = True
                prediction_reason = "Approaching 12-month tenure. Historical provider trend indicates periodic 10-15% annual revision."

        return {
            "price_hike_detected": price_hike_detected,
            "old_price": old_price,
            "hike_percentage": hike_pct,
            "predicted_hike_risk": predicted_hike_risk,
            "prediction_reason": prediction_reason
        }

price_hike_detector = PriceHikeDetector()
