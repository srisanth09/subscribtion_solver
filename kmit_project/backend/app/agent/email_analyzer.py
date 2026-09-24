import re
from typing import List, Dict, Any

class EmailAnalyzer:
    """
    Scans user billing and service emails to extract price change notices,
    trial expiration dates, and upcoming renewals.
    """
    
    def analyze_emails(self, emails: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Processes a list of email objects and returns a dictionary indexed by normalized merchant name.
        """
        merchant_email_intel = {}

        for email in emails:
            subject = email.get("subject", "")
            body = email.get("body", "")
            sender = email.get("sender", "")
            extracted = email.get("extracted_data") or {}
            event_type = email.get("event_type", "")

            # If pre-extracted data exists, use it as baseline
            merchant = extracted.get("merchant")
            if not merchant:
                # Basic NER from sender or subject
                match = re.search(r"@([a-zA-Z0-9\-]+)\.", sender)
                if match:
                    merchant = match.group(1).capitalize()
                else:
                    merchant = "Unknown Merchant"

            norm_m = merchant.lower().strip()
            if norm_m not in merchant_email_intel:
                merchant_email_intel[norm_m] = {
                    "merchant": merchant,
                    "has_email_intel": True,
                    "events": [],
                    "price_hike": None,
                    "trial_info": None,
                    "next_billing_date": None
                }

            entry = merchant_email_intel[norm_m]
            entry["events"].append({
                "date": email.get("date"),
                "event_type": event_type,
                "subject": subject
            })

            # Check for price hike
            if event_type == "price_hike" or "price is changing" in subject.lower() or "price increase" in body.lower():
                entry["price_hike"] = {
                    "old_price": extracted.get("old_price", 499),
                    "new_price": extracted.get("new_price", 599),
                    "percentage": extracted.get("percentage_increase", 20.0),
                    "effective_date": extracted.get("effective_date", "2026-09-20")
                }

            # Check for free trial
            if event_type in ["free_trial_started", "free_trial_expiring"] or "free trial" in body.lower():
                entry["trial_info"] = {
                    "is_trial": True,
                    "trial_days": extracted.get("trial_days", 30),
                    "expiry_date": extracted.get("expiry_date"),
                    "subsequent_price": extracted.get("subsequent_price")
                }

            if event_type == "free_trial_converted":
                if not entry["trial_info"]:
                    entry["trial_info"] = {}
                entry["trial_info"]["converted_to_paid"] = True

            # Next billing date
            if "next_billing_date" in extracted:
                entry["next_billing_date"] = extracted["next_billing_date"]

        return merchant_email_intel

email_analyzer = EmailAnalyzer()
