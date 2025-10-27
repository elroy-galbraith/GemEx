"""
ACE Main Orchestration Module

This module orchestrates the daily and weekly cycles of the ACE trading system:
- Daily cycle: Generate trading plan → Execute (simulated) → Log outcome
- Weekly cycle: Reflect on performance → Update playbook
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

# Import existing market data functions
# Using sys.path to allow importing from parent directory during transition
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from market_planner import (
    get_market_data,
    get_intermarket_analysis,
    get_economic_calendar,
    export_charts,
    SYMBOLS,
    DATE_OUTPUT_DIR,
    OUTPUT_DIR,
    send_telegram_message,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID
)

# Import ACE components from same package
from gemex.ace.components import (
    load_playbook,
    save_playbook,
    run_generator,
    simulate_trade_execution,
    save_trade_log,
    run_reflector,
    save_reflection,
    run_curator,
    load_trade_logs_for_week,
    TRADING_SESSIONS_DIR
)


def gather_market_data() -> Dict[str, Any]:
    """
    Gather all market data needed for trading plan generation.
    Reuses existing market data functions.
    """
    print("\n📊 Gathering market data...")
    
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "eurusd": {
                "current_price": current_price,
                "timeframe_1h": eurusd_data.tail(24).to_dict('records') if not eurusd_data.empty else []
            },
            "intermarket": intermarket,
            "news_events": news_events[:5] if news_events else [],  # Top 5 events
            "chart_analysis_available": True
        }
        
        print(f"✅ Market data gathered (EURUSD: {current_price:.5f})")
        return market_data
        
    except Exception as e:
        print(f"⚠️  Error gathering market data: {e}")
        # Return minimal data
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "eurusd": {"current_price": 1.0000},
            "error": str(e)
        }


def save_trading_plan(trading_plan: Dict[str, Any], date: str = None) -> None:
    """Save trading plan to the daily session folder."""
    if date is None:
        date = datetime.now().strftime("%Y_%m_%d")
    
    session_dir = TRADING_SESSIONS_DIR / date
    session_dir.mkdir(parents=True, exist_ok=True)
    
    plan_path = session_dir / "trading_plan.json"
    with open(plan_path, 'w') as f:
        json.dump(trading_plan, f, indent=2)
    
    # Also create a markdown version for human readability
    md_path = session_dir / "trading_plan.md"
    with open(md_path, 'w') as f:
        f.write(f"# Trading Plan - {trading_plan.get('date', date)}\n\n")
        f.write(f"**Bias**: {trading_plan.get('bias', 'N/A').upper()}\n\n")
        f.write(f"**Confidence**: {trading_plan.get('confidence', 'N/A').upper()}\n\n")
        
        if trading_plan.get('bias') != 'neutral' and 'entry_zone' in trading_plan:
            f.write(f"## Trade Setup\n\n")
            f.write(f"- **Entry Zone**: {trading_plan['entry_zone'][0]:.5f} - {trading_plan['entry_zone'][1]:.5f}\n")
            f.write(f"- **Stop Loss**: {trading_plan.get('stop_loss', 'N/A'):.5f}\n")
            f.write(f"- **Take Profit 1**: {trading_plan.get('take_profit_1', 'N/A'):.5f}\n")
            f.write(f"- **Take Profit 2**: {trading_plan['take_profit_2']:.5f}\n" if 'take_profit_2' in trading_plan and trading_plan['take_profit_2'] is not None else f"- **Take Profit 2**: N/A\n")
            f.write(f"- **Position Size**: {trading_plan.get('position_size_pct', 0.75):.2f}%\n")
            f.write(f"- **Risk/Reward**: {trading_plan.get('risk_reward', 'N/A')}\n\n")
        
        f.write(f"## Rationale\n\n{trading_plan.get('rationale', 'N/A')}\n\n")
        
        if 'playbook_bullets_used' in trading_plan and trading_plan['playbook_bullets_used']:
            f.write(f"## Playbook Rules Applied\n\n")
            for bullet_id in trading_plan['playbook_bullets_used']:
                f.write(f"- {bullet_id}\n")
    
    print(f"✅ Trading plan saved to: {plan_path}")


def send_telegram_trading_plan(trading_plan: Dict[str, Any]) -> None:
    """Send trading plan to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⏭️  Telegram not configured, skipping notification")
        return
    
    try:
        # Format message
        bias_emoji = {"bullish": "📈", "bearish": "📉", "neutral": "➡️"}.get(
            trading_plan.get("bias", "neutral"), "➡️"
        )
        confidence_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(
            trading_plan.get("confidence", "medium"), "🟡"
        )
        
        message = f"""
🤖 **ACE Trading Plan** - {trading_plan.get('date', 'Today')}

{bias_emoji} **Bias**: {trading_plan.get('bias', 'N/A').upper()}
{confidence_emoji} **Confidence**: {trading_plan.get('confidence', 'N/A').upper()}

"""
        
        if trading_plan.get('bias') != 'neutral' and 'entry_zone' in trading_plan:
            message += f"""
                📍 **Entry**: {trading_plan['entry_zone'][0]:.5f} - {trading_plan['entry_zone'][1]:.5f}
                🛑 **Stop**: {trading_plan.get('stop_loss'):.5f}" if isinstance(trading_plan.get('stop_loss'), (int, float)) else "🛑 **Stop**: N/A"
                🎯 **TP1**: {trading_plan.get('take_profit_1'):.5f}" if isinstance(trading_plan.get('take_profit_1'), (int, float)) else "🎯 **TP1**: N/A"
                🎯 **TP2**: {trading_plan.get('take_profit_2'):.5f}" if isinstance(trading_plan.get('take_profit_2'), (int, float)) else "🎯 **TP2**: N/A"
                💰 **Size**: {trading_plan.get('position_size_pct', 0.75):.1f}%
                📊 **R:R**: {trading_plan.get('risk_reward', 'N/A')}

            """
        
        message += f"💡 {trading_plan.get('rationale', 'See full plan for details')}"
        
        send_telegram_message(message)
        print("✅ Trading plan sent to Telegram")
        
    except Exception as e:
        print(f"⚠️  Error sending Telegram message: {e}")


def run_daily_cycle() -> Dict[str, Any]:
    """
    Execute daily trading cycle.
    Run at 8:00 AM EST (before NY session).
    
    Returns:
        Trade log with execution details
    """
    print("=" * 60)
    print("DAILY CYCLE - ACE FOREX TRADER")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Ensure output directories exist
    OUTPUT_DIR.mkdir(exist_ok=True)
    DATE_OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Step 1: Load Playbook
    print("\n[1/7] Loading Playbook...")
    playbook = load_playbook()
    print(f"📚 Playbook version {playbook['metadata']['version']} loaded")
    print(f"   Total bullets: {playbook['metadata']['total_bullets']}")
    
    # Step 2: Gather Market Data
    print("\n[2/7] Gathering Market Data...")
    market_data = gather_market_data()
    
    # Step 3: Generate Charts (for human review)
    print("\n[3/7] Generating Technical Charts...")
    try:
        export_charts()
        print("✅ Charts generated successfully")
    except Exception as e:
        print(f"⚠️  Chart generation failed: {e}")
    
    # Step 4: Run Generator
    print("\n[4/7] Running Generator (Creating Trading Plan)...")
    trading_plan = run_generator(playbook, market_data)
    
    # Add current date if not present
    if "date" not in trading_plan:
        trading_plan["date"] = datetime.now().strftime("%Y-%m-%d")
    
    save_trading_plan(trading_plan)
    
    # Step 5: Send to Telegram
    print("\n[5/7] Sending Plan to Telegram...")
    send_telegram_trading_plan(trading_plan)
    
    # Step 6: Simulate Execution
    print("\n[6/7] Simulating Trade Execution...")
    trade_log = simulate_trade_execution(trading_plan)
    save_trade_log(trade_log)
    
    # Step 7: Save updated playbook (usage timestamps updated)
    print("\n[7/7] Saving Updated Playbook...")
    save_playbook(playbook)
    
    print("\n" + "=" * 60)
    print("DAILY CYCLE COMPLETE")
    if trade_log.get("execution"):
        outcome = trade_log["execution"].get("outcome", "no_trade")
        print(f"Trade Outcome: {outcome.upper()}")
        if "pnl_pips" in trade_log["execution"]:
            pips = trade_log["execution"]["pnl_pips"]
            print(f"P&L: {pips:+d} pips")
    print("=" * 60)
    
    return trade_log


def run_weekly_cycle() -> None:
    """
    Execute weekly reflection and playbook update.
    Run at 5:00 PM EST on Friday.
    """
    print("=" * 60)
    print("WEEKLY CYCLE - ACE FOREX TRADER")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Step 1: Load This Week's Trade Logs
    print("\n[1/4] Loading Weekly Trade Logs...")
    weekly_logs = load_trade_logs_for_week()
    
    if not weekly_logs:
        print("⚠️  No trade logs found for this week. Skipping weekly cycle.")
        return
    
    # Step 2: Run Reflector
    print("\n[2/4] Running Reflector (Analyzing Performance)...")
    current_playbook = load_playbook()
    reflection = run_reflector(weekly_logs, current_playbook)
    save_reflection(reflection)
    
    # Display summary
    summary = reflection.get("summary", {})
    print(f"\n📊 Weekly Performance Summary:")
    print(f"   Total Trades: {summary.get('total_trades', 0)}")
    print(f"   Win Rate: {summary.get('win_rate', 0):.1%}")
    print(f"   Avg R:R: {summary.get('avg_rr', 0):.2f}")
    print(f"   Total Pips: {summary.get('total_pips', 0):+d}")
    
    # Step 3: Run Curator
    print("\n[3/4] Running Curator (Updating Playbook)...")
    updated_playbook = run_curator(reflection, current_playbook)
    save_playbook(updated_playbook)
    
    # Step 4: Send Summary to Telegram
    print("\n[4/4] Sending Weekly Summary to Telegram...")
    send_telegram_weekly_summary(weekly_logs, reflection, updated_playbook)
    
    print("\n" + "=" * 60)
    print("WEEKLY CYCLE COMPLETE")
    print(f"Playbook updated: v{updated_playbook['metadata']['version']}")
    print(f"Total bullets: {updated_playbook['metadata']['total_bullets']}")
    insights_count = len(reflection.get("insights", []))
    print(f"Insights processed: {insights_count}")
    print("=" * 60)


def send_telegram_weekly_summary(
    weekly_logs: list,
    reflection: Dict[str, Any],
    updated_playbook: Dict[str, Any]
) -> None:
    """Send weekly summary to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⏭️  Telegram not configured, skipping notification")
        return
    
    try:
        summary = reflection.get("summary", {})
        
        message = f"""
📊 **Weekly Performance Summary**
Week ending: {reflection.get('week_ending', 'N/A')}

📈 **Results**:
- Trades: {summary.get('total_trades', 0)}
- Win Rate: {summary.get('win_rate', 0):.1%}
- Total Pips: {summary.get('total_pips', 0):+d}

📚 **Playbook Update**:
- Version: {updated_playbook['metadata']['version']}
- Total Bullets: {updated_playbook['metadata']['total_bullets']}
- Insights: {len(reflection.get('insights', []))}

💡 **Key Recommendations**:
"""
        
        for i, rec in enumerate(reflection.get('recommendations', [])[:3], 1):
            message += f"{i}. {rec}\n"
        
        send_telegram_message(message)
        print("✅ Weekly summary sent to Telegram")
        
    except Exception as e:
        print(f"⚠️  Error sending weekly summary: {e}")


def main():
    """Main entry point - determines which cycle to run."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ACE Forex Trading System")
    parser.add_argument(
        "--cycle",
        choices=["daily", "weekly"],
        default="daily",
        help="Which cycle to run (default: daily)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.cycle == "daily":
            run_daily_cycle()
        elif args.cycle == "weekly":
            run_weekly_cycle()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
