#!/usr/bin/env python3
"""
Test script for JSON parsing and cleaning functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gemex.market_planner import clean_json_output

def test_json_cleaning():
    """Test the JSON cleaning function with various inputs."""
    print("🧪 Testing JSON cleaning function...")
    
    test_cases = [
        # Case 1: Clean JSON
        {
            "input": '{"planQualityScore": {"score": 8, "justification": "Good plan"}}',
            "expected": '{"planQualityScore": {"score": 8, "justification": "Good plan"}}'
        },
        # Case 2: JSON with markdown
        {
            "input": '```json\n{"planQualityScore": {"score": 8, "justification": "Good plan"}}\n```',
            "expected": '{"planQualityScore": {"score": 8, "justification": "Good plan"}}'
        },
        # Case 3: JSON with extra text
        {
            "input": 'Here is the analysis:\n{"planQualityScore": {"score": 8, "justification": "Good plan"}}\nEnd of analysis.',
            "expected": '{"planQualityScore": {"score": 8, "justification": "Good plan"}}'
        },
        # Case 4: Empty input
        {
            "input": '',
            "expected": ''
        },
        # Case 5: No JSON
        {
            "input": 'This is not JSON at all',
            "expected": 'This is not JSON at all'
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        result = clean_json_output(test_case["input"])
        if result == test_case["expected"]:
            print(f"✅ Test case {i} passed")
            passed += 1
        else:
            print(f"❌ Test case {i} failed")
            print(f"   Input: {repr(test_case['input'])}")
            print(f"   Expected: {repr(test_case['expected'])}")
            print(f"   Got: {repr(result)}")
    
    print(f"\n📊 JSON Cleaning Tests: {passed}/{total} passed")
    return passed == total

def test_json_parsing():
    """Test JSON parsing with the cleaned output."""
    print("\n🧪 Testing JSON parsing...")
    
    import json
    
    # Test valid JSON
    valid_json = '{"planQualityScore": {"score": 8, "justification": "Good plan"}, "confidenceScore": {"score": 7, "justification": "High confidence"}}'
    cleaned = clean_json_output(valid_json)
    
    try:
        parsed = json.loads(cleaned)
        if "planQualityScore" in parsed and "confidenceScore" in parsed:
            print("✅ Valid JSON parsing test passed")
            return True
        else:
            print("❌ Valid JSON parsing test failed - missing required fields")
            return False
    except json.JSONDecodeError as e:
        print(f"❌ Valid JSON parsing test failed - JSON decode error: {e}")
        return False

def main():
    """Run all JSON parsing tests."""
    print("🚀 Starting JSON Parsing Tests")
    print("=" * 50)
    
    tests = [
        test_json_cleaning,
        test_json_parsing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All JSON parsing tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
