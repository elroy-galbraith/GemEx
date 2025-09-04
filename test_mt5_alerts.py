#!/usr/bin/env python3
"""
Test script for MT5 alerts functionality.
Tests the extract_mt5_alerts_from_plan function with sample trading plan content.
"""

import json
import sys
import os
from datetime import datetime, timezone

# Add the current directory to the path so we can import from market_planner
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mt5_alerts_extraction():
    """Test the MT5 alerts extraction with sample trading plan content."""
    
    # Sample trading plan content with various price levels
    sample_trading_plan = """
    # Daily Market Analysis - EURUSD
    
    ## Key Levels & Zones
    
    Upper Bound / Major Resistance: Price 1.1850. Justification: Previous Week's High, tested and held yesterday.
    Lower Bound / Major Support: Price 1.1650. Justification: Daily Demand Zone, confirmed by yesterday's bounce.
    Bull/Bear Pivot ("Line in the Sand"): Price 1.1720. Justification: Yesterday's key support level.
    Primary Value Zone: 1.1700 - 1.1730. Justification: Confluence of 50% Fib Retracement and yesterday's key level.
    
    ## Plan A: Primary Trade Idea
    
    Entry Protocol:
    Condition: Price must first pull back into the Primary Value Zone (1.1700 - 1.1730).
    Trigger: Execute on break above 1.1735.
    
    Stop Loss (SL): Price 1.1680. Justification: Placed 10 pips below the low of the Value Zone.
    Take Profit 1 (TP1): Price 1.1780. Justification: Targets the nearest liquidity pool.
    Take Profit 2 (TP2): Price 1.1820. Justification: Final target at Daily Major Resistance level.
    
    ## Plan B: Contingency Trade Idea
    
    Entry Protocol:
    Condition: If price rallies directly to Major Resistance (1.1850).
    Trigger: Execute short on rejection at 1.1845.
    
    Stop Loss (SL): Price 1.1870. Justification: Placed above the high of the rejection wick.
    Take Profit (TP): Price 1.1780. Justification: Targets the Bull/Bear Pivot as reversion point.
    """
    
    current_price = 1.1720
    
    try:
        # Import the function from market_planner
        from market_planner import extract_mt5_alerts_from_plan
        
        # Test the extraction
        print("🧪 Testing MT5 alerts extraction...")
        print(f"📊 Current price: {current_price}")
        print(f"📄 Trading plan length: {len(sample_trading_plan)} characters")
        
        alerts_data = extract_mt5_alerts_from_plan(sample_trading_plan, current_price)
        
        # Display results
        print(f"\n✅ Extraction successful!")
        print(f"📊 Generated {alerts_data['metadata']['total_alerts']} alerts")
        print(f"🎯 Symbol: {alerts_data['metadata']['symbol']}")
        print(f"💰 Current price: {alerts_data['metadata']['current_price']}")
        print(f"🕐 Generated at: {alerts_data['metadata']['generated_at']}")
        
        if alerts_data['alerts']:
            print("\n🔔 Generated Alerts:")
            print("-" * 60)
            for i, alert in enumerate(alerts_data['alerts'], 1):
                direction = "📈" if alert['condition'] in ['bid_above', 'ask_above'] else "📉"
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[alert['priority']]
                
                print(f"{i:2}. {direction} {alert['price']:.5f} ({alert['condition']})")
                print(f"    {priority_emoji} {alert['category'].upper()} - {alert['comment']}")
                print()
        
        # Save test output
        test_output_path = "/tmp/test_mt5_alerts.json"
        with open(test_output_path, 'w') as f:
            json.dump(alerts_data, f, indent=2)
        print(f"💾 Test output saved to: {test_output_path}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the GemEx directory")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def validate_alert_structure(alerts_data):
    """Validate the structure of the alerts data."""
    required_fields = ['alerts', 'metadata']
    alert_fields = ['symbol', 'price', 'condition', 'action', 'enabled', 'comment', 'category', 'priority']
    metadata_fields = ['generated_at', 'symbol', 'current_price', 'total_alerts']
    
    print("\n🔍 Validating alert structure...")
    
    # Check top-level structure
    for field in required_fields:
        if field not in alerts_data:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Check metadata
    metadata = alerts_data['metadata']
    for field in metadata_fields:
        if field not in metadata:
            print(f"❌ Missing metadata field: {field}")
            return False
    
    # Check each alert
    for i, alert in enumerate(alerts_data['alerts']):
        for field in alert_fields:
            if field not in alert:
                print(f"❌ Missing alert field in alert {i}: {field}")
                return False
        
        # Validate specific field types and values
        if not isinstance(alert['price'], (int, float)):
            print(f"❌ Invalid price type in alert {i}: {type(alert['price'])}")
            return False
        
        if alert['condition'] not in ['bid_above', 'bid_below', 'ask_above', 'ask_below']:
            print(f"❌ Invalid condition in alert {i}: {alert['condition']}")
            return False
        
        if alert['category'] not in ['entry', 'exit', 'level']:
            print(f"❌ Invalid category in alert {i}: {alert['category']}")
            return False
        
        if alert['priority'] not in ['high', 'medium', 'low']:
            print(f"❌ Invalid priority in alert {i}: {alert['priority']}")
            return False
    
    print("✅ Alert structure validation passed!")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 GemEx MT5 Alerts Test Suite")
    print("=" * 60)
    
    success = test_mt5_alerts_extraction()
    
    if success:
        # Load the test results for validation
        try:
            with open("/tmp/test_mt5_alerts.json", 'r') as f:
                test_data = json.load(f)
            validate_alert_structure(test_data)
        except Exception as e:
            print(f"⚠️  Could not validate structure: {e}")
    
    print("=" * 60)
    print("✅ Test completed!" if success else "❌ Test failed!")
    print("=" * 60)