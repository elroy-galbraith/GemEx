"""
Tests for ACE Components

These tests validate the core ACE functionality without requiring API keys.
"""

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ace_components import (
    initialize_playbook,
    save_playbook,
    load_playbook,
    generate_bullet_id,
    simulate_trade_execution,
    run_curator,
    load_trade_logs_for_week,
    update_bullet_usage,
    PLAYBOOK_PATH,
    PLAYBOOK_HISTORY_DIR,
    TRADING_SESSIONS_DIR
)


def test_initialize_playbook():
    """Test playbook initialization."""
    playbook = initialize_playbook()
    
    # Check structure
    assert "metadata" in playbook
    assert "sections" in playbook
    assert "strategies_and_hard_rules" in playbook["sections"]
    assert "useful_code_and_templates" in playbook["sections"]
    assert "troubleshooting_and_pitfalls" in playbook["sections"]
    
    # Check metadata
    assert playbook["metadata"]["version"] == "1.0"
    assert playbook["metadata"]["total_bullets"] == 5
    
    # Check initial bullets exist
    assert len(playbook["sections"]["strategies_and_hard_rules"]) == 3
    assert len(playbook["sections"]["useful_code_and_templates"]) == 1
    assert len(playbook["sections"]["troubleshooting_and_pitfalls"]) == 1
    
    print("✅ test_initialize_playbook passed")


def test_bullet_id_generation():
    """Test bullet ID generation."""
    bullet_id = generate_bullet_id("strategies_and_hard_rules")
    
    # Check format
    assert bullet_id.startswith("stra-")
    assert len(bullet_id) > 10  # Should have timestamp
    
    print("✅ test_bullet_id_generation passed")


def test_simulate_trade_execution():
    """Test trade execution simulation."""
    
    # Test with bullish plan
    trading_plan = {
        "date": "2025-01-05",
        "bias": "bullish",
        "entry_zone": [1.0485, 1.0495],
        "stop_loss": 1.0465,
        "take_profit_1": 1.0535,
        "take_profit_2": 1.0565,
        "position_size_pct": 0.75,
        "risk_reward": "1:2.5",
        "confidence": "high",
        "playbook_bullets_used": ["strat-001"]
    }
    
    trade_log = simulate_trade_execution(trading_plan)
    
    # Check structure
    assert "plan_id" in trade_log
    assert "execution" in trade_log
    assert "feedback" in trade_log
    
    # Check execution details
    if trade_log["execution"] and trade_log["execution"].get("outcome"):
        assert trade_log["execution"]["outcome"] in ["win", "loss"]
        assert "pnl_pips" in trade_log["execution"]
    
    print("✅ test_simulate_trade_execution passed")


def test_simulate_neutral_plan():
    """Test simulation with neutral bias (no trade)."""
    
    trading_plan = {
        "date": "2025-01-05",
        "bias": "neutral",
        "rationale": "No clear setup",
        "confidence": "low"
    }
    
    trade_log = simulate_trade_execution(trading_plan)
    
    # Should have no trade status
    assert trade_log["execution"]["status"] == "no_trade"
    assert "reason" in trade_log["execution"]
    
    print("✅ test_simulate_neutral_plan passed")


def test_curator_add_bullet():
    """Test curator adding new bullets."""
    
    # Create initial playbook
    playbook = initialize_playbook()
    initial_bullet_count = playbook["metadata"]["total_bullets"]
    
    # Create reflection with add insight
    reflection = {
        "week_ending": "2025-01-05",
        "summary": {"total_trades": 5, "win_rate": 0.6},
        "insights": [
            {
                "type": "success_pattern",
                "suggested_action": "add_bullet",
                "section": "strategies_and_hard_rules",
                "content": "Test strategy: Always check DXY before entering",
                "priority": "high"
            }
        ],
        "recommendations": []
    }
    
    # Run curator
    updated_playbook = run_curator(reflection, playbook)
    
    # Check bullet was added
    assert updated_playbook["metadata"]["total_bullets"] == initial_bullet_count + 1
    
    # Check bullet exists in section
    found = False
    for bullet in updated_playbook["sections"]["strategies_and_hard_rules"]:
        if "check DXY" in bullet["content"]:
            found = True
            break
    assert found, "New bullet not found in playbook"
    
    print("✅ test_curator_add_bullet passed")


def test_curator_increment_counts():
    """Test curator incrementing helpful/harmful counts."""
    
    playbook = initialize_playbook()
    bullet_id = playbook["sections"]["strategies_and_hard_rules"][0]["id"]
    
    # Create reflection with increment insights
    reflection = {
        "week_ending": "2025-01-05",
        "summary": {"total_trades": 5},
        "insights": [
            {
                "type": "playbook_validation",
                "suggested_action": "increment_helpful",
                "bullet_id": bullet_id
            }
        ],
        "recommendations": []
    }
    
    # Run curator
    updated_playbook = run_curator(reflection, playbook)
    
    # Check count was incremented
    bullet = None
    for b in updated_playbook["sections"]["strategies_and_hard_rules"]:
        if b["id"] == bullet_id:
            bullet = b
            break
    
    assert bullet is not None
    assert bullet["helpful_count"] == 1
    
    print("✅ test_curator_increment_counts passed")


def test_curator_prune_harmful():
    """Test curator removing harmful bullets."""
    
    playbook = initialize_playbook()
    
    # Add a harmful bullet
    harmful_bullet = {
        "id": "test-harmful",
        "content": "Test harmful rule",
        "helpful_count": 1,
        "harmful_count": 5,  # Much more harmful than helpful
        "created_at": datetime.now().isoformat(),
        "last_used": None
    }
    playbook["sections"]["strategies_and_hard_rules"].append(harmful_bullet)
    playbook["metadata"]["total_bullets"] += 1
    
    initial_count = playbook["metadata"]["total_bullets"]
    
    # Run curator with empty reflection (just triggers pruning)
    reflection = {
        "week_ending": "2025-01-05",
        "summary": {},
        "insights": [],
        "recommendations": []
    }
    
    updated_playbook = run_curator(reflection, playbook)
    
    # Check harmful bullet was removed
    assert updated_playbook["metadata"]["total_bullets"] < initial_count
    
    # Verify the harmful bullet is gone
    for bullet in updated_playbook["sections"]["strategies_and_hard_rules"]:
        assert bullet["id"] != "test-harmful"
    
    print("✅ test_curator_prune_harmful passed")


def test_update_bullet_usage():
    """Test updating bullet usage timestamp."""
    
    playbook = initialize_playbook()
    bullet_id = playbook["sections"]["strategies_and_hard_rules"][0]["id"]
    
    # Initially should be None
    assert playbook["sections"]["strategies_and_hard_rules"][0]["last_used"] is None
    
    # Update usage
    update_bullet_usage(playbook, bullet_id)
    
    # Should now have timestamp
    assert playbook["sections"]["strategies_and_hard_rules"][0]["last_used"] is not None
    
    print("✅ test_update_bullet_usage passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Running ACE Component Tests")
    print("=" * 60 + "\n")
    
    tests = [
        test_initialize_playbook,
        test_bullet_id_generation,
        test_simulate_trade_execution,
        test_simulate_neutral_plan,
        test_curator_add_bullet,
        test_curator_increment_counts,
        test_curator_prune_harmful,
        test_update_bullet_usage,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
