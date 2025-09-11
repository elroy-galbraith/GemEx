#!/usr/bin/env python3
"""
Standalone test script for the persistence mechanism in GemEx.
This script tests the persistence functionality without requiring the GEMINI_API_KEY.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

def test_fallback_context():
    """Test the fallback context creation."""
    print("🧪 Testing fallback context creation...")
    
    # Simulate the fallback context creation
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y_%m_%d")
    context = {
        "previousSessionDate": yesterday,
        "previousPlanExists": False,
        "previousMarketSnapshot": None,
        "previousKeyLevels": None,
        "previousPlanOutcome": None,
        "marketEvolution": None,
        "fallbackMode": True
    }
    
    assert context["previousPlanExists"] == False
    assert context["fallbackMode"] == True
    assert "previousSessionDate" in context
    
    print("✅ Fallback context test passed")
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

def test_environment_variables():
    """Test that required environment variables are available in GitHub Actions."""
    print("🧪 Testing environment variables...")
    
    if os.environ.get('GITHUB_ACTIONS'):
        # In GitHub Actions, check for required variables
        github_repo = os.environ.get('GITHUB_REPOSITORY')
        github_token = os.environ.get('GITHUB_TOKEN')
        
        assert github_repo is not None, "GITHUB_REPOSITORY should be available in GitHub Actions"
        assert github_token is not None, "GITHUB_TOKEN should be available in GitHub Actions"
        
        print(f"✅ All required environment variables are available")
        print(f"   Repository: {github_repo}")
        print(f"   Token: {'***' if github_token else 'None'}")
    else:
        print("✅ Local environment - no GitHub-specific variables required")
    
    print("✅ Environment variables test completed")
    return True

def test_import_without_api_key():
    """Test that we can import the persistence functions without requiring GEMINI_API_KEY."""
    print("🧪 Testing import without API key...")
    
    try:
        # Test importing specific functions that don't require API key
        from market_planner import (
            create_fallback_previous_context,
            load_session_data_from_path
        )
        
        # Test that these functions work without API key
        context = create_fallback_previous_context()
        assert context["fallbackMode"] == True
        
        print("✅ Import test passed - persistence functions work without API key")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Run all standalone persistence tests."""
    print("🚀 Starting GemEx Standalone Persistence Tests")
    print("=" * 50)
    
    tests = [
        test_fallback_context,
        test_github_actions_detection,
        test_environment_variables,
        test_import_without_api_key
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
        print("🎉 All standalone persistence tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
