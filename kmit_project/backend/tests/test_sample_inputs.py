import pytest
from app.agent.guardrail_engine import guardrail_engine
from app.agent.waste_analyzer import waste_analyzer
from app.agent.confidence_engine import confidence_engine
from app.agent.bundle_detector import bundle_detector

def test_input_1_clear_waste_safe_to_act():
    """
    INPUT 1 from Problem Statement:
    Charge: StreamFlix, $14.99/month, last_used_days_ago=187.
    Guardrail: auto_action_limit = 20.
    Expected: Auto-cancel, log reason ("unused 187 days, under $20 auto-action limit").
    """
    charge = {
        "merchant": "StreamFlix",
        "amount": 14.99,
        "cadence": "monthly",
        "category": "video_streaming",
        "last_used_days_ago": 187,
        "transaction_count": 6
    }
    guardrail = {
        "auto_action_limit": 20.0,
        "protected_categories": ["insurance", "loan_payment"],
        "min_confidence_threshold": 0.85,
        "require_approval_for_duplicates": True
    }

    # 1. Calculate waste score
    waste_score = waste_analyzer.calculate_waste_score(charge)
    assert waste_score >= 50, f"Waste score should be high for 187 days inactive: {waste_score}"
    charge["waste_score"] = waste_score

    # 2. Calculate confidence
    confidence = confidence_engine.calculate_confidence(charge)
    assert confidence >= 0.85, f"Confidence should be high for clear unused service: {confidence}"
    charge["confidence_score"] = confidence

    # 3. Guardrail evaluation
    decision_result = guardrail_engine.evaluate(charge, guardrail)

    assert decision_result["passed"] is True
    assert decision_result["decision"] == "AUTO_CANCEL"
    assert decision_result["status"] == "PASSED"
    assert "under the auto-action limit" in decision_result["message"].lower() or "unused" in decision_result["message"].lower()


def test_input_2_ambiguous_overlapping_services():
    """
    INPUT 2 from Problem Statement:
    Charges: TuneWave $9.99 (used 4 days ago) vs MusicBox Premium $11.99 (used 40 days ago).
    Flag: overlapping_category, category: music_streaming.
    Expected: Recognize duplicate category, recommend keeping TuneWave, ask user before cancelling MusicBox.
    """
    subs = [
        {"merchant": "TuneWave", "amount": 9.99, "category": "music_streaming", "last_used_days_ago": 4, "transaction_count": 4},
        {"merchant": "MusicBox Premium", "amount": 11.99, "category": "music_streaming", "last_used_days_ago": 40, "transaction_count": 4}
    ]
    guardrail = {
        "auto_action_limit": 20.0,
        "protected_categories": ["insurance", "loan_payment"],
        "min_confidence_threshold": 0.85,
        "require_approval_for_duplicates": True
    }

    # 1. Bundle / Duplicate detection
    subs_with_dup = bundle_detector.check_bundles_and_duplicates(subs)
    
    musicbox = next(s for s in subs_with_dup if s["merchant"] == "MusicBox Premium")
    tunewave = next(s for s in subs_with_dup if s["merchant"] == "TuneWave")

    assert musicbox["is_duplicate_detected"] is True
    assert tunewave["is_duplicate_detected"] is True

    # 2. Confidence evaluation
    musicbox["waste_score"] = waste_analyzer.calculate_waste_score(musicbox)
    musicbox["confidence_score"] = confidence_engine.calculate_confidence(musicbox)

    # For duplicate category, confidence must be conservative (< 0.85)
    assert musicbox["confidence_score"] < 0.85

    # 3. Guardrail check
    decision_result = guardrail_engine.evaluate(musicbox, guardrail)

    # Autonomy MUST be blocked; must escalate to user
    assert decision_result["passed"] is False
    assert decision_result["decision"] == "ESCALATE_APPROVAL"
    assert decision_result["status"] == "BLOCKED_AMBIGUOUS_DUPLICATE"


def test_input_3_guardrail_blocks_protected_category():
    """
    INPUT 3 from Problem Statement:
    Charge: HealthGuard Insurance, $89.00/month, category: "insurance".
    Guardrail: protected_categories = ["insurance", "loan_payment"].
    Expected: Never auto-cancel — escalate with reasoning, regardless of usage (even 200+ days).
    """
    charge = {
        "merchant": "HealthGuard Insurance",
        "amount": 89.00,
        "cadence": "monthly",
        "category": "insurance",
        "last_used_days_ago": 210,  # Highly inactive
        "transaction_count": 6
    }
    guardrail = {
        "auto_action_limit": 20.0,
        "protected_categories": ["insurance", "loan_payment"],
        "min_confidence_threshold": 0.85,
        "require_approval_for_duplicates": True
    }

    charge["waste_score"] = waste_analyzer.calculate_waste_score(charge)
    charge["confidence_score"] = confidence_engine.calculate_confidence(charge)

    decision_result = guardrail_engine.evaluate(charge, guardrail)

    # Autonomy MUST be strictly prohibited
    assert decision_result["passed"] is False
    assert decision_result["decision"] == "ESCALATE_APPROVAL"
    assert decision_result["status"] == "BLOCKED_PROTECTED"
    assert "protected" in decision_result["message"].lower()


def test_price_hike_detection():
    """Verifies that unscheduled price hikes increase waste score and alert user."""
    charge = {
        "merchant": "Canva Pro",
        "amount": 599,
        "old_price": 499,
        "hike_percentage": 20.0,
        "price_hike_detected": True,
        "last_used_days_ago": 60,
        "category": "productivity"
    }
    waste_score = waste_analyzer.calculate_waste_score(charge)
    assert waste_score >= 45, "Waste score should include price hike penalty points"


def test_bundle_redundancy_detection():
    """Verifies that standalone music streaming is flagged as redundant when YouTube Premium is active."""
    subs = [
        {"merchant": "YouTube Premium", "category": "video_streaming", "last_used_days_ago": 1},
        {"merchant": "Spotify", "category": "music_streaming", "last_used_days_ago": 30}
    ]
    checked = bundle_detector.check_bundles_and_duplicates(subs)
    spotify = next(s for s in checked if s["merchant"] == "Spotify")
    assert spotify.get("is_bundled") is True
    assert "YouTube Premium" in spotify.get("bundle_provider")
