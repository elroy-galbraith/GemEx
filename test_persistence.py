#!/usr/bin/env python3
"""
Test script for the persistence mechanism in GemEx.
This script tests the ability to download and use previous session data.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add the current directory to the path so we can import market_planner
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from market_planner import (
    download_previous_session_artifacts,
    create_fallback_previous_context,
    get_previous_session_analysis
)

def test_fallback_context():
    """Test the fallback context creation."""
    print("🧪 Testing fallback context creation...")
    
    context = create_fallback_previous_context()
    
    assert context["previousPlanExists"] == False
    assert context["fallbackMode"] == True
    assert "previousSessionDate" in context
    
    print("✅ Fallback context test passed")
    return True

def test_local_session_loading():
    """Test loading local session data if it exists."""
    print("🧪 Testing local session loading...")
    
    # Check if we have any local session data
    trading_session_dir = Path("trading_session")
    if trading_session_dir.exists():
        session_dirs = list(trading_session_dir.glob("20*"))
        if session_dirs:
            print(f"Found {len(session_dirs)} local session directories")
            for session_dir in session_dirs:
                print(f"  - {session_dir.name}")
        else:
            print("No local session directories found")
    else:
        print("No trading_session directory found")
    
    print("✅ Local session loading test completed")
    return True

def test_github_actions_detection():
    """Test GitHub Actions environment detection."""
    print("🧪 Testing GitHub Actions environment detection...")
    
    # Check if we're in GitHub Actions
    in_github_actions = os.environ.get('GITHUB_ACTIONS') is not None
    print(f"Running in GitHub Actions: {in_github_actions}")
    
    if in_github_actions:
        print("GitHub Actions environment detected")
        github_repo = os.environ.get('GITHUB_REPOSITORY')
        github_token = os.environ.get('GITHUB_TOKEN')
        print(f"Repository: {github_repo}")
        print(f"Token available: {github_token is not None}")
    else:
        print("Local environment detected")
    
    print("✅ GitHub Actions detection test completed")
    return True

def test_previous_session_analysis():
    """Test the complete previous session analysis."""
    print("🧪 Testing previous session analysis...")
    
    try:
        context = get_previous_session_analysis()
        
        # Verify the context structure
        required_keys = [
            "previousSessionDate",
            "previousPlanExists",
            "previousMarketSnapshot",
            "previousKeyLevels",
            "previousPlanOutcome"
        ]
        
        for key in required_keys:
            assert key in context, f"Missing key: {key}"
        
        print(f"Previous session date: {context['previousSessionDate']}")
        print(f"Previous plan exists: {context['previousPlanExists']}")
        print(f"Fallback mode: {context.get('fallbackMode', False)}")
        
        print("✅ Previous session analysis test passed")
        return True
        
    except Exception as e:
        print(f"❌ Previous session analysis test failed: {e}")
        return False

def main():
    """Run all persistence tests."""
    print("🚀 Starting GemEx Persistence Tests")
    print("=" * 50)
    
    tests = [
        test_fallback_context,
        test_local_session_loading,
        test_github_actions_detection,
        test_previous_session_analysis
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All persistence tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
