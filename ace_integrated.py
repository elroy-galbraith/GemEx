"""
ACE Integration Example

This file demonstrates how to integrate ACE components with the existing
market_planner.py functions to create a complete trading system.

Note: This requires all dependencies to be installed (yfinance, google-generativeai, etc.)
For a dependency-free demo, use ace_demo.py instead.
"""

import sys
from pathlib import Path
from datetime import datetime

# Check if dependencies are available
try:
    # Import existing market_planner functions
    from market_planner import (
        get_market_data,
        get_intermarket_analysis,
        get_economic_calendar,
        export_charts,
        SYMBOLS,
        send_telegram_message,
        TELEGRAM_BOT_TOKEN,
        TELEGRAM_CHAT_ID,
        DATE_OUTPUT_DIR,
        OUTPUT_DIR
    )
    MARKET_PLANNER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  market_planner dependencies not available: {e}")
    print("   Install dependencies with: pip install -r requirements.txt")
    MARKET_PLANNER_AVAILABLE = False

# Import ACE components
from ace_components import (
    load_playbook,
    save_playbook,
    run_generator,
    simulate_trade_execution,
    save_trade_log,
    run_reflector,
    save_reflection,
    run_curator,
    load_trade_logs_for_week
)


def ace_daily_cycle_integrated():
    """
    Run ACE daily cycle with full market data integration.
    
    This is the production version that uses real market data.
    """
    if not MARKET_PLANNER_AVAILABLE:
        print("❌ Cannot run integrated cycle - dependencies missing")
        sys.exit(1)
    
    print("=" * 70)
    print("ACE FOREX TRADING - DAILY CYCLE (INTEGRATED)")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ensure directories exist
    OUTPUT_DIR.mkdir(exist_ok=True)
    DATE_OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Step 1: Load Playbook
    print("\n[1/7] Loading Playbook...")
    playbook = load_playbook()
    print(f"📚 Playbook v{playbook['metadata']['version']} loaded")
    print(f"   Total bullets: {playbook['metadata']['total_bullets']}")
    
    # Step 2: Gather Real Market Data
    print("\n[2/7] Gathering Market Data...")
    try:
        # Get EURUSD data
        eurusd_data = get_market_data(SYMBOLS["EURUSD"], "1d", "1h")
        current_price = eurusd_data.iloc[-1]["Close"] if not eurusd_data.empty else 1.0000
        
        # Get intermarket data
        intermarket_symbols = {k: v for k, v in SYMBOLS.items() if k != 'EURUSD'}
        intermarket = get_intermarket_analysis(intermarket_symbols)
        
        # Get economic calendar
        news_events = get_economic_calendar()
        
        # Create market snapshot
        market_data = {
            "timestamp": datetime.now().isoformat(),
            "eurusd": {
                "current_price": current_price,
                "timeframe_1h": eurusd_data.tail(24).to_dict('records') if not eurusd_data.empty else []
            },
            "intermarket": intermarket,
            "news_events": news_events[:5] if news_events else [],
        }
        
        print(f"✅ Market data gathered (EURUSD: {current_price:.5f})")
        
    except Exception as e:
        print(f"⚠️  Error gathering market data: {e}")
        market_data = {
            "timestamp": datetime.now().isoformat(),
            "eurusd": {"current_price": 1.0000},
            "error": str(e)
        }
    
    # Step 3: Generate Charts
    print("\n[3/7] Generating Technical Charts...")
    try:
        export_charts()
        print("✅ Charts generated successfully")
    except Exception as e:
        print(f"⚠️  Chart generation failed: {e}")
    
    # Step 4: Run Generator (ACE)
    print("\n[4/7] Running Generator (Creating Trading Plan)...")
    trading_plan = run_generator(playbook, market_data)
    
    # Add current date
    if "date" not in trading_plan:
        trading_plan["date"] = datetime.now().strftime("%Y-%m-%d")
    
    # Save plan
    from ace_main import save_trading_plan
    save_trading_plan(trading_plan)
    
    print(f"✅ Trading plan generated")
    print(f"   Bias: {trading_plan.get('bias', 'N/A').upper()}")
    print(f"   Confidence: {trading_plan.get('confidence', 'N/A').upper()}")
    
    # Step 5: Send to Telegram
    print("\n[5/7] Sending Plan to Telegram...")
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        from ace_main import send_telegram_trading_plan
        send_telegram_trading_plan(trading_plan)
    else:
        print("⏭️  Telegram not configured")
    
    # Step 6: Simulate Execution
    print("\n[6/7] Simulating Trade Execution...")
    trade_log = simulate_trade_execution(trading_plan)
    save_trade_log(trade_log)
    
    if trade_log.get("execution") and "outcome" in trade_log["execution"]:
        print(f"   Outcome: {trade_log['execution']['outcome'].upper()}")
        if "pnl_pips" in trade_log["execution"]:
            print(f"   P&L: {trade_log['execution']['pnl_pips']:+d} pips")
    
    # Step 7: Save Updated Playbook
    print("\n[7/7] Saving Updated Playbook...")
    save_playbook(playbook)
    
    print("\n" + "=" * 70)
    print("DAILY CYCLE COMPLETE")
    print("=" * 70)
    
    return trade_log


def ace_weekly_cycle_integrated():
    """
    Run ACE weekly cycle with full reflection capabilities.
    
    This analyzes the week's trades and updates the playbook.
    """
    print("=" * 70)
    print("ACE FOREX TRADING - WEEKLY CYCLE (INTEGRATED)")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Step 1: Load Weekly Logs
    print("\n[1/4] Loading Weekly Trade Logs...")
    weekly_logs = load_trade_logs_for_week()
    
    if not weekly_logs:
        print("⚠️  No trade logs found for this week")
        return
    
    print(f"📊 Loaded {len(weekly_logs)} trade logs")
    
    # Step 2: Run Reflector
    print("\n[2/4] Running Reflector (Analyzing Performance)...")
    playbook = load_playbook()
    reflection = run_reflector(weekly_logs, playbook)
    save_reflection(reflection)
    
    # Display summary
    summary = reflection.get("summary", {})
    print(f"\n📊 Weekly Performance:")
    print(f"   Total Trades: {summary.get('total_trades', 0)}")
    print(f"   Win Rate: {summary.get('win_rate', 0):.1%}")
    print(f"   Total Pips: {summary.get('total_pips', 0):+d}")
    
    # Step 3: Run Curator
    print("\n[3/4] Running Curator (Updating Playbook)...")
    updated_playbook = run_curator(reflection, playbook)
    save_playbook(updated_playbook)
    
    print(f"   Version: {playbook['metadata']['version']} → {updated_playbook['metadata']['version']}")
    print(f"   Total bullets: {updated_playbook['metadata']['total_bullets']}")
    
    # Step 4: Send Summary to Telegram
    print("\n[4/4] Sending Weekly Summary...")
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID and MARKET_PLANNER_AVAILABLE:
        from ace_main import send_telegram_weekly_summary
        send_telegram_weekly_summary(weekly_logs, reflection, updated_playbook)
    else:
        print("⏭️  Telegram not configured")
    
    print("\n" + "=" * 70)
    print("WEEKLY CYCLE COMPLETE")
    print("=" * 70)


def main():
    """Main entry point for integrated ACE system."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ACE Forex Trading System (Integrated with market_planner)"
    )
    parser.add_argument(
        "--cycle",
        choices=["daily", "weekly"],
        default="daily",
        help="Which cycle to run"
    )
    
    args = parser.parse_args()
    
    try:
        if args.cycle == "daily":
            ace_daily_cycle_integrated()
        elif args.cycle == "weekly":
            ace_weekly_cycle_integrated()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
