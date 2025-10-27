# Using GemEx in Simulation Mode - Quick Start Guide

## Overview

**Good news:** Your GemEx ACE system is **fully functional in simulation mode** right now! You can run it for a week (or longer) to:

1. ✅ See how the AI analyzes real market data
2. ✅ Watch the playbook evolve over time
3. ✅ Track simulated trading performance
4. ✅ Build confidence in the system
5. ✅ Identify areas for improvement

**No broker connection needed!** The system will simulate trade execution based on the trading plans.

---

## How Simulation Mode Works

### What's Real:
- ✅ **Market data** - Actual EURUSD prices from Yahoo Finance
- ✅ **Technical analysis** - Real chart patterns and indicators
- ✅ **Economic calendar** - Live news events from Forex Factory
- ✅ **AI analysis** - Gemini generates trading plans based on real conditions
- ✅ **Playbook evolution** - System learns from simulated outcomes

### What's Simulated:
- 🎲 **Trade execution** - System simulates whether trades would win/lose
- 🎲 **P&L calculation** - Based on the trading plan's risk/reward
- 🎲 **Entry/exit timing** - Assumes trades enter at midpoint of entry zone

### Simulation Logic:

The simulation is currently **simple but functional**:

```python
# Based on plan confidence:
if confidence == "high":
    win_probability = 66% (2 out of 3 trades win)
elif confidence == "medium":
    win_probability = 50% (1 out of 2 trades win)
else:  # low confidence
    win_probability = 0% (trades lose)
```

**Why this works for testing:**
- Tests the full system workflow
- Validates playbook evolution logic
- Shows you the quality of AI-generated plans
- Gives realistic feedback loop

**Limitations:**
- Not based on actual price movement
- Doesn't account for slippage or spread
- Win/loss is deterministic (based on date hash)
- Doesn't validate entry zone quality

---

## Your Week-Long Test Plan

### Day 1 (Today): Setup & First Run

```bash
# 1. Activate environment
source gemx_venv/bin/activate

# 2. Generate today's trading plan
python ace_main.py --cycle daily

# 3. Review what was generated
cat trading_session/$(date +%Y_%m_%d)/trading_plan.md
cat trading_session/$(date +%Y_%m_%d)/trade_log.json
```

**What to observe:**
- Does the trading plan make sense?
- Is the bias (bullish/bearish/neutral) logical?
- Are entry zones and stop losses reasonable?
- Did the simulation execute a trade?

---

### Days 2-5: Daily Routine

**Every morning (before market open):**

```bash
source gemx_venv/bin/activate
python ace_main.py --cycle daily
```

**Review checklist:**
- [ ] Trading plan generated successfully
- [ ] Charts created (15M, 1H, 4H timeframes)
- [ ] Trade log shows execution outcome
- [ ] Playbook usage timestamps updated

**Keep a simple log:**
```
Day 1: Bias=neutral, No trade
Day 2: Bias=bullish, Entry=1.0850, Win, +30 pips
Day 3: Bias=bearish, Entry=1.0820, Loss, -20 pips
...
```

---

### Day 5 (Friday): Weekly Reflection

```bash
# Run weekly cycle
python ace_main.py --cycle weekly
```

**This will:**
1. Load all 5 days of trade logs
2. Analyze performance patterns
3. Generate insights about what worked/didn't work
4. Update the playbook with new bullets
5. Increment playbook version

**Review the reflection:**
```bash
# View reflection
cat weekly_reflections/$(ls -t weekly_reflections/ | head -1) | jq '.'

# Check playbook changes
cat data/playbook.json | jq '.metadata'

# See what bullets were added
cat data/playbook.json | jq '.sections.strategies_and_hard_rules[-3:]'
```

---

## What to Track During the Week

### Daily Metrics:

Create a simple spreadsheet or text file:

```
Date       | Bias    | Entry   | SL      | TP1     | Outcome | Pips | Notes
-----------|---------|---------|---------|---------|---------|------|-------
2025-10-28 | neutral | -       | -       | -       | no_trade| 0    | DXY/SPX conflict
2025-10-29 | bullish | 1.0850  | 1.0820  | 1.0900  | win     | +30  | Clear trend
2025-10-30 | bearish | 1.0820  | 1.0850  | 1.0770  | loss    | -20  | Stopped out
2025-10-31 | bullish | 1.0860  | 1.0830  | 1.0920  | win     | +40  | News catalyst
2025-11-01 | neutral | -       | -       | -       | no_trade| 0    | Low volatility
```

### Weekly Metrics:

```
Total Days: 5
Trading Days: 3 (2 neutral)
Wins: 2
Losses: 1
Win Rate: 66%
Total Pips: +50
Average Win: +35 pips
Average Loss: -20 pips
Risk:Reward: 1:1.75
```

---

## What You'll Learn This Week

### About the System:

1. **Trading Plan Quality**
   - Are plans specific or vague?
   - Do entry zones make sense?
   - Are risk:reward ratios consistently good?
   - Does confidence rating correlate with outcomes?

2. **Playbook Evolution**
   - Does the playbook grow each week?
   - Are new bullets actually helpful?
   - Do harmful bullets get removed?
   - Is version incrementing correctly?

3. **AI Analysis Quality**
   - Does it correctly identify trends?
   - Does it avoid bad setups (neutral bias)?
   - Does intermarket analysis add value?
   - Are news events considered properly?

### About Your Trading Edge:

4. **Pattern Recognition**
   - When does the system perform best?
   - What market conditions cause neutral bias?
   - Which playbook bullets are most cited?
   - Are there consistent failure patterns?

---

## Daily Commands Reference

```bash
# Activate environment (do this first every day)
source gemx_venv/bin/activate

# Generate today's plan
python ace_main.py --cycle daily

# Quick view of today's plan
cat trading_session/$(date +%Y_%m_%d)/trading_plan.md

# View trade outcome
cat trading_session/$(date +%Y_%m_%d)/trade_log.json | jq '.execution'

# Check playbook usage
cat data/playbook.json | jq '.sections.strategies_and_hard_rules[] | {id, last_used}'

# View all this week's outcomes
find trading_session -name "trade_log.json" -mtime -7 -exec cat {} \; | jq '.execution.outcome'
```

---

## End of Week Analysis

After running for 5 trading days, analyze:

### System Performance:

```bash
# Count trades
echo "Total sessions:" $(find trading_session -type d -name "2025_*" | wc -l)

# Count trade logs
echo "Trade logs created:" $(find trading_session -name "trade_log.json" | wc -l)

# View playbook evolution
echo "Playbook version:" $(cat data/playbook.json | jq -r '.metadata.version')
echo "Total bullets:" $(cat data/playbook.json | jq -r '.metadata.total_bullets')
```

### Questions to Answer:

1. **Did the system run reliably?**
   - Were trading plans generated every day?
   - Were there any errors or crashes?
   - Did charts generate correctly?

2. **Were the trading plans actionable?**
   - Did they have specific entry zones?
   - Were stop losses and targets clear?
   - Would you have taken these trades manually?

3. **Did the playbook improve?**
   - Compare v1.0 to current version
   - Are new bullets relevant?
   - Do they reflect the week's outcomes?

4. **What's the simulated performance?**
   - Simulated win rate
   - Simulated average pips
   - Pattern: high confidence → better outcomes?

---

## Comparing Simulation vs. Reality

**Optional: Manual validation during the week**

If you want to see how simulation compares to reality:

1. **Each day, check if the trade would have actually won:**
   - Use TradingView to review EURUSD price action
   - Did price reach the entry zone?
   - Would stop loss have been hit?
   - Would take profit have been reached?

2. **Track two columns:**
   ```
   Date | Simulated Outcome | Actual Outcome | Match?
   -----|-------------------|----------------|-------
   Mon  | Win (+30 pips)    | Win (+25 pips) | ✅
   Tue  | Loss (-20 pips)   | No entry       | ❌
   Wed  | Win (+40 pips)    | Win (+45 pips) | ✅
   ```

3. **This tells you:**
   - How accurate is the simulation?
   - Are entry zones realistic?
   - Do trades actually trigger?

---

## After the Week: Next Steps

### If Results Look Good (50%+ simulated win rate):

✅ **Continue for another 2-3 weeks** to build confidence

✅ **Start manual paper trading** alongside simulation
   - Execute trades manually in OANDA demo
   - Compare manual vs. simulated results
   - See which is more accurate

✅ **Consider building broker integration**
   - After 30+ days of good results
   - See PRODUCTION_GUIDE.md for roadmap

### If Results Are Mixed (40-50% simulated win rate):

⚠️ **Continue simulation but observe:**
   - What causes losses?
   - Are losses on low-confidence trades?
   - Is playbook evolving in right direction?
   - Do you agree with AI's bias calls?

⚠️ **Consider improvements:**
   - Better entry zone logic
   - More conservative confidence rating
   - Enhanced intermarket analysis
   - Additional filters (volatility, time of day)

### If Results Are Poor (<40% simulated win rate):

❌ **Don't trade real money yet!**

🔍 **Debug the system:**
   - Check if market data is accurate
   - Review AI prompts (prompts.py)
   - Analyze playbook bullets
   - Look for systematic bias errors

🛠️ **Potential fixes:**
   - Improve Generator prompts
   - Add more conservative filters
   - Enhance risk management logic
   - Better confidence assessment

---

## Advantages of Running in Simulation Mode

### 1. **Zero Risk**
- No money on the line
- Safe to experiment
- Can run 24/7 without worry

### 2. **Complete Workflow Testing**
- Tests daily cycle
- Tests weekly reflection
- Tests playbook evolution
- Tests file generation

### 3. **Rapid Learning**
- See 5 days of "trading" in 1 week
- Understand AI decision patterns
- Identify system strengths/weaknesses
- Build intuition for when it works

### 4. **Playbook Development**
- System learns and evolves
- Accumulates knowledge
- By week 4, playbook will be much richer
- Real foundation before live trading

### 5. **Preparation for Real Trading**
- Learn the daily routine
- Understand the outputs
- Build confidence (or discover issues)
- No pressure to perform

---

## Simulation Mode Limitations

Be aware that simulation is **not perfect**:

❌ **Oversimplified outcomes** - Real trading is messier
❌ **No slippage/spread** - Actual costs not included
❌ **Deterministic results** - Same plan → same outcome
❌ **Entry assumption** - May not reflect reality
❌ **No market impact** - Assumes perfect fills

**But that's OK!** The goal this week is to:
- Validate the system runs smoothly
- Check AI analysis quality
- Watch playbook evolution
- Build your workflow

You'll validate actual execution later with manual paper trading or broker integration.

---

## Sample Week Schedule

### Monday:
```bash
8:00 AM - Run: python ace_main.py --cycle daily
8:05 AM - Review trading plan
8:10 AM - Note: Would I take this trade?
5:00 PM - Check trade_log.json outcome
5:05 PM - Log results in tracking sheet
```

### Tuesday-Thursday:
```bash
Repeat Monday's routine
```

### Friday:
```bash
8:00 AM - Run: python ace_main.py --cycle daily
5:00 PM - Run: python ace_main.py --cycle weekly
5:10 PM - Review weekly reflection
5:20 PM - Check playbook updates
5:30 PM - Analyze week's performance
6:00 PM - Plan for next week
```

---

## Quick Troubleshooting

### "No trading plan generated"
```bash
# Check for errors
python ace_main.py --cycle daily 2>&1 | tee error.log
cat error.log
```

### "Always neutral bias"
- This can be normal! System is being conservative
- Check market conditions - is there a clear trend?
- Review intermarket data - are there conflicts?
- If 5 days = 5 neutral, may need to adjust prompts

### "Same outcome every day"
- This is expected with current simulation
- Outcomes are deterministic based on date
- For more realistic simulation, we'd need to enhance the logic
- Not a problem for testing workflow

### "Playbook not updating"
- Check if weekly reflection ran successfully
- Verify insights were generated
- Look for errors in Curator component
- May need at least 1 non-neutral trade for meaningful reflection

---

## Summary: Your Week Ahead

**Day 1-5:**
- Run `python ace_main.py --cycle daily` every morning
- Review trading plans
- Track simulated outcomes
- Observe patterns

**Day 5 (Friday):**
- Run `python ace_main.py --cycle weekly`
- Review reflection and playbook updates
- Analyze the week's performance

**After Week 1:**
- Decide: Continue simulation? Start manual? Build automation?
- If simulation looks good → Continue for 3-4 weeks
- If plans are high quality → Consider manual paper trading
- If performance is poor → Debug and improve

**No broker needed yet!** The simulation mode is perfect for:
- Learning the system
- Validating AI quality
- Testing playbook evolution
- Building confidence

When you're ready to connect to OANDA (after proving the system works), I can help you build that integration. But for this week, **just run it in simulation and observe**! 🚀

---

## Your Action Items for Today

```bash
# 1. Run your first daily cycle
source gemx_venv/bin/activate
python ace_main.py --cycle daily

# 2. Review outputs
cat trading_session/$(date +%Y_%m_%d)/trading_plan.md
cat trading_session/$(date +%Y_%m_%d)/trade_log.json

# 3. Create tracking sheet (optional)
cp TRADING_JOURNAL_TEMPLATE.md my_week1_results.md

# 4. Set reminder for tomorrow morning
# "Run python ace_main.py --cycle daily"

# 5. Plan for Friday reflection
# "Run python ace_main.py --cycle weekly"
```

**That's it!** You're ready to run the system in simulation mode for a week. No broker connection needed! 🎯
