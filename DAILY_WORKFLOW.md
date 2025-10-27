# Daily Trading Workflow - Quick Reference

## Every Trading Day (Mon-Fri)

### ☀️ Morning Routine (8:00-9:30 AM EST)

```bash
# 1. Navigate to project
cd /Users/elroygalbraith/Documents/Repos/GemEx

# 2. Activate environment
source gemx_venv/bin/activate

# 3. Generate today's trading plan
python ace_main.py --cycle daily
```

**Expected output:**
- ✅ Market data gathered
- ✅ Charts generated
- ✅ Trading plan created
- ✅ Telegram message sent (if configured)

---

### 📋 Review Trading Plan

```bash
# Quick view of today's plan
cat trading_session/$(date +%Y_%m_%d)/trading_plan.md

# View full JSON details
cat trading_session/$(date +%Y_%m_%d)/trading_plan.json | jq '.'

# Check charts
open trading_session/$(date +%Y_%m_%d)/EURUSD_1H_*.png
```

**What to look for:**
- [ ] Bias: bullish, bearish, or neutral?
- [ ] Entry zone: specific price levels?
- [ ] Stop loss: clearly defined?
- [ ] Take profit: TP1 and TP2 levels?
- [ ] Risk:Reward: minimum 1:1.5?
- [ ] Confidence: high, medium, or low?
- [ ] Reasoning: makes sense?

---

### 💼 Execute Trade (If bias is NOT neutral)

**In your OANDA practice account:**

1. **Set up limit order:**
   - Price: Midpoint of entry zone
   - Units: Based on 1% risk
   - Example: If entry zone is 1.0850-1.0860, set limit at 1.0855

2. **Add stop loss:**
   - Price: Exactly as system recommends
   - Never move stop loss closer to market

3. **Add take profit:**
   - TP1: First target (usually closer)
   - Optional TP2: Second target (further out)

4. **Record in trading journal:**
   - Copy plan details
   - Note your entry price
   - Note entry time

---

### 📊 During NY Session (9:30 AM - 4:00 PM EST)

**Monitor, don't interfere:**
- Let the trade hit TP or SL
- Avoid emotional exits
- Trust the system's levels

**If neutral bias:**
- No trade today
- Record "No trade - neutral bias" in journal
- Use time for system improvement or learning

---

### 🌙 Evening Routine (5:00 PM EST)

```bash
# Check trade outcome
cat trading_session/$(date +%Y_%m_%d)/trade_log.json | jq '.execution'
```

**Update trading journal:**
- [ ] Record exit price
- [ ] Record exit time
- [ ] Calculate P&L (pips and $)
- [ ] Note what worked/didn't work
- [ ] Identify helpful/harmful playbook bullets

---

## Every Friday Evening

### 📊 Weekly Reflection

```bash
# Run weekly analysis
python ace_main.py --cycle weekly
```

**Expected output:**
- ✅ Week's trades analyzed
- ✅ Performance patterns identified
- ✅ Playbook updated
- ✅ Reflection saved

---

### 📖 Review Weekly Reflection

```bash
# View latest reflection
cat weekly_reflections/$(ls -t weekly_reflections/ | head -1) | jq '.'

# Check playbook updates
cat data/playbook.json | jq '.metadata'

# View playbook version history
ls -lt data/playbook_history/
```

**What to check:**
- [ ] Does reflection match your experience?
- [ ] Are success patterns accurate?
- [ ] Are failure patterns identified?
- [ ] Did playbook version increment?
- [ ] Are new bullets helpful?

---

### ✍️ Complete Weekly Journal

**In TRADING_JOURNAL_TEMPLATE.md:**
- [ ] Fill in weekly summary
- [ ] Calculate win rate
- [ ] Calculate total P&L
- [ ] Note key learnings
- [ ] Plan changes for next week

---

## Monthly Review (End of Month)

```bash
# Count total trades
find trading_session -name "trade_log.json" | wc -l

# View playbook evolution
diff data/playbook_history/playbook_v1.0.json data/playbook.json
```

**Assessment:**
- [ ] Total trades: ___
- [ ] Win rate: ___% (target: >50%)
- [ ] Average R:R: ___ (target: >1:1.5)
- [ ] Playbook improved: Yes/No
- [ ] Ready for automation: Yes/No

---

## Troubleshooting

### "No module named 'pandas'"
```bash
source gemx_venv/bin/activate
pip install -r requirements.txt
```

### "GEMINI_API_KEY not found"
```bash
# Check if .env exists
cat .env | grep GEMINI_API_KEY

# If missing, copy template and edit
cp .env.example .env
nano .env  # Add your API key
```

### "No trading plan generated"
```bash
# Check for errors in the output
python ace_main.py --cycle daily 2>&1 | tee debug.log

# Verify market data
python -c "import yfinance as yf; print(yf.download('EURUSD=X', period='1d'))"
```

### "Trading plan is always neutral"
- This is normal! System is being conservative
- Check intermarket conditions
- Review economic calendar
- System may be waiting for better setup

---

## Quick Commands Reference

```bash
# Activate environment
source gemx_venv/bin/activate

# Daily cycle
python ace_main.py --cycle daily

# Weekly cycle
python ace_main.py --cycle weekly

# View today's plan
cat trading_session/$(date +%Y_%m_%d)/trading_plan.md

# View playbook
cat data/playbook.json | jq '.'

# Check system health
python tests/test_ace_system.py

# Full system verification
./verify_setup.sh
```

---

## Key Metrics to Track

### Daily:
- Entry price vs. system recommendation
- Exit price (TP or SL hit?)
- P&L in pips
- P&L in dollars

### Weekly:
- Number of trades
- Win rate
- Average win size (pips)
- Average loss size (pips)
- Actual risk:reward ratio

### Monthly:
- Total P&L
- Maximum drawdown
- Longest winning streak
- Longest losing streak
- Playbook version changes

---

## Success Indicators

✅ **System is working if:**
- Win rate > 50% over 20+ trades
- Average R:R > 1:1.5
- Playbook evolves with new insights
- Trading plans are specific (not vague)
- You understand why trades win/lose

⚠️ **Warning signs:**
- Win rate < 40% over 20+ trades
- Consecutive losses > 5 trades
- Playbook stops improving
- Plans are vague or inconsistent
- You frequently disagree with system

---

## Contact for Help

If system behavior is unexpected:
1. Check TESTING_GUIDE.md
2. Run `./verify_setup.sh`
3. Review error logs
4. Check API key configuration

---

## Notes

- Trading hours: 9:30 AM - 4:00 PM EST (NY session only)
- Avoid trading during major news events
- Risk only 1% per trade
- Never move stop loss against you
- Trust the process, track results
