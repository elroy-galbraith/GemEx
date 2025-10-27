#!/usr/bin/env python3
"""
ACE Trading System - Standalone Demo

This demo shows how the ACE system works without requiring external APIs or data sources.
It uses mock market data to demonstrate the daily and weekly cycles.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from gemex.ace.components import (
    initialize_playbook,
    save_playbook,
    load_playbook,
    simulate_trade_execution,
    save_trade_log,
    run_curator,
    generate_bullet_id,
    PLAYBOOK_PATH,
    TRADING_SESSIONS_DIR,
    WEEKLY_REFLECTIONS_DIR
)


def create_mock_market_data(date: str = None) -> dict:
    """Create mock market data for testing."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    return {
        "timestamp": f"{date}T12:00:00Z",
        "eurusd": {
            "current_price": 1.0850,
            "trend": "bullish",
            "support": 1.0820,
            "resistance": 1.0900
        },
        "intermarket": {
            "dxy": {"trend": "bearish", "level": 103.50},
            "spx500": {"trend": "bullish", "level": 5100},
            "us10y": {"level": 4.25}
        },
        "news_events": [
            {"time": "14:30", "impact": "high", "event": "FOMC Minutes"},
            {"time": "15:00", "impact": "medium", "event": "ISM Services"}
        ]
    }


def create_mock_trading_plan(playbook: dict, market_data: dict, date: str = None) -> dict:
    """Create a mock trading plan (without calling actual LLM)."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Use playbook bullets
    bullets_used = []
    if playbook["sections"]["strategies_and_hard_rules"]:
        bullets_used.append(playbook["sections"]["strategies_and_hard_rules"][0]["id"])
    
    # Generate plan based on mock data
    current_price = market_data["eurusd"]["current_price"]
    
    return {
        "date": date,
        "bias": "bullish",
        "entry_zone": [current_price - 0.0010, current_price],
        "stop_loss": current_price - 0.0035,
        "take_profit_1": current_price + 0.0050,
        "take_profit_2": current_price + 0.0080,
        "position_size_pct": 0.75,
        "risk_reward": "1:2.3",
        "rationale": f"DXY weakness ({market_data['intermarket']['dxy']['trend']}) + SPX strength supports bullish bias",
        "playbook_bullets_used": bullets_used,
        "confidence": "medium"
    }


def demo_daily_cycle():
    """Demonstrate daily trading cycle."""
    print("=" * 70)
    print("ACE TRADING SYSTEM - DAILY CYCLE DEMO")
    print("=" * 70)
    
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Step 1: Load or create playbook
    print("\n[1/5] Loading Playbook...")
    if PLAYBOOK_PATH.exists():
        playbook = load_playbook()
        print(f"   📚 Loaded existing playbook v{playbook['metadata']['version']}")
    else:
        playbook = initialize_playbook()
        save_playbook(playbook)
        print(f"   📚 Initialized new playbook v{playbook['metadata']['version']}")
    
    print(f"   Total bullets: {playbook['metadata']['total_bullets']}")
    print(f"   Sections: {len(playbook['sections'])}")
    
    # Step 2: Create mock market data
    print("\n[2/5] Gathering Market Data...")
    market_data = create_mock_market_data(date)
    print(f"   💹 EURUSD: {market_data['eurusd']['current_price']}")
    print(f"   📊 DXY: {market_data['intermarket']['dxy']['level']} ({market_data['intermarket']['dxy']['trend']})")
    print(f"   📰 News events: {len(market_data['news_events'])}")
    
    # Step 3: Generate trading plan (mock)
    print("\n[3/5] Generating Trading Plan...")
    trading_plan = create_mock_trading_plan(playbook, market_data, date)
    print(f"   🎯 Bias: {trading_plan['bias'].upper()}")
    print(f"   📍 Entry: {trading_plan['entry_zone'][0]:.5f} - {trading_plan['entry_zone'][1]:.5f}")
    print(f"   🛑 Stop: {trading_plan['stop_loss']:.5f}")
    print(f"   🎯 TP1: {trading_plan['take_profit_1']:.5f}")
    print(f"   💡 Confidence: {trading_plan['confidence'].upper()}")
    
    # Save plan
    date_dir = TRADING_SESSIONS_DIR / datetime.now().strftime("%Y_%m_%d")
    date_dir.mkdir(parents=True, exist_ok=True)
    plan_path = date_dir / "trading_plan.json"
    with open(plan_path, 'w') as f:
        json.dump(trading_plan, f, indent=2)
    print(f"   ✅ Plan saved to {plan_path}")
    
    # Step 4: Simulate execution
    print("\n[4/5] Simulating Trade Execution...")
    trade_log = simulate_trade_execution(trading_plan)
    
    if trade_log["execution"] and "outcome" in trade_log["execution"]:
        outcome = trade_log["execution"]["outcome"]
        pips = trade_log["execution"].get("pnl_pips", 0)
        print(f"   📊 Outcome: {outcome.upper()}")
        print(f"   💰 P&L: {pips:+d} pips")
        
        # Save log
        save_trade_log(trade_log)
    else:
        print(f"   ⏸️  Status: {trade_log['execution']['status']}")
    
    # Step 5: Update playbook
    print("\n[5/5] Updating Playbook...")
    save_playbook(playbook)
    print(f"   ✅ Playbook saved with updated usage timestamps")
    
    print("\n" + "=" * 70)
    print("DAILY CYCLE COMPLETE")
    print("=" * 70)


def demo_weekly_cycle():
    """Demonstrate weekly reflection cycle."""
    print("\n" + "=" * 70)
    print("ACE TRADING SYSTEM - WEEKLY CYCLE DEMO")
    print("=" * 70)
    
    # Step 1: Create mock weekly logs
    print("\n[1/4] Creating Mock Weekly Logs...")
    weekly_logs = []
    
    for i in range(5):  # 5 trading days
        date = (datetime.now() - timedelta(days=4-i)).strftime("%Y-%m-%d")
        
        # Create mock plan and execution
        plan = {
            "date": date,
            "bias": "bullish" if i % 2 == 0 else "bearish",
            "confidence": ["high", "medium", "low"][i % 3]
        }
        
        trade_log = {
            "plan_id": date,
            "execution": {
                "outcome": "win" if i % 3 != 0 else "loss",
                "pnl_pips": 40 if i % 3 != 0 else -20,
                "entry_price": 1.0850,
                "exit_price": 1.0890 if i % 3 != 0 else 1.0830
            },
            "feedback": {
                "entry_quality": "good",
                "exit_timing": "good" if i % 3 != 0 else "stopped_out"
            }
        }
        weekly_logs.append(trade_log)
    
    print(f"   📊 Created {len(weekly_logs)} mock trade logs")
    
    # Step 2: Calculate summary
    print("\n[2/4] Analyzing Performance...")
    wins = sum(1 for log in weekly_logs if log["execution"]["outcome"] == "win")
    total_pips = sum(log["execution"]["pnl_pips"] for log in weekly_logs)
    win_rate = wins / len(weekly_logs)
    
    print(f"   📈 Total Trades: {len(weekly_logs)}")
    print(f"   ✅ Wins: {wins} ({win_rate:.1%})")
    print(f"   💰 Total Pips: {total_pips:+d}")
    
    # Step 3: Create mock reflection
    print("\n[3/4] Generating Insights...")
    reflection = {
        "week_ending": datetime.now().strftime("%Y-%m-%d"),
        "summary": {
            "total_trades": len(weekly_logs),
            "win_rate": win_rate,
            "total_pips": total_pips,
            "avg_rr": 1.8
        },
        "insights": [
            {
                "type": "success_pattern",
                "observation": "Bullish trades had higher win rate this week",
                "suggested_action": "add_bullet",
                "section": "strategies_and_hard_rules",
                "content": "When DXY < 104, bullish setups have higher probability",
                "priority": "high"
            },
            {
                "type": "execution_issue",
                "observation": "Early exits left pips on table",
                "suggested_action": "add_bullet",
                "section": "troubleshooting_and_pitfalls",
                "content": "Let winners run - don't exit at first TP if momentum strong",
                "priority": "medium"
            }
        ],
        "recommendations": [
            "Focus on bullish setups in current market regime",
            "Improve exit timing - scale out instead of full exit",
            "Review risk management on losing trades"
        ],
        "market_regime_notes": "Trending week with clear directional bias"
    }
    
    print(f"   💡 Generated {len(reflection['insights'])} insights")
    
    # Save reflection
    week_str = datetime.now().strftime("%Y_W%U")
    reflection_path = WEEKLY_REFLECTIONS_DIR / f"{week_str}_reflection.json"
    with open(reflection_path, 'w') as f:
        json.dump(reflection, f, indent=2)
    print(f"   ✅ Reflection saved to {reflection_path}")
    
    # Step 4: Update playbook with curator
    print("\n[4/4] Updating Playbook with Curator...")
    playbook = load_playbook()
    old_version = playbook["metadata"]["version"]
    old_bullets = playbook["metadata"]["total_bullets"]
    
    updated_playbook = run_curator(reflection, playbook)
    save_playbook(updated_playbook)
    
    new_version = updated_playbook["metadata"]["version"]
    new_bullets = updated_playbook["metadata"]["total_bullets"]
    
    print(f"   📚 Version: {old_version} → {new_version}")
    print(f"   📝 Bullets: {old_bullets} → {new_bullets} ({new_bullets - old_bullets:+d})")
    
    print("\n" + "=" * 70)
    print("WEEKLY CYCLE COMPLETE")
    print("=" * 70)


def show_playbook_summary():
    """Display current playbook summary."""
    print("\n" + "=" * 70)
    print("CURRENT PLAYBOOK SUMMARY")
    print("=" * 70)
    
    if not PLAYBOOK_PATH.exists():
        print("\n⚠️  No playbook found. Run demo_daily_cycle() first.")
        return
    
    playbook = load_playbook()
    
    print(f"\n📚 Version: {playbook['metadata']['version']}")
    print(f"📅 Last Updated: {playbook['metadata']['last_updated']}")
    print(f"📝 Total Bullets: {playbook['metadata']['total_bullets']}")
    
    for section_name, bullets in playbook["sections"].items():
        print(f"\n{'=' * 50}")
        print(f"Section: {section_name.replace('_', ' ').title()}")
        print(f"{'=' * 50}")
        
        for bullet in bullets[:5]:  # Show first 5 bullets
            print(f"\n• ID: {bullet['id']}")
            print(f"  Content: {bullet['content']}")
            print(f"  Helpful: {bullet['helpful_count']} | Harmful: {bullet['harmful_count']}")
            if bullet.get('last_used'):
                print(f"  Last Used: {bullet['last_used'][:10]}")
        
        if len(bullets) > 5:
            print(f"\n  ... and {len(bullets) - 5} more bullets")


def main():
    """Main demo function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ACE Trading System Demo")
    parser.add_argument(
        "--demo",
        choices=["daily", "weekly", "both", "summary"],
        default="both",
        help="Which demo to run"
    )
    
    args = parser.parse_args()
    
    try:
        if args.demo in ["daily", "both"]:
            demo_daily_cycle()
        
        if args.demo in ["weekly", "both"]:
            demo_weekly_cycle()
        
        if args.demo in ["summary", "both"]:
            show_playbook_summary()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
