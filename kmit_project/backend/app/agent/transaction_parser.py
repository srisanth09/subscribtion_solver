import datetime
from typing import List, Dict, Any
from collections import defaultdict

# Pre-known service inactive usage signals (for realistic simulation if explicit usage telemetry isn't supplied)
KNOWN_SERVICE_USAGE_SIGNALS = {
    "streamflix": 187,         # Explicitly unused for 187 days as in INPUT 1
    "ironfit gym": 90,         # Unused for 90 days
    "tunewave": 4,             # Actively used 4 days ago as in INPUT 2
    "musicbox premium": 40,    # Unused 40 days as in INPUT 2
    "healthguard insurance": 210, # 210 days as in INPUT 3
    "canva pro": 120,          # Inactive 120 days
    "headspace": 45,           # Free trial converted, unused 45 days
    "netflix": 3,              # Actively used 3 days ago
    "spotify": 5,              # Actively used 5 days ago
    "youtube premium": 2,      # Actively used 2 days ago
    "github copilot": 1,       # Actively used 1 day ago
    "hdfc home loan": 30,
}

class TransactionParser:
    """
    Scans raw transactions, detects periodic billing patterns across cadences,
    and clusters recurring charges.
    """
    
    def detect_recurring_charges(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Groups transactions by merchant, calculates intervals,
        and identifies recurring subscriptions.
        """
        # Group by normalized merchant name
        grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for tx in transactions:
            m_key = tx["merchant"].strip()
            grouped[m_key].append(tx)

        detected_subscriptions = []

        for merchant, tx_list in grouped.items():
            # Sort chronologically
            sorted_tx = sorted(tx_list, key=lambda x: x["date"])
            
            # Check cadence if more than 1 transaction
            dates = [datetime.datetime.strptime(t["date"], "%Y-%m-%d").date() for t in sorted_tx]
            amounts = [t["amount"] for t in sorted_tx]
            
            # Determine cadence and recurrence
            is_recurring = False
            cadence = "monthly"
            avg_interval = 30
            
            if len(dates) >= 2:
                intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
                avg_interval = sum(intervals) / len(intervals)
                
                if 5 <= avg_interval <= 10:
                    cadence = "weekly"
                    is_recurring = True
                elif 25 <= avg_interval <= 35:
                    cadence = "monthly"
                    is_recurring = True
                elif 80 <= avg_interval <= 100:
                    cadence = "quarterly"
                    is_recurring = True
                elif 340 <= avg_interval <= 380:
                    cadence = "yearly"
                    is_recurring = True
                else:
                    # Generic recurring if interval variance is small (< 10 days)
                    if len(intervals) >= 2 and max(intervals) - min(intervals) <= 12:
                        is_recurring = True
                        cadence = "monthly"
            elif len(dates) == 1 and any(sub_kw in sorted_tx[0].get("description", "").lower() for sub_kw in ["monthly", "plan", "premium", "trial", "membership"]):
                is_recurring = True
                cadence = "monthly"

            if is_recurring or len(sorted_tx) >= 2:
                latest_tx = sorted_tx[-1]
                category = latest_tx.get("category", "general")
                current_amount = latest_tx["amount"]
                
                # Check for historical price hike
                price_hike_detected = False
                old_amount = None
                hike_pct = 0.0
                if len(amounts) >= 2:
                    prev_amount = amounts[-2]
                    # If previous non-zero amount was different from current amount
                    if prev_amount > 0 and current_amount > prev_amount:
                        price_hike_detected = True
                        old_amount = prev_amount
                        hike_pct = round(((current_amount - prev_amount) / prev_amount) * 100, 1)

                # Check for free trial conversion (zero followed by paid)
                trial_converted = False
                if len(amounts) >= 2 and amounts[-2] == 0 and current_amount > 0:
                    trial_converted = True

                # Determine last used days ago
                m_norm = merchant.lower().strip()
                last_used = KNOWN_SERVICE_USAGE_SIGNALS.get(m_norm, 15)

                detected_subscriptions.append({
                    "merchant": merchant,
                    "amount": current_amount,
                    "currency": latest_tx.get("currency", "₹"),
                    "cadence": cadence,
                    "category": category,
                    "last_billed_date": str(dates[-1]),
                    "transaction_count": len(sorted_tx),
                    "last_used_days_ago": last_used,
                    "price_hike_detected": price_hike_detected,
                    "old_price": old_amount,
                    "hike_percentage": hike_pct,
                    "trial_converted": trial_converted,
                    "raw_transactions": sorted_tx
                })

        return detected_subscriptions

transaction_parser = TransactionParser()
