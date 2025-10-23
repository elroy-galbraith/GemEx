# ACE (Agentic Context Engineering) Trading System

## Overview

The ACE Trading System is a proof-of-concept forex trading system that uses **Agentic Context Engineering** to create and evolve a comprehensive trading "Playbook" through daily market analysis and weekly reflection cycles. Instead of fine-tuning models or using static prompts, this system maintains an evolving Playbook that accumulates strategies, patterns, and lessons over time.

## Architecture

### Core Components

1. **Playbook** (`data/playbook.json`)
   - Structured collection of trading strategies, patterns, and lessons
   - Each "bullet" has helpful/harmful counts and usage tracking
   - Organized into sections: strategies, code templates, pitfalls

2. **Generator** (`ace_components.py::run_generator`)
   - Creates daily trading plans using playbook + market data
   - Generates entry/exit levels, risk/reward ratios
   - Cites which playbook bullets influenced the decision

3. **Executor** (`ace_components.py::simulate_trade_execution`)
   - Simulates trade execution (paper trading)
   - Tracks outcomes (win/loss, pips, execution quality)
   - Can be upgraded to real broker integration

4. **Reflector** (`ace_components.py::run_reflector`)
   - Weekly analysis of trading performance
   - Identifies success patterns, failure patterns, outdated rules
   - Suggests playbook updates

5. **Curator** (`ace_components.py::run_curator`)
   - Updates playbook based on Reflector insights
   - Adds new bullets, increments counts, removes harmful rules
   - Maintains playbook version history

## Daily Cycle

Run before NY session (8:00 AM EST):

```bash
python ace_main.py --cycle daily
```

**Steps:**
1. Load playbook
2. Gather market data (EURUSD, DXY, SPX500, US10Y, news)
3. Generate technical charts
4. Run Generator → Create trading plan
5. Send plan to Telegram
6. Simulate trade execution
7. Save trade log

**Output:**
- `trading_session/YYYY_MM_DD/trading_plan.json`
- `trading_session/YYYY_MM_DD/trading_plan.md`
- `trading_session/YYYY_MM_DD/trade_log.json`
- Updated playbook with usage timestamps

## Weekly Cycle

Run on Friday EOD (5:00 PM EST):

```bash
python ace_main.py --cycle weekly
```

**Steps:**
1. Load week's trade logs (Monday-Friday)
2. Run Reflector → Analyze performance
3. Run Curator → Update playbook
4. Send summary to Telegram

**Output:**
- `weekly_reflections/YYYY_WNN_reflection.json`
- `data/playbook.json` (updated version)
- `data/playbook_history/playbook_vX.X.json` (backup)

## Data Structures

### Playbook Structure

```json
{
  "metadata": {
    "version": "1.5",
    "last_updated": "2025-01-05T12:00:00Z",
    "total_bullets": 42
  },
  "sections": {
    "strategies_and_hard_rules": [
      {
        "id": "strat-001",
        "content": "Only trade during NY session (9:30 AM - 4:00 PM EST)",
        "helpful_count": 5,
        "harmful_count": 0,
        "created_at": "2025-01-01T00:00:00Z",
        "last_used": "2025-01-05T12:00:00Z"
      }
    ],
    "useful_code_and_templates": [...],
    "troubleshooting_and_pitfalls": [...]
  }
}
```

### Trading Plan Structure

```json
{
  "date": "2025-01-05",
  "bias": "bullish",
  "entry_zone": [1.0485, 1.0495],
  "stop_loss": 1.0465,
  "take_profit_1": 1.0535,
  "take_profit_2": 1.0565,
  "position_size_pct": 0.75,
  "risk_reward": "1:2.5",
  "rationale": "DXY weakness + SPX strength suggests bullish bias",
  "playbook_bullets_used": ["strat-001", "pit-003"],
  "confidence": "high"
}
```

### Trade Log Structure

```json
{
  "plan_id": "2025-01-05",
  "execution": {
    "entry_time": "2025-01-05T13:30:00Z",
    "entry_price": 1.0490,
    "exit_time": "2025-01-05T16:45:00Z",
    "exit_price": 1.0530,
    "pnl_pips": 40,
    "pnl_usd": 300,
    "outcome": "win"
  },
  "feedback": {
    "entry_quality": "good",
    "exit_timing": "early",
    "playbook_bullets_feedback": {
      "strat-001": "helpful"
    }
  }
}
```

## Integration with Existing Code

### What We Keep (Reused)

✅ Chart generation (`export_charts`)
✅ Market data fetching (`get_market_data`, `get_intermarket_analysis`)
✅ News scraping (`get_economic_calendar`)
✅ Technical indicators (`calculate_indicators`)
✅ Telegram integration (`send_telegram_message`)
✅ File organization (`OUTPUT_DIR`, `DATE_OUTPUT_DIR`)

### What We Modified

🔄 Main orchestration flow → Daily/Weekly cycles
🔄 LLM prompts → Generator and Reflector
🔄 Review system → Simplified to execution feedback

### What We Added

➕ Playbook data structure and management
➕ Generator component (ACE-aware trading plan creation)
➕ Executor component (simulated trade execution)
➕ Reflector component (weekly analysis)
➕ Curator component (playbook updates)
➕ New file structure for playbooks and reflections

## Setup

### Prerequisites

- Python 3.12+
- Google Gemini API key (for Generator and Reflector)
- Telegram bot token (optional, for notifications)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your_gemini_api_key"
export TELEGRAM_BOT_TOKEN="your_bot_token"  # Optional
export TELEGRAM_CHAT_ID="your_chat_id"      # Optional
```

### First Run

On first run, the system will automatically:
1. Create `data/` directory
2. Initialize playbook with basic trading rules
3. Create directory structure for sessions and reflections

## Usage

### Run Daily Analysis

```bash
python ace_main.py --cycle daily
```

This generates a trading plan and simulates execution.

### Run Weekly Reflection

```bash
python ace_main.py --cycle weekly
```

This analyzes the week's performance and updates the playbook.

### Test ACE Components

```bash
python tests/test_ace_components.py
```

This validates core ACE functionality without requiring API keys.

## File Structure

```
GemEx/
├── ace_components.py           # Core ACE components
├── ace_main.py                 # Daily/weekly orchestration
├── market_planner.py           # Existing market data functions
├── prompts.py                  # Original prompts (kept for compatibility)
│
├── data/
│   ├── playbook.json           # Current playbook state
│   └── playbook_history/       # Versioned backups
│
├── trading_session/
│   └── YYYY_MM_DD/             # Daily session folders
│       ├── trading_plan.json
│       ├── trading_plan.md
│       ├── trade_log.json
│       └── charts/             # Technical charts
│
├── weekly_reflections/
│   └── YYYY_WNN_reflection.json
│
└── tests/
    └── test_ace_components.py  # ACE component tests
```

## GitHub Actions Integration

The system can be scheduled via GitHub Actions:

```yaml
# Run daily analysis
- cron: '0 13 * * 1-5'  # 8 AM EST, Mon-Fri

# Run weekly reflection
- cron: '0 22 * * 5'    # 5 PM EST, Friday
```

See `.github/workflows/` for workflow configurations.

## Safety Features

1. **Paper Trading Only**: Executor simulates trades (no real orders)
2. **Playbook Versioning**: Every update creates a backup
3. **Harmful Bullet Pruning**: Automatically removes rules that consistently fail
4. **Confidence Scoring**: Plans rated high/medium/low confidence
5. **No Trade Option**: Generator can decline to trade if no good setup

## Future Enhancements

### Phase 2: Feedback Quality
- Add Sharpe ratio, win rate, avg R:R calculations
- Implement "process metrics" beyond P&L
- Enhanced Reflector analysis

### Phase 3: Robustness
- Semantic deduplication using embeddings
- Market regime detection (trend vs. range)
- Rollback capability for playbook versions

### Phase 4: Live Trading
- OANDA API integration
- Real-time price streaming
- Actual order placement in paper account

## Monitoring & Debugging

### Check Playbook Health

```bash
cat data/playbook.json | jq '.metadata'
```

### Review Recent Plans

```bash
ls -lt trading_session/ | head -5
cat trading_session/YYYY_MM_DD/trading_plan.md
```

### Analyze Weekly Performance

```bash
cat weekly_reflections/YYYY_WNN_reflection.json | jq '.summary'
```

### View Logs

All operations print to stdout. Redirect to file if needed:

```bash
python ace_main.py --cycle daily 2>&1 | tee logs/daily_$(date +%Y%m%d).log
```

## Troubleshooting

### "Google Generative AI not available"

Install the package:
```bash
pip install google-generativeai
```

### "GEMINI_API_KEY not found"

Set the environment variable:
```bash
export GEMINI_API_KEY="your_key_here"
```

### "No trade logs found for this week"

Run daily cycle at least once before running weekly cycle.

### Charts not generating

Check that matplotlib and mplfinance are installed:
```bash
pip install matplotlib mplfinance
```

## License

Apache License 2.0 - See LICENSE file for details.

**EDUCATIONAL PURPOSE ONLY**: This software is for educational and research purposes only. Not financial advice.
