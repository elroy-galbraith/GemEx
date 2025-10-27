# GemEx Quick Reference - New Package Structure

## 🚀 Quick Commands

### Daily Trading Cycle
```bash
./scripts/run_daily.sh
# or
python gemex/ace/main.py --cycle daily
```

### Weekly Reflection
```bash
python gemex/ace/main.py --cycle weekly
```

### Launch Web UI
```bash
./scripts/launch_ui.sh
# or
streamlit run gemex/ui/app.py
```

## 📦 Common Imports

### ACE Components
```python
from gemex.ace.components import (
    load_playbook,
    save_playbook,
    run_generator,
    simulate_trade_execution,
    run_reflector,
    run_curator
)
```

### Market Analysis
```python
from gemex.market_planner import (
    get_market_data,
    get_economic_calendar,
    export_charts
)
```

### Configuration & Prompts
```python
from gemex.prompts import PLANNER_SYSTEM_PROMPT, REVIEWER_SYSTEM_PROMPT
from gemex.config import VISUAL_INDICATORS, PSYCHOLOGY_TIPS
```

### Convenience (Package Root)
```python
from gemex import (
    load_playbook,
    save_playbook,
    run_generator,
    simulate_trade_execution
)
```

## 📁 File Locations

| What | Location |
|------|----------|
| ACE Components | `gemex/ace/components.py` |
| Daily Cycle Runner | `gemex/ace/main.py` |
| Web UI | `gemex/ui/app.py` |
| Market Analysis | `gemex/market_planner.py` |
| AI Prompts | `gemex/prompts.py` |
| Configuration | `gemex/config.py` |
| Scripts | `scripts/` |
| Trading Plans | `trading_session/YYYY_MM_DD/` |
| Playbook | `data/playbook.json` |
| Weekly Reflections | `weekly_reflections/` |

## 🔗 Backward Compatibility

Old imports still work! These are symlinks:
- `ace_components.py` → `gemex/ace/components.py`
- `ace_main.py` → `gemex/ace/main.py`
- `app.py` → `gemex/ui/app.py`
- `market_planner.py` → `gemex/market_planner.py`
- `prompts.py` → `gemex/prompts.py`
- `telegram_constants.py` → `gemex/config.py`

## 🎯 Common Tasks

### Load and Modify Playbook
```python
from gemex import load_playbook, save_playbook

# Load
playbook = load_playbook()

# Modify
playbook["patterns"]["support_resistance"]["success_rate"] = 0.75

# Save
save_playbook(playbook)
```

### Run Full Daily Cycle
```python
from gemex.ace.main import ace_daily_cycle

# Run complete daily cycle
ace_daily_cycle()
```

### Generate Trading Plan
```python
from gemex import run_generator
from gemex.market_planner import get_market_data

data = get_market_data()
playbook = load_playbook()
plan = run_generator(playbook, data)
```

### Simulate Trade Execution
```python
from gemex import simulate_trade_execution

execution = simulate_trade_execution(trading_plan, latest_candle, playbook)
```

## 🧪 Testing

```bash
# Test imports
python -c "from gemex.ace import components; print('✅ Works')"

# Run tests
python -m pytest tests/test_ace_components.py -v

# Run all tests
python -m pytest tests/ -v
```

## 📚 Documentation

- Full migration guide: `PYTHON_REORGANIZATION_COMPLETE.md`
- Visual summary: `PYTHON_REORGANIZATION_VISUAL.md`
- Original plan: `PYTHON_ORGANIZATION_PLAN.md`
- Main README: `README.md`
- Scripts guide: `scripts/README.md`

## ⚡ Pro Tips

1. **Use new imports**: Better for long-term maintenance
2. **Symlinks work**: No rush to migrate existing code
3. **Package exports**: Import from `gemex` for convenience
4. **Scripts updated**: Use `./scripts/run_daily.sh`
5. **UI from package**: `streamlit run gemex/ui/app.py`

## 🆘 Troubleshooting

### Import not found?
```bash
cd /Users/elroygalbraith/Documents/Repos/GemEx
python -c "from gemex.ace import components"
```

### Check symlinks
```bash
ls -la *.py | grep '^l'
```

### Verify package structure
```bash
tree gemex/
```

---

**Quick Start**: `./scripts/run_daily.sh` or `./scripts/launch_ui.sh`  
**Need Help?**: See `PYTHON_REORGANIZATION_COMPLETE.md`
