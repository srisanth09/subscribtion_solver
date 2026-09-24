import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import Subscription, GuardrailConfig, MerchantCommunication, ActionLog
from app.agent.orchestrator import orchestrator
from app.agent.negotiation_agent import negotiation_agent
from app.data.seed_data import seed_initial_data

from sqlalchemy.pool import StaticPool

# In-memory database for isolated testing with StaticPool
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    seed_initial_data(db, user_id="u_neg_test")
    yield db
    db.close()
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def client(db_session):
    return TestClient(app)

def get_or_create_sub(db, user_id, merchant, amount=649.0, category="video_streaming", status="pending_approval"):
    sub = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.merchant == merchant
    ).first()
    if not sub:
        sub = Subscription(
            user_id=user_id,
            merchant=merchant,
            amount=amount,
            currency="₹",
            category=category,
            status=status,
            waste_score=75,
            confidence_score=0.92
        )
        db.add(sub)
    else:
        sub.amount = amount
        sub.status = status
        sub.waste_score = 75
        sub.confidence_score = 0.92
    db.commit()
    db.refresh(sub)
    return sub

def test_negotiation_mode_contacts_merchant_before_cancelling(db_session):
    """
    Verifies that when Negotiation Mode is enabled, the agent contacts the merchant
    with a generated discount/downgrade request before cancelling an eligible subscription.
    """
    user_id = "u_neg_test"

    # Enable negotiation_mode on user guardrails
    guardrail = db_session.query(GuardrailConfig).filter(GuardrailConfig.user_id == user_id).first()
    if not guardrail:
        guardrail = GuardrailConfig(user_id=user_id, negotiation_mode=True)
        db_session.add(guardrail)
    else:
        guardrail.negotiation_mode = True
    db_session.commit()

    # Run audit with negotiation mode prompt
    audit_res = orchestrator.run_full_audit(
        db=db_session,
        user_id=user_id,
        user_prompt="Run audit with negotiation mode"
    )

    # Verify audit trace contains NEGOTIATION_MODE_ENGAGED
    neg_traces = [t for t in audit_res["audit_trace"] if t["step"] == "NEGOTIATION_MODE_ENGAGED"]
    assert len(neg_traces) >= 1, "Should have engaged negotiation mode for eligible wasteful subscription"
    assert any("StreamFlix" in t["message"] for t in neg_traces)

    # Verify StreamFlix subscription is in 'negotiating' status, NOT prematurely cancelled
    streamflix = db_session.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.merchant == "StreamFlix"
    ).first()
    assert streamflix is not None
    assert streamflix.status == "negotiating"

    # Verify merchant communication record was generated and dispatched
    comm = db_session.query(MerchantCommunication).filter(
        MerchantCommunication.user_id == user_id,
        MerchantCommunication.subscription_id == streamflix.id
    ).first()
    assert comm is not None
    assert comm.status == "SENT"
    assert comm.original_price == streamflix.amount
    assert comm.target_price < comm.original_price
    assert "StreamFlix" in comm.pitch_message

def test_test_merchant_receives_negotiation_request(db_session):
    """
    Verifies that a test merchant receives a negotiation request with a tailored pitch letter and target pricing.
    """
    user_id = "u_neg_test"
    sub = get_or_create_sub(db_session, user_id, "TuneWave", amount=399.0, category="music_streaming")

    comm = negotiation_agent.send_negotiation_to_merchant(
        db=db_session,
        user_id=user_id,
        subscription=sub,
        request_type="DISCOUNT_REQUEST",
        target_discount_pct=25.0
    )

    assert comm.id is not None
    assert comm.status == "SENT"
    assert comm.merchant == "TuneWave"
    assert comm.original_price == 399.0
    assert comm.target_price == 299.25
    assert "TuneWave" in comm.pitch_message
    assert sub.status == "negotiating"

def test_agent_handles_accepted_offer_correctly(db_session):
    """
    Verifies that when the merchant accepts the offer:
    - The agent evaluates the response
    - Applies the discount / new price
    - Sets subscription status to 'negotiated'
    - Realized monthly/annual savings are credited
    - NEGOTIATION_ACCEPTED action log is recorded
    """
    user_id = "u_neg_test"
    sub = get_or_create_sub(db_session, user_id, "StreamFlix", amount=649.0, category="video_streaming")
    orig_price = sub.amount

    # Send request
    comm = negotiation_agent.send_negotiation_to_merchant(
        db=db_session,
        user_id=user_id,
        subscription=sub,
        request_type="DISCOUNT_REQUEST",
        target_discount_pct=25.0
    )

    # Simulate merchant accepts offer
    eval_result = negotiation_agent.evaluate_and_apply_merchant_response(
        db=db_session,
        user_id=user_id,
        communication_id=comm.id,
        outcome="ACCEPTED",
        counter_price=486.75
    )

    assert eval_result["success"] is True
    assert eval_result["status"] == "ACCEPTED"
    assert eval_result["resulting_action"] == "APPLIED_DISCOUNT"
    assert eval_result["subscription_status"] == "negotiated"
    assert eval_result["new_price"] == 486.75
    assert eval_result["monthly_savings"] == round(orig_price - 486.75, 2)

    # Check updated database state
    db_session.refresh(sub)
    assert sub.status == "negotiated"
    assert sub.amount == 486.75

    db_session.refresh(comm)
    assert comm.status == "MERCHANT_ACCEPTED"
    assert comm.merchant_outcome == "ACCEPTED"
    assert comm.resulting_action == "APPLIED_DISCOUNT"

    # Verify ActionLog
    log = db_session.query(ActionLog).filter(
        ActionLog.user_id == user_id,
        ActionLog.subscription_id == sub.id,
        ActionLog.action_type == "NEGOTIATION_ACCEPTED"
    ).first()
    assert log is not None
    assert log.monthly_saving == round(orig_price - 486.75, 2)

def test_agent_handles_rejected_offer_correctly(db_session):
    """
    Verifies that when the merchant rejects the offer:
    - The agent evaluates the rejection
    - Subscription price remains strictly unchanged at original price (NOT 0, NOT discounted)
    - Subscription status remains 'active'
    - Realized monthly and annual savings are strictly 0.0
    - Action log: NEGOTIATION_FAILED with monthly_saving=0.0, annual_saving=0.0
    - No AUTO_CANCEL is triggered
    """
    user_id = "u_neg_test"
    sub = get_or_create_sub(db_session, user_id, "StreamFlix", amount=649.0, category="video_streaming")
    orig_price = sub.amount

    # Send request
    comm = negotiation_agent.send_negotiation_to_merchant(
        db=db_session,
        user_id=user_id,
        subscription=sub,
        request_type="DISCOUNT_REQUEST"
    )

    # Simulate merchant rejects offer
    eval_result = negotiation_agent.evaluate_and_apply_merchant_response(
        db=db_session,
        user_id=user_id,
        communication_id=comm.id,
        outcome="REJECTED"
    )

    assert eval_result["success"] is True
    assert eval_result["status"] == "REJECTED"
    assert eval_result["resulting_action"] == "ORIGINAL_PRICE_MAINTAINED"
    assert eval_result["subscription_status"] == "active"
    assert eval_result["new_price"] == orig_price
    assert eval_result["monthly_savings"] == 0.0
    assert eval_result["annual_savings"] == 0.0

    # Check database state: price must be strictly preserved
    db_session.refresh(sub)
    assert sub.status == "active"
    assert sub.amount == orig_price

    db_session.refresh(comm)
    assert comm.status == "MERCHANT_REJECTED"
    assert comm.resulting_action == "ORIGINAL_PRICE_MAINTAINED"
    assert comm.monthly_saving == 0.0
    assert comm.annual_saving == 0.0

    # Verify ActionLog contains NEGOTIATION_FAILED with zero savings
    failed_log = db_session.query(ActionLog).filter(
        ActionLog.user_id == user_id,
        ActionLog.subscription_id == sub.id,
        ActionLog.action_type == "NEGOTIATION_FAILED"
    ).first()
    assert failed_log is not None
    assert failed_log.amount == orig_price
    assert failed_log.monthly_saving == 0.0
    assert failed_log.annual_saving == 0.0

    # Verify NO AUTO_CANCEL log was created
    cancel_log = db_session.query(ActionLog).filter(
        ActionLog.user_id == user_id,
        ActionLog.subscription_id == sub.id,
        ActionLog.action_type == "AUTO_CANCEL"
    ).first()
    assert cancel_log is None

def test_tier_downgrade_request_and_simulation_api(client, db_session):
    """
    Tests tier downgrade request type and verifies full E2E test-merchant simulate endpoint.
    """
    user_id = "u_neg_test"
    sub = get_or_create_sub(db_session, user_id, "TuneWave", amount=399.0, category="music_streaming")

    # 1. Test simulation of ACCEPTED tier downgrade
    res = client.post("/api/merchants/test-merchant/simulate", json={
        "subscription_id": sub.id,
        "simulate_outcome": "ACCEPTED",
        "request_type": "TIER_DOWNGRADE",
        "user_id": user_id
    })

    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["status"] == "ACCEPTED"
    assert data["resulting_action"] == "APPLIED_DISCOUNT"
    assert data["subscription_status"] == "negotiated"
    assert data["monthly_savings"] > 0

    # 2. Check communications list endpoint
    list_res = client.get(f"/api/merchants/communications?user_id={user_id}&subscription_id={sub.id}")
    assert list_res.status_code == 200
    comms = list_res.json()
    assert len(comms) >= 1
    assert comms[0]["merchant"] == "TuneWave"
    assert comms[0]["request_type"] == "TIER_DOWNGRADE"
    assert comms[0]["status"] == "MERCHANT_ACCEPTED"
