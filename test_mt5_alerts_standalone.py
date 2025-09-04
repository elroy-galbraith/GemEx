#!/usr/bin/env python3
"""
Standalone test for MT5 alerts functionality.
Tests the extract_mt5_alerts_from_plan function without requiring full dependencies.
"""

import json
import re
from datetime import datetime, timezone

def extract_mt5_alerts_from_plan(trade_plan_text, current_price):
    """Extract price levels from trading plan and generate MT5 alerts JSON."""
    alerts = []
    
    # Helper function to create alert object
    def create_alert(price, condition, comment, category, priority="medium"):
        return {
            "symbol": "EURUSD",
            "price": float(price),
            "condition": condition,
            "action": "notification",
            "enabled": True,
            "comment": comment,
            "category": category,
            "priority": priority
        }
    
    # Extract price levels using regex patterns
    price_patterns = [
        (r"Entry.*?(\d+\.\d{4,5})", "entry", "high"),
        (r"Stop Loss.*?(\d+\.\d{4,5})", "exit", "high"), 
        (r"Take Profit.*?(\d+\.\d{4,5})", "exit", "high"),
        (r"TP1.*?(\d+\.\d{4,5})", "exit", "high"),
        (r"TP2.*?(\d+\.\d{4,5})", "exit", "medium"),
        (r"Upper Bound.*?(\d+\.\d{4,5})", "level", "medium"),
        (r"Lower Bound.*?(\d+\.\d{4,5})", "level", "medium"),
        (r"Major Resistance.*?(\d+\.\d{4,5})", "level", "medium"),
        (r"Major Support.*?(\d+\.\d{4,5})", "level", "medium"),
        (r"Bull/Bear Pivot.*?(\d+\.\d{4,5})", "level", "high"),
        (r"Primary Value Zone.*?(\d+\.\d{4,5})", "level", "medium")
    ]
    
    for pattern, category, priority in price_patterns:
        matches = re.findall(pattern, trade_plan_text, re.IGNORECASE)
        for match in matches:
            try:
                price_level = float(match)
                
                # Determine alert condition based on current price
                if price_level > current_price:
                    condition = "bid_above"
                    direction = "above"
                else:
                    condition = "bid_below" 
                    direction = "below"
                
                # Create descriptive comment based on category
                if category == "entry":
                    comment = f"Entry signal triggered {direction} {price_level}"
                elif category == "exit":
                    comment = f"Exit level reached {direction} {price_level}"
                else:
                    comment = f"Key level {direction} {price_level}"
                
                alerts.append(create_alert(price_level, condition, comment, category, priority))
                
            except ValueError:
                continue
    
    # Remove duplicates based on price level
    seen_prices = set()
    unique_alerts = []
    for alert in alerts:
        if alert["price"] not in seen_prices:
            seen_prices.add(alert["price"])
            unique_alerts.append(alert)
    
    # Sort alerts by price level
    unique_alerts.sort(key=lambda x: x["price"])
    
    return {
        "alerts": unique_alerts,
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "symbol": "EURUSD",
            "current_price": current_price,
            "total_alerts": len(unique_alerts)
        }
    }

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
    Trigger: Execute on break above Entry 1.1735.
    
    Stop Loss (SL): Price 1.1680. Justification: Placed 10 pips below the low of the Value Zone.
    Take Profit 1 (TP1): Price 1.1780. Justification: Targets the nearest liquidity pool.
    Take Profit 2 (TP2): Price 1.1820. Justification: Final target at Daily Major Resistance level.
    
    ## Plan B: Contingency Trade Idea
    
    Entry Protocol:
    Condition: If price rallies directly to Major Resistance (1.1850).
    Trigger: Execute short on rejection at Entry 1.1845.
    
    Stop Loss (SL): Price 1.1870. Justification: Placed above the high of the rejection wick.
    Take Profit (TP): Price 1.1780. Justification: Targets the Bull/Bear Pivot as reversion point.
    """
    
    current_price = 1.1720
    
    try:        
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
        
        return alerts_data
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None

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
    print("🔧 GemEx MT5 Alerts Test Suite (Standalone)")
    print("=" * 60)
    
    alerts_data = test_mt5_alerts_extraction()
    
    if alerts_data:
        valid = validate_alert_structure(alerts_data)
        print("\n📋 Sample JSON structure:")
        print(json.dumps(alerts_data, indent=2)[:500] + "..." if len(json.dumps(alerts_data, indent=2)) > 500 else json.dumps(alerts_data, indent=2))
        
    print("=" * 60)
    print("✅ Test completed!" if alerts_data else "❌ Test failed!")
    print("=" * 60)