import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, default="Demo User")
    email = Column(String, default="user@example.com")
    currency = Column(String, default="₹")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    guardrails = relationship("GuardrailConfig", back_populates="user", uselist=False, cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    emails = relationship("EmailLog", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    action_logs = relationship("ActionLog", back_populates="user", cascade="all, delete-orphan")

class GuardrailConfig(Base):
    __tablename__ = "guardrails"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True, index=True)
    auto_action_limit = Column(Float, default=2000.0)  # Default ₹2000 or $20
    protected_categories = Column(JSON, default=lambda: ["insurance", "loan_payment", "healthcare", "utility", "education"])
    min_confidence_threshold = Column(Float, default=0.85)
    require_approval_for_duplicates = Column(Boolean, default=True)
    negotiation_mode = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="guardrails")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String, unique=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    merchant = Column(String, index=True)
    amount = Column(Float)
    currency = Column(String, default="₹")
    date = Column(String)  # ISO Date string: YYYY-MM-DD
    category = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="transactions")

class EmailLog(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    sender = Column(String)
    subject = Column(String)
    body = Column(Text)
    date = Column(String)
    event_type = Column(String)  # subscription_renewal, price_hike, free_trial_started, free_trial_expiring
    extracted_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="emails")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    merchant = Column(String, index=True)
    amount = Column(Float)
    currency = Column(String, default="₹")
    cadence = Column(String, default="monthly")  # weekly, monthly, quarterly, yearly
    category = Column(String, index=True)
    last_used_days_ago = Column(Integer, default=0)
    
    # Intelligence Metrics
    waste_score = Column(Integer, default=0)        # 0 - 100
    confidence_score = Column(Float, default=0.0)   # 0.0 - 1.0 (or 0% - 100%)
    
    # Status: "active", "cancelled", "downgraded", "pending_approval", "negotiating", "protected", "kept"
    status = Column(String, default="active", index=True)
    
    # Feature flags
    is_free_trial = Column(Boolean, default=False)
    trial_converted = Column(Boolean, default=False)
    
    price_hike_detected = Column(Boolean, default=False)
    old_price = Column(Float, nullable=True)
    hike_percentage = Column(Float, nullable=True)
    
    is_duplicate_detected = Column(Boolean, default=False)
    duplicate_category = Column(String, nullable=True)
    duplicate_counterpart = Column(String, nullable=True)
    
    is_bundled = Column(Boolean, default=False)
    bundle_provider = Column(String, nullable=True)
    bundle_description = Column(String, nullable=True)
    
    # Guardrail evaluation & decision
    guardrail_status = Column(String, default="PENDING")  # PASSED, BLOCKED_PROTECTED, BLOCKED_LIMIT, BLOCKED_CONFIDENCE
    decision = Column(String, default="MONITOR")          # AUTO_CANCEL, AUTO_DOWNGRADE, ESCALATE_APPROVAL, KEEP
    decision_reason = Column(Text, nullable=True)
    action_taken = Column(String, nullable=True)
    
    next_billing_date = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="subscriptions")
    negotiation_offers = relationship("NegotiationOffer", back_populates="subscription", cascade="all, delete-orphan")

class ActionLog(Base):
    __tablename__ = "action_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    subscription_id = Column(Integer, nullable=True)
    merchant = Column(String)
    action_type = Column(String)  # AUTO_CANCEL, AUTO_DOWNGRADE, ESCALATE_APPROVAL, BLOCKED_GUARDRAIL, USER_APPROVED, USER_KEPT, NEGOTIATION_ACCEPTED
    reason = Column(Text)
    waste_score = Column(Integer, default=0)
    confidence = Column(Float, default=0.0)
    amount = Column(Float, default=0.0)
    monthly_saving = Column(Float, default=0.0)
    annual_saving = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    extra_details = Column(JSON, nullable=True)
    
    user = relationship("User", back_populates="action_logs")

class NegotiationOffer(Base):
    __tablename__ = "negotiation_offers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    merchant = Column(String)
    original_price = Column(Float)
    offered_price = Column(Float)
    discount_percent = Column(Float)
    monthly_saving = Column(Float, nullable=True, default=0.0)
    annual_saving = Column(Float, nullable=True, default=0.0)
    pitch_letter = Column(Text)
    merchant_reply = Column(Text)
    status = Column(String, default="pending_acceptance")  # pending_acceptance, accepted, declined, expired
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    subscription = relationship("Subscription", back_populates="negotiation_offers")

class MerchantCommunication(Base):
    __tablename__ = "merchant_communications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), index=True)
    merchant = Column(String, index=True)
    channel = Column(String, default="REST_API")  # REST_API, EMAIL_GATEWAY, MERCHANT_PORTAL
    request_type = Column(String, default="DISCOUNT_REQUEST")  # DISCOUNT_REQUEST, TIER_DOWNGRADE
    
    # Negotiation specifics
    original_price = Column(Float)
    target_price = Column(Float)
    target_discount_pct = Column(Float, default=25.0)
    pitch_subject = Column(String)
    pitch_message = Column(Text)
    
    # Lifecycle status: SENT, RECEIVED_BY_MERCHANT, MERCHANT_ACCEPTED, MERCHANT_REJECTED, EVALUATED
    status = Column(String, default="SENT", index=True)
    
    # Merchant Response
    merchant_reply_text = Column(Text, nullable=True)
    merchant_counter_price = Column(Float, nullable=True)
    merchant_outcome = Column(String, nullable=True)  # ACCEPTED, REJECTED
    
    # Agent Reasoning & Evaluation
    agent_evaluation = Column(Text, nullable=True)
    resulting_action = Column(String, nullable=True)  # APPLIED_DISCOUNT, PROCEEDED_TO_CANCEL, ESCALATED_TO_HUMAN
    monthly_saving = Column(Float, default=0.0)
    annual_saving = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)
    evaluated_at = Column(DateTime, nullable=True)
    
    subscription = relationship("Subscription", backref="merchant_communications")
    user = relationship("User", backref="merchant_communications")
