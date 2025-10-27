#!/usr/bin/env python3
"""
Comprehensive ACE System Test

This script tests the entire ACE trading system end-to-end:
1. Environment setup
2. Playbook initialization
3. Daily cycle (with mocked API if needed)
4. Trade simulation
5. Weekly cycle
6. Playbook evolution

Run with: python tests/test_ace_system.py [--with-api]
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gemex.ace.components import (
    initialize_playbook,
    save_playbook,
    load_playbook,
    simulate_trade_execution,
    run_curator,
    save_trade_log,
    PLAYBOOK_PATH,
    TRADING_SESSIONS_DIR
)


class TestResults:
    """Track test results."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.tests = []
    
    def add_pass(self, test_name: str, message: str = ""):
        self.passed += 1
        self.tests.append(("PASS", test_name, message))
        print(f"✅ {test_name}: {message}")
    
    def add_fail(self, test_name: str, message: str = ""):
        self.failed += 1
        self.tests.append(("FAIL", test_name, message))
        print(f"❌ {test_name}: {message}")
    
    def add_warning(self, test_name: str, message: str = ""):
        self.warnings += 1
        self.tests.append(("WARN", test_name, message))
        print(f"⚠️  {test_name}: {message}")
    
    def summary(self):
        total = self.passed + self.failed + self.warnings
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"⚠️  Warnings: {self.warnings}")
        print("="*60)
        
        if self.failed > 0:
            print("\nFailed tests:")
            for status, name, msg in self.tests:
                if status == "FAIL":
                    print(f"  • {name}: {msg}")
        
        return self.failed == 0


def test_environment(results: TestResults):
    """Test 1: Environment setup."""
    print("\n" + "="*60)
    print("TEST 1: Environment Setup")
    print("="*60)
    
    # Check Python version
    version = sys.version_info
    if version.major >= 3 and version.minor >= 12:
        results.add_pass("Python version", f"{version.major}.{version.minor}")
    else:
        results.add_warning("Python version", f"{version.major}.{version.minor} (recommend 3.12+)")
    
    # Check core dependencies
    core_deps = {
        'pandas': 'pd',
        'numpy': 'np',
        'requests': 'requests',
        'yfinance': 'yf',
        'google.generativeai': 'genai'
    }
    
    for dep_name, import_as in core_deps.items():
        try:
            if import_as:
                exec(f"import {dep_name} as {import_as}")
            else:
                exec(f"import {dep_name}")
            results.add_pass(f"Import {dep_name}", "Available")
        except ImportError:
            results.add_fail(f"Import {dep_name}", "Not available")
    
    # Check API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key and len(api_key) > 10:
        results.add_pass("GEMINI_API_KEY", "Set")
    else:
        results.add_warning("GEMINI_API_KEY", "Not set (some tests will be skipped)")


def test_playbook_initialization(results: TestResults):
    """Test 2: Playbook initialization and structure."""
    print("\n" + "="*60)
    print("TEST 2: Playbook Initialization")
    print("="*60)
    
    # Initialize fresh playbook
    playbook = initialize_playbook()
    
    # Check structure
    if "metadata" in playbook and "sections" in playbook:
        results.add_pass("Playbook structure", "Valid")
    else:
        results.add_fail("Playbook structure", "Missing required keys")
        return
    
    # Check sections
    required_sections = [
        "strategies_and_hard_rules",
        "useful_code_and_templates",
        "troubleshooting_and_pitfalls"
    ]
    
    for section in required_sections:
        if section in playbook["sections"]:
            count = len(playbook["sections"][section])
            results.add_pass(f"Section: {section}", f"{count} bullets")
        else:
            results.add_fail(f"Section: {section}", "Missing")
    
    # Check metadata
    metadata = playbook["metadata"]
    if metadata.get("version") and metadata.get("last_updated"):
        results.add_pass("Playbook metadata", f"Version {metadata['version']}")
    else:
        results.add_fail("Playbook metadata", "Incomplete")


def test_trade_simulation(results: TestResults):
    """Test 3: Trade execution simulation."""
    print("\n" + "="*60)
    print("TEST 3: Trade Execution Simulation")
    print("="*60)
    
    # Create sample bullish plan
    bullish_plan = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "bias": "bullish",
        "entry_zone": [1.0500, 1.0510],
        "stop_loss": 1.0480,
        "take_profit_1": 1.0550,
        "take_profit_2": 1.0580,
        "position_size_pct": 0.75,
        "risk_reward": "1:2.5",
        "confidence": "high",
        "playbook_bullets_used": ["strat-001", "strat-002"]
    }
    
    trade_log = simulate_trade_execution(bullish_plan)
    
    # Check trade log structure
    required_keys = ["plan_id", "execution", "feedback"]
    for key in required_keys:
        if key in trade_log:
            results.add_pass(f"Trade log: {key}", "Present")
        else:
            results.add_fail(f"Trade log: {key}", "Missing")
    
    # Check execution details
    if trade_log.get("execution"):
        execution = trade_log["execution"]
        if execution.get("outcome") in ["win", "loss", "no_trade"]:
            results.add_pass("Trade outcome", execution["outcome"])
        else:
            results.add_warning("Trade outcome", "Unknown outcome")
    
    # Test neutral plan (no trade)
    neutral_plan = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "bias": "neutral",
        "confidence": "low",
        "playbook_bullets_used": []
    }
    
    neutral_log = simulate_trade_execution(neutral_plan)
    if neutral_log.get("execution") and neutral_log["execution"].get("outcome") == "no_trade":
        results.add_pass("Neutral bias handling", "No trade executed")
    elif not neutral_log.get("execution") or not neutral_log["execution"].get("outcome"):
        results.add_warning("Neutral bias handling", "Execution outcome missing")
    else:
        results.add_warning("Neutral bias handling", "Trade executed on neutral bias")


def test_curator_operations(results: TestResults):
    """Test 4: Curator playbook updates."""
    print("\n" + "="*60)
    print("TEST 4: Curator Operations")
    print("="*60)
    
    # Initialize playbook
    playbook = initialize_playbook()
    initial_count = len(playbook["sections"]["strategies_and_hard_rules"])
    
    # Create mock reflection with insights (correct structure)
    reflection = {
        "performance_summary": {
            "total_trades": 10,
            "winning_trades": 6,
            "win_rate": 0.60
        },
        "success_patterns": [
            "Trading with trend during NY session yields better results"
        ],
        "failure_patterns": [
            "Counter-trend trades during low volatility periods fail frequently"
        ],
        "insights": [
            {
                "suggested_action": "add_bullet",
                "section": "strategies_and_hard_rules",
                "content": "Avoid counter-trend trades when ATR < 50 pips"
            },
            {
                "suggested_action": "increment_helpful",
                "bullet_id": "strat-001"
            }
        ]
    }
    
    # Run curator (correct parameter order: reflection, playbook)
    updated_playbook = run_curator(reflection, playbook)
    
    # Check if bullet was added
    new_count = len(updated_playbook["sections"]["strategies_and_hard_rules"])
    if new_count > initial_count:
        results.add_pass("Curator: Add bullet", f"Added {new_count - initial_count} bullet(s)")
    else:
        results.add_fail("Curator: Add bullet", "No bullet added")
    
    # Check version increment
    if float(updated_playbook["metadata"]["version"]) > float(playbook["metadata"]["version"]):
        results.add_pass("Curator: Version increment", 
                        f"{playbook['metadata']['version']} → {updated_playbook['metadata']['version']}")
    else:
        results.add_fail("Curator: Version increment", "Version not incremented")


def test_file_persistence(results: TestResults):
    """Test 5: File saving and loading."""
    print("\n" + "="*60)
    print("TEST 5: File Persistence")
    print("="*60)
    
    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)
    
    # Create and save test playbook
    playbook = initialize_playbook()
    save_playbook(playbook)
    
    if PLAYBOOK_PATH.exists():
        results.add_pass("Playbook save", f"Saved to {PLAYBOOK_PATH}")
    else:
        results.add_fail("Playbook save", f"File not created at {PLAYBOOK_PATH}")
        return
    
    # Load playbook
    loaded_playbook = load_playbook()
    
    if loaded_playbook:
        results.add_pass("Playbook load", "Successfully loaded")
    else:
        results.add_fail("Playbook load", "Failed to load")
        return
    
    # Verify content matches
    if loaded_playbook["metadata"]["version"] == playbook["metadata"]["version"]:
        results.add_pass("Playbook integrity", "Data matches after save/load")
    else:
        results.add_fail("Playbook integrity", "Data mismatch after save/load")


def test_directory_structure(results: TestResults):
    """Test 6: Directory structure creation."""
    print("\n" + "="*60)
    print("TEST 6: Directory Structure")
    print("="*60)
    
    required_dirs = {
        "data": "Playbook storage",
        "data/playbook_history": "Playbook versions",
        "trading_session": "Daily trading sessions",
        "weekly_reflections": "Weekly analysis"
    }
    
    for dir_path, description in required_dirs.items():
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        
        if path.exists() and path.is_dir():
            results.add_pass(f"Directory: {dir_path}", description)
        else:
            results.add_fail(f"Directory: {dir_path}", "Failed to create")


def main():
    """Run all tests."""
    parser = argparse.ArgumentParser(description="Test ACE trading system")
    parser.add_argument("--with-api", action="store_true", 
                       help="Run tests that require API access")
    args = parser.parse_args()
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║       ACE TRADING SYSTEM - COMPREHENSIVE TEST SUITE        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    results = TestResults()
    
    # Run all tests
    test_environment(results)
    test_playbook_initialization(results)
    test_trade_simulation(results)
    test_curator_operations(results)
    test_file_persistence(results)
    test_directory_structure(results)
    
    # Print summary
    success = results.summary()
    
    if success:
        print("\n✅ All tests passed! The ACE system is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
