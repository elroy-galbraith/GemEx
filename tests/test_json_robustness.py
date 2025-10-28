"""
Test JSON parsing robustness in ACE components.

This script tests the enhanced JSON cleaning and error handling.
"""

import json
from pathlib import Path

# Test cases for malformed JSON responses
test_cases = [
    {
        "name": "Valid JSON with markdown wrapper",
        "input": '```json\n{"bias": "bullish", "confidence": "high"}\n```',
        "should_succeed": True
    },
    {
        "name": "Valid JSON with JSON identifier",
        "input": '```json\n{"bias": "bearish", "confidence": "medium"}\n```',
        "should_succeed": True
    },
    {
        "name": "Valid JSON with uppercase JSON",
        "input": '```JSON\n{"bias": "neutral", "confidence": "low"}\n```',
        "should_succeed": True
    },
    {
        "name": "Unterminated string (original error)",
        "input": '```json\n{"bias": "bullish",\n"rationale": "This is an unterminated string\n```',
        "should_succeed": False
    },
    {
        "name": "Missing closing brace",
        "input": '```json\n{"bias": "bullish", "confidence": "high"\n```',
        "should_succeed": False
    },
    {
        "name": "Plain JSON without markdown",
        "input": '{"bias": "neutral", "confidence": "medium"}',
        "should_succeed": True
    },
    {
        "name": "Extra trailing text",
        "input": '```json\n{"bias": "bullish", "confidence": "high"}\n```\n\nHere is some extra text',
        "should_succeed": True  # Should extract valid JSON part
    }
]


def clean_json_response(text: str) -> str:
    """
    Replicate the cleaning logic from components.py
    """
    plan_text = text.strip()
    
    # Clean JSON if wrapped in markdown
    if plan_text.startswith("```"):
        parts = plan_text.split("```")
        if len(parts) >= 2:
            plan_text = parts[1]
            if plan_text.strip().startswith("json"):
                plan_text = plan_text.strip()[4:].strip()
            elif plan_text.strip().startswith("JSON"):
                plan_text = plan_text.strip()[4:].strip()
    
    # Remove any trailing markdown markers
    if plan_text.endswith("```"):
        plan_text = plan_text[:-3].strip()
    
    return plan_text


def test_json_parsing():
    """Test JSON parsing with various inputs."""
    print("🧪 Testing JSON parsing robustness\n")
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['name']}")
        print(f"  Input: {test['input'][:60]}..." if len(test['input']) > 60 else f"  Input: {test['input']}")
        
        try:
            cleaned = clean_json_response(test['input'])
            result = json.loads(cleaned)
            
            if test['should_succeed']:
                print(f"  ✅ PASS - Successfully parsed: {result}")
                passed += 1
            else:
                print(f"  ❌ FAIL - Should have failed but succeeded: {result}")
                failed += 1
                
        except json.JSONDecodeError as e:
            if not test['should_succeed']:
                print(f"  ✅ PASS - Correctly failed: {e}")
                passed += 1
            else:
                print(f"  ❌ FAIL - Should have succeeded but failed: {e}")
                print(f"     Cleaned text: {clean_json_response(test['input'])}")
                failed += 1
        except Exception as e:
            print(f"  ❌ UNEXPECTED ERROR: {e}")
            failed += 1
        
        print()
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print(f"{'='*60}\n")
    
    if failed == 0:
        print("✅ All tests passed!")
        return True
    else:
        print(f"⚠️  {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = test_json_parsing()
    exit(0 if success else 1)
