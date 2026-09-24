import csv
import json
import os
from sqlalchemy.orm import Session
from app.models import User, GuardrailConfig, Transaction, EmailLog, Subscription
from app.config import settings

DATA_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(DATA_DIR, "transactions.csv")
EMAILS_PATH = os.path.join(DATA_DIR, "emails.json")

def seed_initial_data(db: Session, user_id: str = "u_301"):
    """Seeds default user, guardrails, transactions, and emails into the database."""
    
    # 1. User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(
            id=user_id,
            name="Srisanth (Guardian Demo)",
            email="srisanth@kmit.ac.in",
            currency="₹"
        )
        db.add(user)
        db.commit()
    
    # 2. Guardrails
    guardrail = db.query(GuardrailConfig).filter(GuardrailConfig.user_id == user_id).first()
    if not guardrail:
        guardrail = GuardrailConfig(
            user_id=user_id,
            auto_action_limit=2000.0,  # ₹2,000 auto-action threshold
            protected_categories=["insurance", "loan_payment", "healthcare", "utility", "education"],
            min_confidence_threshold=0.85,
            require_approval_for_duplicates=True
        )
        db.add(guardrail)
        db.commit()

    # 3. Transactions from CSV
    existing_tx_count = db.query(Transaction).filter(Transaction.user_id == user_id).count()
    if existing_tx_count == 0 and os.path.exists(CSV_PATH):
        with open(CSV_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tx = Transaction(
                    transaction_id=f"{user_id}_{row['transaction_id']}",
                    user_id=user_id,
                    merchant=row["merchant"],
                    amount=float(row["amount"]),
                    currency=row.get("currency", "₹"),
                    date=row["date"],
                    category=row["category"],
                    description=row.get("description", "")
                )
                db.add(tx)
        db.commit()

    # 4. Emails from JSON
    existing_email_count = db.query(EmailLog).filter(EmailLog.user_id == user_id).count()
    if existing_email_count == 0 and os.path.exists(EMAILS_PATH):
        with open(EMAILS_PATH, mode="r", encoding="utf-8") as f:
            emails_data = json.load(f)
            for item in emails_data:
                email = EmailLog(
                    user_id=user_id,
                    sender=item["sender"],
                    subject=item["subject"],
                    body=item["body"],
                    date=item["date"],
                    event_type=item["event_type"],
                    extracted_data=item.get("extracted_data")
                )
                db.add(email)
        db.commit()
