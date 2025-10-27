#!/usr/bin/env python3
"""
Test script to verify that the reviewer LLM call fix works correctly.
This test simulates the reviewer pipeline without requiring a full market data run.
"""

import json
import sys
import os
from pathlib import Path

# Add the project root to Python path so we can import modules
sys.path.insert(0, str(Path(__file__).parent))

from gemex.prompts import REVIEWER_SYSTEM_PROMPT
from gemex.market_planner import call_llm, clean_json_output, configure_gemini

def test_reviewer_with_mock_data():
    """Test the reviewer with mock trading plan and data packet."""
    
    # Mock data packet (simplified)
    mock_data_packet = {
        "marketSnapshot": {
            "pair": "EURUSD",
            "currentPrice": 1.0850,
            "currentTimeUTC": "2025-01-09T10:00:00Z"
        },
        "multiTimeframeAnalysis": {
            "Daily": {"trendDirection": "Bullish"},
            "H4": {"trendDirection": "Bullish"},
            "H1": {"trendDirection": "Consolidating"}
        }
    }
    
    # Mock trade plan
    mock_trade_plan = """
# EURUSD Trading Plan - 2025-01-09

## Daily Market Thesis & Narrative
**Overarching Bias:** High-Conviction Bullish
**Primary Narrative:** EURUSD showing strong bullish momentum with clear break above 1.0800 resistance.

## Key Levels & Zones
**Upper Bound / Major Resistance:** 1.0900 (Weekly resistance level)
**Lower Bound / Major Support:** 1.0800 (Previous resistance, now support)
**Bull/Bear Pivot:** 1.0820 (Break below invalidates bullish bias)
**Primary Value Zone:** 1.0830 - 1.0840

## Plan A: Primary Trade Idea
**Trade Objective:** Long from Value Zone retest
**Entry:** 1.0835
**Stop Loss:** 1.0815 (20 pips)
**Take Profit 1:** 1.0885 (50 pips)
**Take Profit 2:** 1.0915 (80 pips)
**Risk/Reward:** 1:4.0

## Risk Management
- Risk 0.75% of capital
- Move SL to breakeven at TP1
"""
    
    print("🧪 Testing Reviewer LLM Call...")
    print("=" * 50)
    
    try:
        # Check if API key is configured
        configure_gemini()
        print("✅ Gemini API configured successfully")
        
        # Create reviewer prompt (same as in run_viper_coil)
        reviewer_user_prompt = f"""
        Here is the original data packet and the proposed trade plan. Analyze both and provide your scores.

        ### ORIGINAL DATA PACKET
        ```json
        {json.dumps(mock_data_packet, indent=2)}
        ```

        ### PROPOSED TRADE PLAN
        ```markdown
        {mock_trade_plan}
        ```
        """
        
        print("\n📤 Calling Reviewer LLM...")
        print(f"System prompt length: {len(REVIEWER_SYSTEM_PROMPT)} chars")
        print(f"User prompt length: {len(reviewer_user_prompt)} chars")
        
        # Call the LLM with the system prompt (this should now work correctly)
        review_output_raw = call_llm(REVIEWER_SYSTEM_PROMPT, reviewer_user_prompt)
        
        print("\n📥 Raw Reviewer Response:")
        print("-" * 30)
        print(review_output_raw[:500] + "..." if len(review_output_raw) > 500 else review_output_raw)
        print("-" * 30)
        
        # Try to parse the JSON
        cleaned_output = clean_json_output(review_output_raw)
        
        if cleaned_output:
            try:
                review_scores = json.loads(cleaned_output)
                print("\n✅ JSON Parsing Successful!")
                print(f"Plan Quality Score: {review_scores.get('planQualityScore', {}).get('score', 'N/A')}")
                print(f"Confidence Score: {review_scores.get('confidenceScore', {}).get('score', 'N/A')}")
                
                # Check if we got real scores (not the fallback 0 scores)
                quality_score = review_scores.get('planQualityScore', {}).get('score', 0)
                confidence_score = review_scores.get('confidenceScore', {}).get('score', 0)
                
                if quality_score > 0 and confidence_score > 0:
                    print("🎉 SUCCESS: Got real reviewer scores (not fallback)!")
                    return True
                else:
                    print("⚠️  WARNING: Got fallback scores (0/10) - system prompt may not be working")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parsing Failed: {e}")
                print(f"Cleaned output: {cleaned_output[:200]}...")
                return False
        else:
            print("❌ No valid output from clean_json_output function")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Reviewer LLM Fix")
    print("This test verifies that the system prompt is being used correctly.")
    print()
    
    success = test_reviewer_with_mock_data()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TEST PASSED: Reviewer is now working correctly!")
    else:
        print("❌ TEST FAILED: There may still be issues with the reviewer.")
    print("=" * 50)
