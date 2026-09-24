from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class GuardrailConfigSchema(BaseModel):
    user_id: str = "u_301"
    auto_action_limit: float = 2000.0
    protected_categories: List[str] = ["insurance", "loan_payment", "healthcare", "utility", "education"]
    min_confidence_threshold: float = 0.85
    require_approval_for_duplicates: bool = True
    negotiation_mode: bool = False

    class Config:
        from_attributes = True

class GuardrailUpdate(BaseModel):
    auto_action_limit: Optional[float] = None
    protected_categories: Optional[List[str]] = None
    min_confidence_threshold: Optional[float] = None
    require_approval_for_duplicates: Optional[bool] = None
    negotiation_mode: Optional[bool] = None

class TransactionSchema(BaseModel):
    id: Optional[int] = None
    transaction_id: str
    user_id: str = "u_301"
    merchant: str
    amount: float
    currency: str = "₹"
    date: str
    category: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class EmailSchema(BaseModel):
    id: Optional[int] = None
    user_id: str = "u_301"
    sender: str
    subject: str
    body: str
    date: str
    event_type: str
    extracted_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class NegotiationOfferSchema(BaseModel):
    id: int
    subscription_id: int
    merchant: str
    original_price: float
    offered_price: float
    discount_percent: float
    monthly_saving: Optional[float] = 0.0
    annual_saving: Optional[float] = 0.0
    pitch_letter: str
    merchant_reply: str
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MerchantCommunicationSchema(BaseModel):
    id: int
    user_id: str
    subscription_id: int
    merchant: str
    channel: str
    request_type: str
    original_price: float
    target_price: float
    target_discount_pct: float
    pitch_subject: str
    pitch_message: str
    status: str
    merchant_reply_text: Optional[str] = None
    merchant_counter_price: Optional[float] = None
    merchant_outcome: Optional[str] = None
    agent_evaluation: Optional[str] = None
    resulting_action: Optional[str] = None
    monthly_saving: Optional[float] = 0.0
    annual_saving: Optional[float] = 0.0
    created_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    evaluated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SendNegotiationRequest(BaseModel):
    subscription_id: int
    request_type: str = "DISCOUNT_REQUEST"  # DISCOUNT_REQUEST, TIER_DOWNGRADE
    target_discount_pct: float = 25.0
    user_id: str = "u_301"

class MerchantResponseRequest(BaseModel):
    outcome: str = "ACCEPTED"  # "ACCEPTED" or "REJECTED"
    counter_price: Optional[float] = None
    response_text: Optional[str] = None
    user_id: str = "u_301"

class TestMerchantSimulateRequest(BaseModel):
    subscription_id: int
    simulate_outcome: str = "ACCEPTED"  # "ACCEPTED" or "REJECTED"
    request_type: str = "DISCOUNT_REQUEST"
    user_id: str = "u_301"

class SubscriptionCreate(BaseModel):
    user_id: str = "u_301"
    merchant: str = Field(..., min_length=1, description="Merchant or Service name")
    amount: float = Field(..., gt=0, description="Recurring cost, must be greater than 0")
    currency: str = Field(default="₹", description="Currency symbol")
    cadence: str = Field(default="monthly", description="Billing frequency: weekly, monthly, quarterly, yearly")
    category: str = Field(..., min_length=1, description="Subscription category")
    last_used_days_ago: int = Field(default=0, ge=0, description="Days since last use")
    is_duplicate: bool = Field(default=False, description="Whether it is a duplicate subscription")
    duplicate_counterpart: Optional[str] = Field(default=None, description="Duplicate counterpart service")
    is_bundled: bool = Field(default=False, description="Whether it is part of a bundle")
    bundle_provider: Optional[str] = Field(default=None, description="Bundle provider name")
    bundle_description: Optional[str] = Field(default=None, description="Bundle description")
    is_free_trial: bool = Field(default=False, description="Whether it is a free trial")
    trial_converted: bool = Field(default=False, description="Whether free trial converted")
    previous_price: Optional[float] = Field(default=None, description="Previous price before hike")
    current_price: Optional[float] = Field(default=None, description="Current price")
    transaction_date: Optional[str] = Field(default=None, description="Transaction or start date")

class SubscriptionSchema(BaseModel):
    id: int
    user_id: str
    merchant: str
    amount: float
    currency: str
    cadence: str
    category: str
    last_used_days_ago: int
    waste_score: int
    confidence_score: float
    status: str
    is_free_trial: bool
    trial_converted: bool
    price_hike_detected: bool
    old_price: Optional[float] = None
    hike_percentage: Optional[float] = None
    is_duplicate_detected: bool
    duplicate_category: Optional[str] = None
    duplicate_counterpart: Optional[str] = None
    is_bundled: bool
    bundle_provider: Optional[str] = None
    bundle_description: Optional[str] = None
    guardrail_status: str
    decision: str
    decision_reason: Optional[str] = None
    action_taken: Optional[str] = None
    next_billing_date: Optional[str] = None
    negotiation_offers: Optional[List[NegotiationOfferSchema]] = []

    class Config:
        from_attributes = True

class ActionLogSchema(BaseModel):
    id: int
    user_id: str
    subscription_id: Optional[int]
    merchant: str
    action_type: str
    reason: str
    waste_score: int
    confidence: float
    amount: float
    monthly_saving: float
    annual_saving: float
    timestamp: datetime
    extra_details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class AuditExecutionLog(BaseModel):
    step: str
    message: str
    status: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None

class AuditRequest(BaseModel):
    user_id: str = "u_301"
    user_prompt: str = "Go through my subscriptions and clean up anything I'm not using."

class AuditResponse(BaseModel):
    user_id: str
    status: str
    message: str
    total_subscriptions_scanned: int
    auto_cancelled_count: int
    escalated_count: int
    protected_count: int
    active_kept_count: int
    potential_monthly_savings: float
    potential_annual_savings: float
    currency: str
    audit_trace: List[AuditExecutionLog]

class SubscriptionUserAction(BaseModel):
    action: str  # "approve_cancel", "keep", "downgrade", "negotiate"
    user_note: Optional[str] = None

class SavingsSummary(BaseModel):
    currency: str = "₹"
    total_subscriptions: int
    active_count: int
    auto_cancelled_count: int
    pending_approval_count: int
    protected_count: int
    price_hikes_count: int
    duplicates_count: int
    monthly_waste_prevented: float
    annual_waste_prevented: float
    realized_monthly_savings: float
    realized_annual_savings: float
    potential_monthly_savings: float
    potential_annual_savings: float

class PromptRequest(BaseModel):
    user_id: str = "u_301"
    prompt: str = Field(..., description="Natural language prompt or command for the agent")

class PromptResponse(BaseModel):
    user_id: str
    prompt: str
    intent: str
    reply: str
    action_taken: Optional[str] = None
    monthly_savings: Optional[float] = None
    annual_savings: Optional[float] = None
    currency: Optional[str] = "₹"
    audit_trace: Optional[List[AuditExecutionLog]] = None
    data: Optional[Dict[str, Any]] = None

