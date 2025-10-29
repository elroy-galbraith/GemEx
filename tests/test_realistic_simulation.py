"""
Test the realistic simulation using actual price data.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gemex.ace.realistic_simulation import simulate_trade_with_real_data, backtest_trading_plan


def test_single_trade_simulation():
    """Test simulation with a sample trading plan."""
    
    # Actual trading plan from Oct 29, 2025
    trading_plan = {
        "date": "2025-10-29",
        "bias": "bearish_pattern",
        "entry_zone": [1.1644, 1.1645],   # Short entry zone (tight)
        "stop_loss": 1.1658,              # Stop loss above entry (bearish trade)
        "take_profit_1": 1.1633,          # Take profit 1 below entry
        "take_profit_2": 1.1628,          # Take profit 2 below entry
        "position_size_pct": 0.5,
        "risk_reward": "1:1.8",
        "confidence": "medium_probability",
        "rationale": "Research observation: EURUSD consolidating with bearish intermarket correlations (DXY up, US10Y down). Recent hourly candles show indecision. FOMC news ahead creates volatility risk. Short scalp opportunity before or after news event.",
        "playbook_bullets_used": ["strat-002", "code-001", "pit-001"]
    }
    
    print("=" * 60)
    print("Testing Realistic Trade Simulation")
    print("=" * 60)
    print(f"\nTrading Plan Date: {trading_plan['date']}")
    print(f"Bias: {trading_plan['bias']}")
    print(f"Entry Zone: {trading_plan['entry_zone']}")
    print(f"Stop Loss: {trading_plan['stop_loss']}")
    print(f"Take Profit: {trading_plan['take_profit_1']}")
    
    # Run simulation
    result = simulate_trade_with_real_data(trading_plan)
    
    print("\n" + "-" * 60)
    print("SIMULATION RESULT")
    print("-" * 60)
    
    if result["execution"]:
        exec_data = result["execution"]
        print(f"Status: {exec_data.get('status', 'EXECUTED')}")
        
        if "entry_price" in exec_data:
            print(f"Entry Time: {exec_data['entry_time']}")
            print(f"Entry Price: {exec_data['entry_price']:.5f}")
            print(f"Exit Time: {exec_data['exit_time']}")
            print(f"Exit Price: {exec_data['exit_price']:.5f}")
            print(f"Outcome: {exec_data['outcome'].upper()}")
            print(f"P&L: {exec_data['pnl_pips']:+d} pips (${exec_data['pnl_usd']:+d})")
            print(f"Method: {exec_data.get('method', 'unknown')}")
        else:
            print(f"Reason: {exec_data.get('reason', 'Unknown')}")
    else:
        print("No execution data available")
    
    print(f"\nFeedback:")
    print(f"  Entry Quality: {result['feedback']['entry_quality']}")
    print(f"  Exit Timing: {result['feedback']['exit_timing']}")
    
    return result


def test_backtest_week():
    """Test backtesting over a week."""
    
    trading_plan = {
        "bias": "bullish",
        "confidence": "high",
        "entry_zone": [1.0850, 1.0870],
        "stop_loss": 1.0830,
        "take_profit_1": 1.0920,
    }
    
    print("\n\n" + "=" * 60)
    print("Testing Week-Long Backtest")
    print("=" * 60)
    
    results = backtest_trading_plan(
        trading_plan,
        start_date="2025-10-20",
        end_date="2025-10-27"
    )
    
    print(f"\nBacktest Period: Oct 20-27, 2025")
    print(f"Total Trading Days: {len(results)}")
    
    wins = sum(1 for r in results if r["execution"] and r["execution"].get("outcome") == "win")
    losses = sum(1 for r in results if r["execution"] and r["execution"].get("outcome") == "loss")
    no_trades = sum(1 for r in results if r["execution"] and r["execution"].get("status") == "no_trade")
    
    total_pips = sum(
        r["execution"].get("pnl_pips", 0) 
        for r in results 
        if r["execution"] and "pnl_pips" in r["execution"]
    )
    
    print(f"\nResults:")
    print(f"  Wins: {wins}")
    print(f"  Losses: {losses}")
    print(f"  No Trades: {no_trades}")
    print(f"  Total P&L: {total_pips:+d} pips")
    
    if wins + losses > 0:
        win_rate = (wins / (wins + losses)) * 100
        print(f"  Win Rate: {win_rate:.1f}%")
    
    return results


if __name__ == "__main__":
    # Test single trade
    result = test_single_trade_simulation()
    
    # Test backtest (optional - uncomment to run)
    # backtest_results = test_backtest_week()
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
