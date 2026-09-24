from typing import Dict, Any

class WasteAnalyzer:
    """
    Computes an explainable, multi-factor Waste Score between 0 and 100.
    Factors:
      1. Days of Inactivity (0-50 pts)
      2. Duplicate / Category Overlap (0-25 pts)
      3. Unused Converted Free Trial (0-20 pts)
      4. Bundle Redundancy (0-20 pts)
      5. Recent Unscheduled Price Hike (0-15 pts)
      6. High Recurring Dollar Outflow (0-15 pts)
    """

    def calculate_waste_score(self, subscription: Dict[str, Any]) -> int:
        days_inactive = subscription.get("last_used_days_ago", 0)
        amount = subscription.get("amount", 0.0)
        is_duplicate = subscription.get("is_duplicate_detected", False)
        is_bundled = subscription.get("is_bundled", False)
        price_hike = subscription.get("price_hike_detected", False)
        trial_converted = subscription.get("trial_converted", False)
        
        score = 0

        # 1. Inactivity Points (Longer inactivity = severe financial waste)
        if days_inactive >= 180:
            score += 75
        elif days_inactive >= 90:
            score += 50
        elif days_inactive >= 60:
            score += 35
        elif days_inactive >= 30:
            score += 20
        elif days_inactive <= 7:
            # Actively used! Minimal waste score
            score = 5
            return score

        # Recurring charge with zero recent usage penalty
        if days_inactive >= 30:
            score += 15

        # 2. Duplicate / Category Overlap
        if is_duplicate:
            score += 20

        # 3. Unused Converted Free Trial
        if trial_converted and days_inactive >= 14:
            score += 20

        # 4. Bundle Redundancy (paying separately for something covered in a bundle)
        if is_bundled:
            score += 20

        # 5. Price Hike
        if price_hike:
            score += 15

        # 6. Cost magnitude
        if amount >= 2000 or amount >= 50:
            score += 15
        elif amount >= 1000 or amount >= 10:
            score += 10

        # Normalize score between 0 and 100
        waste_score = max(0, min(100, score))
        return waste_score

waste_analyzer = WasteAnalyzer()
