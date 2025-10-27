# GemEx ACE System - Testing Guide

This guide provides comprehensive testing strategies to verify the ACE trading system is working correctly.

## Quick Start (Fastest Way)

```bash
# Run automated verification script (recommended)
./scripts/verify_setup.sh
```

This script will:
- ✅ Check virtual environment and dependencies
- ✅ Verify Python version
- ✅ Run comprehensive tests
- ✅ Validate directory structure
- ✅ Check environment variables

## Manual Quick Start

```bash
# 1. Activate virtual environment
source gemx_venv/bin/activate

# 2. Ensure .env file is configured
cp .env.example .env  # First time only
# Edit .env and add your GEMINI_API_KEY

# 3. Run comprehensive test suite
python tests/test_ace_system.py
```

**Note:** The virtual environment must be activated for all tests to pass. The system uses `python-dotenv` to load environment variables from `.env` file automatically.

## Testing Levels

### Level 1: Environment Validation (30 seconds)

**Purpose:** Verify Python environment and dependencies are properly installed.

```bash
python tests/test_environment.py
```

**Expected Output:**
- ✅ Python 3.12+ detected
- ✅ Core packages available (pandas, numpy, requests)
- ✅ Optional packages available (yfinance, google.generativeai)

**If Tests Fail:**
- Ensure virtual environment is activated
- Run: `pip install -r requirements.txt`

---

### Level 2: Unit Tests (2-3 minutes)

**Purpose:** Test individual ACE components without requiring API keys.

```bash
# Test ACE components
python tests/test_ace_components.py

# Test integration logic
python tests/test_integration.py
```

**What's Tested:**
- ✅ Playbook initialization and structure
- ✅ Bullet ID generation
- ✅ Trade execution simulation (bullish, bearish, neutral)
- ✅ Curator operations (add, increment, prune bullets)
- ✅ Date filtering logic
- ✅ High-impact event detection

**Expected Output:**
```
✅ test_initialize_playbook passed
✅ test_bullet_id_generation passed
✅ test_simulate_trade_execution passed
✅ test_curator_add_bullet passed
...
```

---

### Level 3: Comprehensive System Test (3-5 minutes)

**Purpose:** End-to-end validation of all ACE components.

```bash
python tests/test_ace_system.py
```

**What's Tested:**
1. **Environment Setup**
   - Python version check
   - Dependency availability
   - API key validation

2. **Playbook Initialization**
   - Data structure validation
   - Section completeness
   - Metadata integrity

3. **Trade Simulation**
   - Bullish plan execution
   - Neutral plan handling
   - Trade log structure

4. **Curator Operations**
   - Adding new bullets
   - Version incrementing
   - Playbook updates

5. **File Persistence**
   - Save/load operations
   - Data integrity
   - Directory creation

6. **Directory Structure**
   - All required directories exist
   - Proper permissions

**Expected Output:**
```
╔════════════════════════════════════════════════════════════╗
║       ACE TRADING SYSTEM - COMPREHENSIVE TEST SUITE        ║
╚════════════════════════════════════════════════════════════╝

============================================================
TEST 1: Environment Setup
============================================================
✅ Python version: 3.13
✅ Import pandas: Available
✅ Import numpy: Available
...

============================================================
TEST SUMMARY
============================================================
Total Tests: 25
✅ Passed: 25
❌ Failed: 0
⚠️  Warnings: 0
============================================================

✅ All tests passed! The ACE system is working correctly.
```

---

### Level 4: Daily Cycle Test (5-10 minutes)

**Purpose:** Test full daily trading cycle with real market data.

**Prerequisites:**
- GEMINI_API_KEY environment variable set
- Internet connection for market data

```bash
# Run daily cycle
python ace_main.py --cycle daily
```

**What Happens:**
1. 📊 Gathers market data (EURUSD, DXY, SPX500, US10Y)
2. 📈 Generates technical charts
3. 🤖 Calls Gemini API to create trading plan
4. 💼 Simulates trade execution
5. 💾 Saves outputs to `trading_session/YYYY_MM_DD/`

**Files to Verify:**
```bash
# Check if these files exist
ls -la trading_session/$(date +%Y_%m_%d)/

# Expected files:
# - trading_plan.json         (AI-generated plan)
# - trading_plan.md           (Human-readable plan)
# - trade_log.json           (Execution results)
# - viper_packet.json        (Market data)
# - EURUSD_*.png             (Charts)
# - intermarket_charts/      (Intermarket analysis)
```

**Validation Checklist:**
- [ ] `trading_plan.json` contains: date, bias, entry_zone, stop_loss, take_profit
- [ ] `trade_log.json` contains: execution outcome, pnl_pips, feedback
- [ ] Charts are generated (4 timeframes for EURUSD)
- [ ] Playbook usage timestamps updated in `data/playbook.json`

**Manual Verification:**
```bash
# Read the trading plan
cat trading_session/$(date +%Y_%m_%d)/trading_plan.md

# Check playbook was updated
cat data/playbook.json | grep last_used | head -5

# Verify trade log
cat trading_session/$(date +%Y_%m_%d)/trade_log.json | jq '.execution.outcome'
```

---

### Level 5: Weekly Cycle Test (3-5 minutes)

**Purpose:** Test weekly reflection and playbook evolution.

**Prerequisites:**
- At least one daily cycle run completed
- GEMINI_API_KEY environment variable set

```bash
# Run weekly cycle
python ace_main.py --cycle weekly
```

**What Happens:**
1. 📚 Loads all trade logs from current week
2. 🧠 Analyzes performance patterns
3. ✍️ Generates reflection insights
4. 📖 Updates playbook with new lessons
5. 🗂️ Backs up old playbook version

**Files to Verify:**
```bash
# Check reflection file
ls -la weekly_reflections/

# Check playbook was updated
ls -la data/playbook_history/

# Expected files:
# - weekly_reflections/YYYY_WNN_reflection.json
# - data/playbook.json (updated version)
# - data/playbook_history/playbook_v*.json (backup)
```

**Validation Checklist:**
- [ ] Reflection file created with success/failure patterns
- [ ] Playbook version incremented
- [ ] New bullets added based on insights
- [ ] Helpful/harmful counts updated
- [ ] Backup created in playbook_history

**Manual Verification:**
```bash
# View reflection
cat weekly_reflections/$(ls -t weekly_reflections/ | head -1)

# Check playbook version
cat data/playbook.json | jq '.metadata.version'

# Count playbook bullets
cat data/playbook.json | jq '.metadata.total_bullets'

# View recent playbook changes
diff data/playbook_history/playbook_v1.0.json data/playbook.json
```

---

## Common Testing Scenarios

### Scenario 1: Clean Install Test

**Goal:** Verify system works on fresh installation.

```bash
# 1. Clone repository
git clone https://github.com/elroy-galbraith/GemEx.git
cd GemEx

# 2. Setup environment
python -m venv gemx_venv
source gemx_venv/bin/activate
pip install -r requirements.txt

# 3. Run comprehensive test
python tests/test_ace_system.py

# 4. Run daily cycle
export GEMINI_API_KEY="your_key"
python ace_main.py --cycle daily
```

---

### Scenario 2: Playbook Evolution Test

**Goal:** Verify playbook learns over time.

```bash
# Day 1: Run and record initial playbook
python ace_main.py --cycle daily
cp data/playbook.json playbook_day1.json

# Day 2-5: Run daily cycles
python ace_main.py --cycle daily  # Repeat for 4 more days

# End of week: Run reflection
python ace_main.py --cycle weekly

# Compare playbooks
diff playbook_day1.json data/playbook.json
```

**Expected Changes:**
- Version number increased
- last_used timestamps updated
- helpful_count incremented for successful strategies
- New bullets added based on weekly insights

---

### Scenario 3: API Failure Graceful Degradation

**Goal:** Verify system handles API failures gracefully.

```bash
# Unset API key
unset GEMINI_API_KEY

# Run tests that don't require API
python tests/test_ace_components.py  # Should pass
python tests/test_ace_system.py      # Should show warnings but not crash

# Try daily cycle (should fail gracefully)
python ace_main.py --cycle daily     # Should show clear error message
```

**Expected Behavior:**
- Clear error messages (not crashes)
- Unit tests still pass
- System indicates what's missing

---

### Scenario 4: Data Validation Test

**Goal:** Verify generated data has correct structure.

```bash
# Run daily cycle
python ace_main.py --cycle daily

# Validate JSON structure
python -c "
import json
from pathlib import Path
from datetime import datetime

# Find today's directory
today = datetime.now().strftime('%Y_%m_%d')
session_dir = Path(f'trading_session/{today}')

# Load and validate files
plan = json.loads((session_dir / 'trading_plan.json').read_text())
log = json.loads((session_dir / 'trade_log.json').read_text())

# Validation checks
assert 'date' in plan, 'Missing date in plan'
assert 'bias' in plan, 'Missing bias in plan'
assert 'execution' in log, 'Missing execution in log'
assert 'feedback' in log, 'Missing feedback in log'

print('✅ All data structures valid')
"
```

---

## Continuous Integration Testing

For automated testing in CI/CD:

```bash
# Run all non-API tests
python tests/test_ace_components.py
python tests/test_integration.py
python tests/test_ace_system.py  # Skips API-dependent tests

# Set API key in GitHub Secrets for full tests
# GEMINI_API_KEY
```

---

## Troubleshooting

### Test Failures

**"Import pandas: Not available"**
```bash
pip install pandas numpy scipy
```

**"GEMINI_API_KEY: Not set"**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**"Playbook save: File not created"**
```bash
mkdir -p data
chmod 755 data
```

**"Charts not generated"**
- Check internet connection (market data fetch)
- Verify matplotlib is installed: `pip install matplotlib`

### Performance Validation

**Is the Generator creating good plans?**
```bash
# Review multiple trading plans
for dir in trading_session/*/; do
    echo "=== $(basename $dir) ==="
    cat "$dir/trading_plan.md" | grep -A5 "BIAS:"
done
```

**Is the Executor making realistic decisions?**
```bash
# Check win rate over time
python -c "
import json
from pathlib import Path

logs = list(Path('trading_session').rglob('trade_log.json'))
wins = sum(1 for log in logs if json.loads(log.read_text())['execution'].get('outcome') == 'win')
total = len([log for log in logs if json.loads(log.read_text())['execution'].get('outcome') != 'no_trade'])

print(f'Win Rate: {wins}/{total} = {wins/total*100:.1f}%' if total > 0 else 'No trades yet')
"
```

**Is the Playbook evolving?**
```bash
# View playbook version history
ls -lt data/playbook_history/

# Count bullets over time
for file in data/playbook_history/*.json; do
    echo "$(basename $file): $(cat $file | jq '.metadata.total_bullets') bullets"
done
```

---

## Benchmarks

**Expected Performance:**
- Unit tests: < 5 seconds
- Comprehensive test: < 1 minute
- Daily cycle: 1-2 minutes
- Weekly cycle: 30-60 seconds

**Resource Usage:**
- Memory: ~200MB (data processing)
- Disk: ~5MB per trading day
- API calls: 2 per daily cycle, 1 per weekly cycle

---

## Success Criteria

✅ **System is working correctly if:**

1. All unit tests pass
2. Comprehensive test suite shows 0 failures
3. Daily cycle generates valid trading plans
4. Trade logs capture execution details
5. Weekly cycle creates reflections
6. Playbook version increments over time
7. Charts are generated successfully
8. Telegram messages sent (if configured)

❌ **System needs attention if:**

1. Unit tests fail
2. JSON files have invalid structure
3. Playbook version doesn't increment
4. No charts generated
5. API errors not handled gracefully
6. Files not saved to correct locations

---

## Next Steps

After confirming the system works:

1. **Production Deployment:**
   - Set up GitHub Actions for daily automation
   - Configure Telegram notifications
   - Monitor playbook evolution weekly

2. **Performance Tracking:**
   - Track win rate over 30+ days
   - Analyze playbook bullet effectiveness
   - Review reflection quality

3. **System Enhancements:**
   - Integrate with live broker (replace simulation)
   - Add more currency pairs
   - Enhance chart analysis

---

## Support

If tests fail or system behavior is unexpected:

1. Check this testing guide
2. Review error messages carefully
3. Verify environment setup (Python version, dependencies)
4. Check API key configuration
5. Examine generated files for structure issues

For additional help, see:
- `ACE_README.md` - System architecture
- `README.md` - Original project documentation
- `tests/test_*.py` - Test implementation details
