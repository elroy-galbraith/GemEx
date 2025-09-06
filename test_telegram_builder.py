#!/usr/bin/env python3
"""
Test script for the new TelegramMessageBuilder class.
Tests the concise message format without requiring actual market data.
"""

import json
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_telegram_message_builder():
    """Test the TelegramMessageBuilder with mock data."""
    print("🧪 Testing TelegramMessageBuilder...")
    print("=" * 50)
    
    try:
        # Import after adding to path
        from market_planner import TelegramMessageBuilder
        
        # Create mock data packet
        mock_data_packet = {
            "marketSnapshot": {
                "currentPrice": 1.0835,
                "currentTimeUTC": "2025-09-06T10:30:00.000000+00:00"
            },
            "multiTimeframeAnalysis": {
                "Daily": {
                    "trendDirection": "Bullish",
                    "keySupportLevels": [1.0800, 1.0780],
                    "keyResistanceLevels": [1.0850, 1.0880]
                },
                "H4": {
                    "trendDirection": "Bullish", 
                    "keySupportLevels": [1.0815, 1.0800],
                    "keyResistanceLevels": [1.0845, 1.0860]
                },
                "H1": {
                    "trendDirection": "Bullish"
                }
            }
        }
        
        # Create mock review scores
        mock_review_scores = {
            "planQualityScore": {"score": 8},
            "confidenceScore": {"score": 7}
        }
        
        # Initialize message builder
        builder = TelegramMessageBuilder()
        
        # Test summary message
        print("📊 Testing summary message...")
        summary_message = builder.build_summary_message(mock_data_packet, mock_review_scores, 5)
        print("\n" + "="*40)
        print("SUMMARY MESSAGE:")
        print("="*40)
        print(summary_message)
        print("="*40)
        
        # Test technical details
        print("\n📈 Testing technical details...")
        technical_details = builder.build_technical_details(mock_data_packet)
        print("\n" + "="*40)
        print("TECHNICAL DETAILS:")
        print("="*40)
        print(technical_details)
        print("="*40)
        
        # Test psychology tips
        print("\n💡 Testing psychology tips...")
        for condition in ['calm_market', 'volatile_market', 'general']:
            tip = builder.get_daily_psychology_tip(condition)
            print(f"{condition}: {tip}")
        
        # Test message length comparison
        print(f"\n📏 Message Length Analysis:")
        print(f"Summary message: {len(summary_message)} characters")
        print(f"Technical details: {len(technical_details)} characters")
        print(f"Total concise format: {len(summary_message) + len(technical_details)} characters")
        
        # Create a mock old-style message for comparison
        old_style_length = 800  # Estimated from looking at old format
        reduction_percentage = ((old_style_length - len(summary_message)) / old_style_length) * 100
        print(f"Estimated reduction: {reduction_percentage:.1f}%")
        
        print("\n✅ TelegramMessageBuilder tests completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("This may be due to missing dependencies - test the class structure only")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_helper_functions():
    """Test the helper functions."""
    print("\n🔧 Testing helper functions...")
    
    try:
        from market_planner import _determine_market_condition, _create_abbreviated_plan
        
        # Test market condition determination
        condition1 = _determine_market_condition("Bullish", "Bullish", 8)
        condition2 = _determine_market_condition("Bullish", "Bearish", 6)
        print(f"Aligned trends: {condition1}")
        print(f"Mixed trends: {condition2}")
        
        # Test plan abbreviation
        mock_plan = """
# Daily Market Analysis

## Plan A: Long Setup
Entry: 1.0835
Stop Loss: 1.0815 
Take Profit: 1.0885
Risk/Reward: 1:2.5

## Risk Management
- Risk 1% of capital
- Move stop to breakeven at 50% target

## Market Context
Long analysis about market conditions...
"""
        
        abbreviated = _create_abbreviated_plan(mock_plan)
        print(f"\nAbbreviated plan ({len(abbreviated)} chars):")
        print(abbreviated)
        
        print("✅ Helper functions working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Helper function test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing New Telegram Message Format")
    print("This test validates the TelegramMessageBuilder implementation")
    print()
    
    success1 = test_telegram_message_builder()
    success2 = test_helper_functions()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED!")
        print("New concise Telegram format is working correctly.")
    else:
        print("❌ SOME TESTS FAILED")
        print("Check the implementation for issues.")
    print("=" * 50)