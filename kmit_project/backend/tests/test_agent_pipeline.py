import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.agent.orchestrator import orchestrator
from app.data.seed_data import seed_initial_data
from app.models import Subscription, ActionLog

# In-memory database for testing
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

def test_full_agent_audit_pipeline(db_session):
    """Verifies that running the full audit produces expected subscriptions, auto-cancellations, and logs."""
    result = orchestrator.run_full_audit(
        db=db_session,
        user_id="u_test",
        user_prompt="Audit my subscriptions and cancel inactive ones"
    )

    assert result["status"] == "COMPLETED"
    assert result["total_subscriptions_scanned"] > 0
    assert result["auto_cancelled_count"] >= 1
    assert result["potential_monthly_savings"] > 0
    assert len(result["audit_trace"]) >= 5

    # Check StreamFlix was auto-cancelled
    streamflix = db_session.query(Subscription).filter(
        Subscription.user_id == "u_test",
        Subscription.merchant == "StreamFlix"
    ).first()
    assert streamflix is not None
    assert streamflix.status == "cancelled"
    assert streamflix.action_taken == "AUTO_CANCELLED"

    # Check HealthGuard Insurance was protected
    insurance = db_session.query(Subscription).filter(
        Subscription.user_id == "u_test",
        Subscription.merchant == "HealthGuard Insurance"
    ).first()
    assert insurance is not None
    assert insurance.status == "protected"
    assert insurance.guardrail_status == "BLOCKED_PROTECTED"

    # Check MusicBox Premium was escalated
    musicbox = db_session.query(Subscription).filter(
        Subscription.user_id == "u_test",
        Subscription.merchant == "MusicBox Premium"
    ).first()
    assert musicbox is not None
    assert musicbox.status == "pending_approval"
    assert musicbox.is_duplicate_detected is True

    # Check Action Logs created
    action_logs = db_session.query(ActionLog).filter(ActionLog.user_id == "u_test").all()
    assert len(action_logs) >= 3

def test_process_user_prompt(db_session):
    """Verifies that user prompts for audits and inquiries are processed correctly."""
    # 1. Audit Prompt
    audit_res = orchestrator.process_user_prompt(
        db=db_session,
        user_id="u_test",
        prompt="Audit my subscriptions and clean up waste"
    )
    assert audit_res["intent"] == "AUDIT_EXECUTION"
    assert "StreamFlix" in audit_res["reply"] or "Completed" in audit_res["reply"]
    assert audit_res["monthly_savings"] > 0

    # 2. Informational Query Prompt
    query_res = orchestrator.process_user_prompt(
        db=db_session,
        user_id="u_test",
        prompt="How much money am I saving?"
    )
    assert query_res["intent"] == "QUERY_ANSWER"
    assert "saving" in query_res["reply"].lower()

    # 3. Direct Cancel Prompt
    cancel_res = orchestrator.process_user_prompt(
        db=db_session,
        user_id="u_test",
        prompt="cancel StreamFlix"
    )
    assert cancel_res["intent"] == "DIRECT_ACTION"
    assert "cancelled streamflix" in cancel_res["reply"].lower()

def test_repeated_audit_idempotency_no_duplicate_savings(db_session):
    """
    Verifies that running the audit repeatedly is completely idempotent:
    1. First Run: StreamFlix and other inactive subscriptions auto-cancel, savings recorded.
    2. Second Run: Already-cancelled subscriptions are skipped, no duplicate ActionLogs, savings remain unchanged.
    3. Third Run: Savings remain unchanged, no duplicate ActionLogs.
    """
    from app.routes.savings import get_savings_metrics

    # --- FIRST AUDIT ---
    res1 = orchestrator.run_full_audit(db=db_session, user_id="u_test")
    assert res1["status"] == "COMPLETED"
    
    metrics1 = get_savings_metrics(user_id="u_test", db=db_session)
    first_realized_monthly = metrics1.realized_monthly_savings
    first_realized_annual = metrics1.realized_annual_savings
    first_potential_monthly = metrics1.potential_monthly_savings
    assert first_realized_monthly > 0

    # StreamFlix log count after first audit
    streamflix_logs_1 = db_session.query(ActionLog).filter(
        ActionLog.user_id == "u_test",
        ActionLog.merchant == "StreamFlix",
        ActionLog.action_type == "AUTO_CANCEL"
    ).count()
    assert streamflix_logs_1 == 1

    total_logs_1 = db_session.query(ActionLog).filter(ActionLog.user_id == "u_test").count()

    # --- SECOND AUDIT (Repeated run) ---
    res2 = orchestrator.run_full_audit(db=db_session, user_id="u_test")
    assert res2["status"] == "COMPLETED"

    metrics2 = get_savings_metrics(user_id="u_test", db=db_session)
    assert metrics2.realized_monthly_savings == first_realized_monthly, (
        f"Monthly savings must not increase! Expected {first_realized_monthly}, got {metrics2.realized_monthly_savings}"
    )
    assert metrics2.realized_annual_savings == first_realized_annual
    assert metrics2.potential_monthly_savings == first_potential_monthly
    assert metrics2.auto_cancelled_count == metrics1.auto_cancelled_count

    # Check that no new AUTO_CANCEL ActionLog was created for StreamFlix
    streamflix_logs_2 = db_session.query(ActionLog).filter(
        ActionLog.user_id == "u_test",
        ActionLog.merchant == "StreamFlix",
        ActionLog.action_type == "AUTO_CANCEL"
    ).count()
    assert streamflix_logs_2 == 1, "Duplicate StreamFlix ActionLog must not be created!"

    total_logs_2 = db_session.query(ActionLog).filter(ActionLog.user_id == "u_test").count()
    assert total_logs_2 == total_logs_1, "Total ActionLogs must not increase on repeated audit!"

    # --- THIRD AUDIT (Repeated run) ---
    res3 = orchestrator.run_full_audit(db=db_session, user_id="u_test")
    assert res3["status"] == "COMPLETED"

    metrics3 = get_savings_metrics(user_id="u_test", db=db_session)
    assert metrics3.realized_monthly_savings == first_realized_monthly, (
        f"Monthly savings must remain constant on 3rd audit! Expected {first_realized_monthly}, got {metrics3.realized_monthly_savings}"
    )
    assert metrics3.potential_monthly_savings == first_potential_monthly
    assert metrics3.auto_cancelled_count == metrics1.auto_cancelled_count

    streamflix_logs_3 = db_session.query(ActionLog).filter(
        ActionLog.user_id == "u_test",
        ActionLog.merchant == "StreamFlix",
        ActionLog.action_type == "AUTO_CANCEL"
    ).count()
    assert streamflix_logs_3 == 1

def test_manual_subscription_creation_and_audit(db_session):
    """
    Verifies that manually added subscriptions are:
    1. Saved in SQLite with Waste Score, Confidence, and Price Hike analysis.
    2. Synchronized with a Transaction record.
    3. Processed and audited by the Agent Orchestrator according to guardrails.
    """
    from app.routes.subscriptions import create_subscription
    from app.schemas import SubscriptionCreate
    from app.models import Transaction

    # 1. Add manual inactive subscription under limit (Netflix: ₹649, inactive 120 days)
    netflix_data = SubscriptionCreate(
        user_id="u_test",
        merchant="Netflix",
        amount=649.0,
        currency="₹",
        category="video_streaming",
        cadence="monthly",
        last_used_days_ago=120,
        previous_price=499.0,
        is_duplicate=False,
        transaction_date="2026-03-01"
    )
    sub = create_subscription(data=netflix_data, db=db_session)
    assert sub.merchant == "Netflix"
    assert sub.waste_score >= 80  # high waste due to 120 days inactivity
    assert sub.price_hike_detected is True
    assert sub.hike_percentage > 0

    # Verify transaction record was created
    tx = db_session.query(Transaction).filter(
        Transaction.user_id == "u_test",
        Transaction.merchant == "Netflix"
    ).first()
    assert tx is not None
    assert tx.amount == 649.0

    # 2. Run Audit - Netflix should be detected from DB and auto-cancelled (amount <= 2000 limit)
    audit_res = orchestrator.run_full_audit(db=db_session, user_id="u_test")
    assert audit_res["status"] == "COMPLETED"

    netflix_sub = db_session.query(Subscription).filter(
        Subscription.user_id == "u_test",
        Subscription.merchant == "Netflix"
    ).first()
    assert netflix_sub.status == "cancelled"
    assert netflix_sub.action_taken == "AUTO_CANCELLED"

    # Verify action log recorded
    netflix_log = db_session.query(ActionLog).filter(
        ActionLog.user_id == "u_test",
        ActionLog.merchant == "Netflix"
    ).first()
    assert netflix_log is not None
    assert netflix_log.monthly_saving == 649.0

    # 3. Add manual subscription exceeding auto limit (SuperCloud: ₹4,500, inactive 100 days)
    cloud_data = SubscriptionCreate(
        user_id="u_test",
        merchant="SuperCloud",
        amount=4500.0,
        currency="₹",
        category="developer_tools",
        cadence="monthly",
        last_used_days_ago=100
    )
    cloud_sub = create_subscription(data=cloud_data, db=db_session)
    assert cloud_sub.guardrail_status == "BLOCKED_LIMIT"
    assert cloud_sub.status == "pending_approval"


