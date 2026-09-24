import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from app.database import Base
from app.data.seed_data import seed_initial_data
from app.models import Subscription, ActionLog, NegotiationOffer
from app.routes.subscriptions import (
    start_merchant_negotiation, 
    accept_negotiated_offer, 
    decline_negotiated_offer,
    fail_negotiated_offer,
    expire_negotiated_offer,
    get_subscription_detail
)
from app.routes.savings import get_savings_metrics
from app.agent.orchestrator import orchestrator

TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    seed_initial_data(db, user_id="u_test")
    yield db
    db.close()
    Base.metadata.drop_all(bind=test_engine)

def test_negotiate_streamflix_scenario(db_session):
    """
    End-to-end demo scenario from specification:
    StreamFlix at ₹999/month
    1. User clicks Negotiate -> AI generates 25% discount retention offer.
    2. Pending offer does NOT prematurely add to realized savings.
    3. User clicks Accept Offer -> new price ₹749.25, monthly saving ₹249.75, annual saving ₹2,997.
    4. ActionLog recorded with NEGOTIATION_ACCEPTED.
    5. Running audit repeatedly does not duplicate savings or overwrite negotiated price.
    """
    # Setup StreamFlix at ₹999/mo
    sub = db_session.query(Subscription).filter(
        Subscription.user_id == "u_test",
        Subscription.merchant == "StreamFlix"
    ).first()
    if not sub:
        sub = Subscription(
            user_id="u_test",
            merchant="StreamFlix",
            amount=999.0,
            currency="₹",
            category="video_streaming",
            status="pending_approval"
        )
        db_session.add(sub)
    else:
        sub.amount = 999.0
        sub.status = "pending_approval"
    db_session.commit()
    db_session.refresh(sub)

    initial_metrics = get_savings_metrics(user_id="u_test", db=db_session)
    initial_realized_savings = initial_metrics.realized_monthly_savings

    # 1. Start Negotiation
    res = start_merchant_negotiation(sub_id=sub.id, db=db_session)
    offer = res["offer"]

    assert offer.merchant == "StreamFlix"
    assert offer.original_price == 999.0
    assert offer.offered_price == 749.25
    assert offer.discount_percent == 25.0
    assert offer.monthly_saving == 249.75
    assert offer.annual_saving == 2997.0
    assert offer.status == "pending_acceptance"
    assert "retention discount" in offer.merchant_reply.lower() or "25%" in offer.merchant_reply

    # 2. Verify pending offer does NOT increase realized savings
    pending_metrics = get_savings_metrics(user_id="u_test", db=db_session)
    assert pending_metrics.realized_monthly_savings == initial_realized_savings, (
        "Pending negotiation offer must NOT increase realized savings!"
    )

    # 3. Accept Offer
    accept_res = accept_negotiated_offer(sub_id=sub.id, offer_id=offer.id, db=db_session)
    assert accept_res["monthly_savings"] == 249.75
    assert accept_res["annual_savings"] == 2997.0

    # Verify subscription updated
    db_session.refresh(sub)
    assert sub.amount == 749.25
    assert sub.status == "negotiated"

    db_session.refresh(offer)
    assert offer.status == "accepted"

    # 4. Verify realized savings increased by exactly ₹249.75
    accepted_metrics = get_savings_metrics(user_id="u_test", db=db_session)
    assert accepted_metrics.realized_monthly_savings == initial_realized_savings + 249.75
    assert accepted_metrics.realized_annual_savings == initial_metrics.realized_annual_savings + 2997.0

    # Verify ActionLog created
    log = db_session.query(ActionLog).filter(
        ActionLog.user_id == "u_test",
        ActionLog.subscription_id == sub.id,
        ActionLog.action_type == "NEGOTIATION_ACCEPTED"
    ).first()
    assert log is not None
    assert log.monthly_saving == 249.75
    assert log.annual_saving == 2997.0
    assert log.amount == 749.25

    # 5. First full audit:
    audit_res1 = orchestrator.run_full_audit(db=db_session, user_id="u_test")
    assert audit_res1["status"] == "COMPLETED"

    # StreamFlix must still be negotiated at 749.25, NOT cancelled or reset!
    db_session.refresh(sub)
    assert sub.amount == 749.25, "Negotiated discounted amount must be retained after audit!"
    assert sub.status == "negotiated"

    streamflix_logs = db_session.query(ActionLog).filter(
        ActionLog.user_id == "u_test",
        ActionLog.merchant == "StreamFlix"
    ).all()
    assert len(streamflix_logs) == 1
    assert streamflix_logs[0].action_type == "NEGOTIATION_ACCEPTED"
    assert streamflix_logs[0].monthly_saving == 249.75

    post_audit1_metrics = get_savings_metrics(user_id="u_test", db=db_session)

    # 6. Repeated Audit Idempotency: Running audit again must NOT increase savings
    audit_res2 = orchestrator.run_full_audit(db=db_session, user_id="u_test")
    assert audit_res2["status"] == "COMPLETED"

    post_audit2_metrics = get_savings_metrics(user_id="u_test", db=db_session)
    assert post_audit2_metrics.realized_monthly_savings == post_audit1_metrics.realized_monthly_savings, (
        "Running audit repeatedly must NOT increase savings!"
    )

def test_negotiate_decline_scenario(db_session):
    """
    Verifies that declining an offer:
    1. Sets offer status to 'declined'.
    2. Maintains original subscription price.
    3. Records NEGOTIATION_DECLINED in ActionLog with zero savings.
    4. Does not increase realized savings.
    """
    sub = db_session.query(Subscription).filter(
        Subscription.user_id == "u_test",
        Subscription.merchant == "Canva Pro"
    ).first()
    if not sub:
        sub = Subscription(
            user_id="u_test",
            merchant="Canva Pro",
            amount=599.0,
            currency="₹",
            category="productivity",
            status="active"
        )
        db_session.add(sub)
        db_session.commit()

    original_price = sub.amount
    initial_metrics = get_savings_metrics(user_id="u_test", db=db_session)

    # Start negotiation
    res = start_merchant_negotiation(sub_id=sub.id, db=db_session)
    offer = res["offer"]

    # Decline offer
    decline_res = decline_negotiated_offer(sub_id=sub.id, offer_id=offer.id, db=db_session)
    assert decline_res["monthly_savings"] == 0.0

    db_session.refresh(sub)
    assert sub.amount == original_price
    assert sub.status == "active"

    db_session.refresh(offer)
    assert offer.status == "declined"

    # Savings must remain completely unchanged
    post_decline_metrics = get_savings_metrics(user_id="u_test", db=db_session)
    assert post_decline_metrics.realized_monthly_savings == initial_metrics.realized_monthly_savings

    # Verify ActionLog
    log = db_session.query(ActionLog).filter(
        ActionLog.user_id == "u_test",
        ActionLog.subscription_id == sub.id,
        ActionLog.action_type == "NEGOTIATION_DECLINED"
    ).first()
    assert log is not None
    assert log.monthly_saving == 0.0

def test_negotiation_guardrail_blocking(db_session):
    """
    Verifies that negotiation is strictly blocked for protected categories (e.g. insurance, loans).
    """
    # HealthGuard Insurance is in category 'insurance'
    insurance = db_session.query(Subscription).filter(
        Subscription.user_id == "u_test",
        Subscription.merchant == "HealthGuard Insurance"
    ).first()
    if not insurance:
        insurance = Subscription(
            user_id="u_test",
            merchant="HealthGuard Insurance",
            amount=2500.0,
            currency="₹",
            category="insurance",
            status="protected"
        )
        db_session.add(insurance)
        db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        start_merchant_negotiation(sub_id=insurance.id, db=db_session)

    assert exc_info.value.status_code == 403
    assert "protected category" in exc_info.value.detail.lower()

def test_negotiation_cancelled_blocked(db_session):
    """
    Verifies that negotiation cannot be started for already cancelled subscriptions.
    """
    sub = Subscription(
        user_id="u_test",
        merchant="OldDeadApp",
        amount=300.0,
        currency="₹",
        category="entertainment",
        status="cancelled"
    )
    db_session.add(sub)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        start_merchant_negotiation(sub_id=sub.id, db=db_session)

    assert exc_info.value.status_code == 400
    assert "cancelled" in exc_info.value.detail.lower()

def test_no_duplicate_offers_on_refresh(db_session):
    """
    Verifies that repeatedly calling /negotiate returns the existing pending offer
    rather than creating duplicate database entries.
    """
    sub = db_session.query(Subscription).filter(
        Subscription.user_id == "u_test",
        Subscription.merchant == "TuneWave"
    ).first()
    if not sub:
        sub = Subscription(
            user_id="u_test",
            merchant="TuneWave",
            amount=399.0,
            currency="₹",
            category="music_streaming",
            status="pending_approval"
        )
        db_session.add(sub)
        db_session.commit()

    # First call
    res1 = start_merchant_negotiation(sub_id=sub.id, db=db_session)
    offer1_id = res1["offer"].id

    # Second call (e.g. page refresh or repeated click)
    res2 = start_merchant_negotiation(sub_id=sub.id, db=db_session)
    offer2_id = res2["offer"].id

    assert offer1_id == offer2_id

    total_offers = db_session.query(NegotiationOffer).filter(
        NegotiationOffer.subscription_id == sub.id
    ).count()
    assert total_offers == 1


# ============================================================================
# 9 Explicit Test Cases Required for Failed & Successful Negotiation Handling
# ============================================================================

def test_case_1_negotiation_succeeds_user_accepts_discounted_price_applied(db_session):
    """
    Test Case 1: Negotiation succeeds -> user accepts -> discounted price applied.
    Original price = ₹999 -> Discount = 25% -> New price = ₹749.25.
    """
    sub = Subscription(
        user_id="u_test",
        merchant="Case1Service",
        amount=999.0,
        currency="₹",
        category="video_streaming",
        status="active"
    )
    db_session.add(sub)
    db_session.commit()

    res = start_merchant_negotiation(sub_id=sub.id, db=db_session)
    offer = res["offer"]
    assert offer.original_price == 999.0
    assert offer.offered_price == 749.25

    accept_res = accept_negotiated_offer(sub_id=sub.id, offer_id=offer.id, db=db_session)
    assert accept_res["monthly_savings"] == 249.75
    assert accept_res["annual_savings"] == 2997.0

    db_session.refresh(sub)
    assert sub.amount == 749.25
    assert sub.status == "negotiated"

    log = db_session.query(ActionLog).filter(
        ActionLog.user_id == "u_test",
        ActionLog.subscription_id == sub.id,
        ActionLog.action_type == "NEGOTIATION_ACCEPTED"
    ).first()
    assert log is not None
    assert log.amount == 749.25
    assert log.monthly_saving == 249.75


def test_case_2_negotiation_succeeds_user_declines_original_price_remains(db_session):
    """
    Test Case 2: Negotiation succeeds -> user declines -> original price remains.
    Original price = ₹999 -> User declines -> Price stays ₹999 (NOT ₹749, NOT ₹0).
    """
    sub = Subscription(
        user_id="u_test",
        merchant="Case2Service",
        amount=999.0,
        currency="₹",
        category="productivity",
        status="active"
    )
    db_session.add(sub)
    db_session.commit()

    res = start_merchant_negotiation(sub_id=sub.id, db=db_session)
    offer = res["offer"]

    decline_res = decline_negotiated_offer(sub_id=sub.id, offer_id=offer.id, db=db_session)
    assert decline_res["monthly_savings"] == 0.0
    assert decline_res["annual_savings"] == 0.0
    assert decline_res["original_price"] == 999.0
    assert decline_res["final_price"] == 999.0

    db_session.refresh(sub)
    assert sub.amount == 999.0
    assert sub.status == "active"

    log = db_session.query(ActionLog).filter(
        ActionLog.user_id == "u_test",
        ActionLog.subscription_id == sub.id,
        ActionLog.action_type == "NEGOTIATION_DECLINED"
    ).first()
    assert log is not None
    assert log.amount == 999.0
    assert log.monthly_saving == 0.0
    assert log.annual_saving == 0.0


def test_case_3_negotiation_fails_original_price_remains(db_session):
    """
    Test Case 3: Negotiation fails -> original price remains.
    Original price = ₹999 -> Negotiation = FAILED -> Price stays ₹999 (NOT ₹749, NOT ₹0).
    """
    sub = Subscription(
        user_id="u_test",
        merchant="Case3Service",
        amount=999.0,
        currency="₹",
        category="video_streaming",
        status="active"
    )
    db_session.add(sub)
    db_session.commit()

    res = start_merchant_negotiation(sub_id=sub.id, db=db_session)
    offer = res["offer"]

    fail_res = fail_negotiated_offer(sub_id=sub.id, offer_id=offer.id, reason="Merchant refused concession", db=db_session)
    assert fail_res["monthly_savings"] == 0.0
    assert fail_res["annual_savings"] == 0.0
    assert fail_res["original_price"] == 999.0
    assert fail_res["final_price"] == 999.0

    db_session.refresh(sub)
    assert sub.amount == 999.0
    assert sub.status == "active"

    log = db_session.query(ActionLog).filter(
        ActionLog.user_id == "u_test",
        ActionLog.subscription_id == sub.id,
        ActionLog.action_type == "NEGOTIATION_FAILED"
    ).first()
    assert log is not None
    assert log.amount == 999.0
    assert log.monthly_saving == 0.0
    assert log.annual_saving == 0.0


def test_case_4_negotiation_expires_original_price_remains(db_session):
    """
    Test Case 4: Negotiation expires -> original price remains.
    Original price = ₹999 -> Offer expires -> Price stays ₹999.
    """
    sub = Subscription(
        user_id="u_test",
        merchant="Case4Service",
        amount=999.0,
        currency="₹",
        category="developer_tools",
        status="active"
    )
    db_session.add(sub)
    db_session.commit()

    res = start_merchant_negotiation(sub_id=sub.id, db=db_session)
    offer = res["offer"]

    expire_res = expire_negotiated_offer(sub_id=sub.id, offer_id=offer.id, db=db_session)
    assert expire_res["monthly_savings"] == 0.0
    assert expire_res["annual_savings"] == 0.0
    assert expire_res["original_price"] == 999.0
    assert expire_res["final_price"] == 999.0

    db_session.refresh(sub)
    assert sub.amount == 999.0
    assert sub.status == "active"

    log = db_session.query(ActionLog).filter(
        ActionLog.user_id == "u_test",
        ActionLog.subscription_id == sub.id,
        ActionLog.action_type == "NEGOTIATION_FAILED"
    ).first()
    assert log is not None
    assert log.amount == 999.0
    assert log.monthly_saving == 0.0


def test_case_5_refresh_page_after_failed_negotiation_original_price_remains(db_session):
    """
    Test Case 5: Refresh page after failed negotiation -> original price remains.
    Verifies that calling GET /api/subscriptions/{sub_id} returns original price.
    """
    sub = Subscription(
        user_id="u_test",
        merchant="Case5Service",
        amount=999.0,
        currency="₹",
        category="music_streaming",
        status="active"
    )
    db_session.add(sub)
    db_session.commit()

    res = start_merchant_negotiation(sub_id=sub.id, db=db_session)
    offer = res["offer"]
    fail_negotiated_offer(sub_id=sub.id, offer_id=offer.id, db=db_session)

    # Simulate page refresh / fetching subscription detail
    refreshed_sub = get_subscription_detail(sub_id=sub.id, db=db_session)
    assert refreshed_sub.amount == 999.0
    assert refreshed_sub.status == "active"


def test_case_6_run_audit_again_after_failed_negotiation_original_price_remains(db_session):
    """
    Test Case 6: Run audit again after failed negotiation -> original price remains.
    Verifies that orchestrator.run_full_audit does not change price or auto-cancel.
    """
    sub = Subscription(
        user_id="u_test",
        merchant="Case6Service",
        amount=999.0,
        currency="₹",
        category="fitness",
        status="active"
    )
    db_session.add(sub)
    db_session.commit()

    res = start_merchant_negotiation(sub_id=sub.id, db=db_session)
    offer = res["offer"]
    fail_negotiated_offer(sub_id=sub.id, offer_id=offer.id, db=db_session)

    # Run audit again
    audit_res = orchestrator.run_full_audit(db=db_session, user_id="u_test")
    assert audit_res["status"] == "COMPLETED"

    # Verify subscription amount strictly remains ₹999
    db_session.refresh(sub)
    assert sub.amount == 999.0
    assert sub.status == "active"


def test_case_7_run_audit_again_after_accepted_negotiation_discount_not_applied_twice(db_session):
    """
    Test Case 7: Run audit again after accepted negotiation -> discount not applied twice.
    Verifies price stays ₹749.25 across multiple audit runs and is never re-discounted.
    """
    sub = Subscription(
        user_id="u_test",
        merchant="Case7Service",
        amount=999.0,
        currency="₹",
        category="productivity",
        status="active"
    )
    db_session.add(sub)
    db_session.commit()

    res = start_merchant_negotiation(sub_id=sub.id, db=db_session)
    offer = res["offer"]
    accept_negotiated_offer(sub_id=sub.id, offer_id=offer.id, db=db_session)

    db_session.refresh(sub)
    assert sub.amount == 749.25

    # Run audit 1st time
    orchestrator.run_full_audit(db=db_session, user_id="u_test")
    db_session.refresh(sub)
    assert sub.amount == 749.25

    # Run audit 2nd time
    orchestrator.run_full_audit(db=db_session, user_id="u_test")
    db_session.refresh(sub)
    assert sub.amount == 749.25


def test_case_8_failed_negotiation_produces_zero_realized_savings(db_session):
    """
    Test Case 8: Failed negotiation produces ₹0 realized savings.
    Verifies that realized_monthly_savings and realized_annual_savings are unchanged.
    """
    initial_metrics = get_savings_metrics(user_id="u_test", db=db_session)

    sub = Subscription(
        user_id="u_test",
        merchant="Case8Service",
        amount=999.0,
        currency="₹",
        category="entertainment",
        status="active"
    )
    db_session.add(sub)
    db_session.commit()

    res = start_merchant_negotiation(sub_id=sub.id, db=db_session)
    offer = res["offer"]
    fail_negotiated_offer(sub_id=sub.id, offer_id=offer.id, db=db_session)

    post_fail_metrics = get_savings_metrics(user_id="u_test", db=db_session)
    assert post_fail_metrics.realized_monthly_savings == initial_metrics.realized_monthly_savings
    assert post_fail_metrics.realized_annual_savings == initial_metrics.realized_annual_savings


def test_case_9_accepted_negotiation_produces_exactly_one_savings_entry(db_session):
    """
    Test Case 9: Accepted negotiation produces exactly one monthly & annual savings entry.
    Verifies that repeated accepts and audits do NOT duplicate ActionLogs or savings.
    """
    initial_metrics = get_savings_metrics(user_id="u_test", db=db_session)

    sub = Subscription(
        user_id="u_test",
        merchant="Case9Service",
        amount=999.0,
        currency="₹",
        category="streaming",
        status="active"
    )
    db_session.add(sub)
    db_session.commit()

    # Negotiation: 25% off ₹999 -> offered price ₹749.25, monthly saving ₹249.75
    res = start_merchant_negotiation(sub_id=sub.id, db=db_session)
    offer = res["offer"]

    # 1. Accept first time
    accept_negotiated_offer(sub_id=sub.id, offer_id=offer.id, db=db_session)

    # 2. Call accept again (idempotent call)
    accept_negotiated_offer(sub_id=sub.id, offer_id=offer.id, db=db_session)

    # 3. Run audit 1st time
    orchestrator.run_full_audit(db=db_session, user_id="u_test")

    # 4. Run audit 2nd time
    orchestrator.run_full_audit(db=db_session, user_id="u_test")

    # Verify exactly one ActionLog of type NEGOTIATION_ACCEPTED exists for this subscription
    logs = db_session.query(ActionLog).filter(
        ActionLog.user_id == "u_test",
        ActionLog.subscription_id == sub.id,
        ActionLog.action_type == "NEGOTIATION_ACCEPTED"
    ).all()
    assert len(logs) == 1
    assert logs[0].amount == 749.25
    assert logs[0].monthly_saving == 249.75
    assert logs[0].annual_saving == 2997.0

    # Running repeated audit must not duplicate savings
    metrics_audit1 = get_savings_metrics(user_id="u_test", db=db_session)
    orchestrator.run_full_audit(db=db_session, user_id="u_test")
    metrics_audit2 = get_savings_metrics(user_id="u_test", db=db_session)
    assert metrics_audit2.realized_monthly_savings == metrics_audit1.realized_monthly_savings
    assert metrics_audit2.realized_annual_savings == metrics_audit1.realized_annual_savings

