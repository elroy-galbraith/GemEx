"""
Realistic Trade Simulation Using Actual Historical Price Data

This module enhances the simulation by validating trades against real market movement
instead of using deterministic hash-based outcomes.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import yfinance as yf


def simulate_trade_with_real_data(
    trading_plan: Dict[str, Any],
    lookback_hours: int = 8
) -> Dict[str, Any]:
    """
    Simulate trade execution using actual historical price data.
    
    This checks if:
    1. Price actually entered the entry zone
    2. Which level hit first: stop loss or take profit
    3. Actual P&L based on real price movement
    
    Args:
        trading_plan: The trading plan with entry zone, SL, TP levels
        lookback_hours: How many hours after plan generation to check (default 8 for NY session)
        
    Returns:
        Trade log with realistic execution details
    """
    trade_log = {
        "plan_id": trading_plan.get("date", datetime.now().strftime("%Y-%m-%d")),
        "execution": None,
        "feedback": {
            "entry_quality": "not_triggered",
            "exit_timing": "n/a",
            "unexpected_events": [],
            "playbook_bullets_feedback": {}
        }
    }
    
    # Handle neutral bias
    bias = trading_plan.get("bias", "neutral")
    if "neutral" in bias.lower() or "entry_zone" not in trading_plan:
        trade_log["execution"] = {
            "status": "no_trade",
            "reason": "Neutral bias or no entry criteria met"
        }
        return trade_log
    
    # Get required price levels from trading plan
    entry_zone = trading_plan.get("entry_zone", [])
    stop_loss = trading_plan.get("stop_loss")
    take_profit_1 = trading_plan.get("take_profit_1")
    
    if not entry_zone or not stop_loss or not take_profit_1:
        trade_log["execution"] = {
            "status": "no_trade",
            "reason": "Missing required price levels (entry/SL/TP)"
        }
        return trade_log
    
    # Determine trade direction
    entry_min = min(entry_zone)
    entry_max = max(entry_zone)
    entry_mid = (entry_min + entry_max) / 2
    
    is_long = take_profit_1 > entry_mid
    
    # Fetch actual price data for the trading session
    try:
        plan_date = datetime.strptime(trading_plan["date"], "%Y-%m-%d")
        
        # Get 15-minute data for the day (gives us detailed price action)
        ticker = yf.Ticker("EURUSD=X")
        start_time = plan_date.replace(hour=13, minute=0)  # 1 PM UTC (9 AM EST - just before NY open)
        end_time = start_time + timedelta(hours=lookback_hours)
        
        price_data = ticker.history(
            start=start_time,
            end=end_time,
            interval="15m"
        )
        
        if price_data.empty:
            # No data available (weekend/holiday) - fall back to simple simulation
            return _fallback_simulation(trading_plan, "No price data available for this date")
        
        # Check if price entered the entry zone
        entry_triggered = False
        entry_time = None
        entry_price = None
        
        for idx, row in price_data.iterrows():
            # Check if price touched the entry zone
            if entry_min <= row['Low'] <= entry_max or entry_min <= row['High'] <= entry_max:
                entry_triggered = True
                entry_time = idx
                # Use mid-point of entry zone as fill price (realistic assumption)
                entry_price = entry_mid
                break
            # For long trades, check if price went below entry zone (better entry)
            if is_long and row['Low'] <= entry_min:
                entry_triggered = True
                entry_time = idx
                entry_price = entry_min
                break
            # For short trades, check if price went above entry zone
            if not is_long and row['High'] >= entry_max:
                entry_triggered = True
                entry_time = idx
                entry_price = entry_max
                break
        
        if not entry_triggered:
            trade_log["execution"] = {
                "status": "no_trade",
                "reason": "Entry zone never triggered by price action"
            }
            trade_log["feedback"]["entry_quality"] = "not_triggered"
            return trade_log
        
        # Entry was triggered - now check which level hit first (SL or TP)
        outcome = None
        exit_time = None
        exit_price = None
        
        # Check price action after entry
        for idx, row in price_data[price_data.index > entry_time].iterrows():
            if is_long:
                # Check if stop loss hit
                if row['Low'] <= stop_loss:
                    outcome = "loss"
                    exit_time = idx
                    exit_price = stop_loss
                    break
                # Check if take profit hit
                if row['High'] >= take_profit_1:
                    outcome = "win"
                    exit_time = idx
                    exit_price = take_profit_1
                    break
            else:  # Short trade
                # Check if stop loss hit
                if row['High'] >= stop_loss:
                    outcome = "loss"
                    exit_time = idx
                    exit_price = stop_loss
                    break
                # Check if take profit hit
                if row['Low'] <= take_profit_1:
                    outcome = "win"
                    exit_time = idx
                    exit_price = take_profit_1
                    break
        
        # If neither SL nor TP hit by end of session, close at market
        if outcome is None:
            exit_time = price_data.index[-1]
            exit_price = price_data.iloc[-1]['Close']
            
            # Determine if it's a win or loss based on current P&L
            if is_long:
                outcome = "win" if exit_price > entry_price else "loss"
            else:
                outcome = "win" if exit_price < entry_price else "loss"
        
        # Calculate P&L
        if is_long:
            pnl_pips = int((exit_price - entry_price) * 10000)
        else:
            pnl_pips = int((entry_price - exit_price) * 10000)
        
        # Create execution log
        trade_log["execution"] = {
            "entry_time": entry_time.isoformat(),
            "entry_price": round(entry_price, 5),
            "exit_time": exit_time.isoformat(),
            "exit_price": round(exit_price, 5),
            "pnl_pips": pnl_pips,
            "pnl_usd": pnl_pips * 10,  # Assuming $10/pip
            "outcome": outcome,
            "method": "real_price_data"
        }
        
        trade_log["feedback"]["entry_quality"] = "good"
        trade_log["feedback"]["exit_timing"] = "take_profit_hit" if outcome == "win" else "stopped_out"
        
        return trade_log
        
    except Exception as e:
        print(f"⚠️  Error fetching price data: {e}")
        return _fallback_simulation(trading_plan, f"Data error: {str(e)}")


def _fallback_simulation(trading_plan: Dict[str, Any], reason: str) -> Dict[str, Any]:
    """
    Fallback to simple simulation when real data isn't available.
    This is the original hash-based simulation logic.
    """
    trade_log = {
        "plan_id": trading_plan.get("date", datetime.now().strftime("%Y-%m-%d")),
        "execution": None,
        "feedback": {
            "entry_quality": "simulated",
            "exit_timing": "simulated",
            "unexpected_events": [reason],
            "playbook_bullets_feedback": {}
        }
    }
    
    confidence = trading_plan.get("confidence", "medium")
    
    # Hash-based outcome
    if confidence == "high":
        outcome = "win" if hash(trading_plan["date"]) % 3 != 0 else "loss"
    elif confidence == "medium":
        outcome = "win" if hash(trading_plan["date"]) % 2 == 0 else "loss"
    else:
        outcome = "loss"
    
    if "entry_zone" in trading_plan:
        entry_price = sum(trading_plan["entry_zone"]) / 2
        
        if outcome == "win":
            exit_price = trading_plan.get("take_profit_1", entry_price * 1.002)
            pnl_pips = int((exit_price - entry_price) * 10000)
        else:
            exit_price = trading_plan.get("stop_loss", entry_price * 0.998)
            pnl_pips = int((exit_price - entry_price) * 10000)
        
        trade_log["execution"] = {
            "entry_time": f"{trading_plan['date']}T14:00:00Z",
            "entry_price": entry_price,
            "exit_time": f"{trading_plan['date']}T16:30:00Z",
            "exit_price": exit_price,
            "pnl_pips": pnl_pips,
            "pnl_usd": pnl_pips * 10,
            "outcome": outcome,
            "method": "hash_based_fallback"
        }
    
    return trade_log


def backtest_trading_plan(
    trading_plan: Dict[str, Any],
    start_date: str,
    end_date: str
) -> List[Dict[str, Any]]:
    """
    Backtest a trading plan strategy over a date range.
    
    This is useful for testing if a playbook pattern would have worked
    historically.
    
    Args:
        trading_plan: The trading plan template to test
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        List of trade logs for each day
    """
    results = []
    
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    current = start
    
    while current <= end:
        # Skip weekends
        if current.weekday() < 5:  # Monday = 0, Friday = 4
            daily_plan = trading_plan.copy()
            daily_plan["date"] = current.strftime("%Y-%m-%d")
            
            result = simulate_trade_with_real_data(daily_plan)
            results.append(result)
        
        current += timedelta(days=1)
    
    return results
