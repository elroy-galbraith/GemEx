# GemEx UI Quick Reference

## 🚀 Launch Commands

```bash
# Quick launch (recommended)
./scripts/launch_ui.sh

# Manual launch
streamlit run app.py

# Custom port
streamlit run app.py --server.port 8080
```

## 📱 Navigation

### Page Structure

```
┌─────────────────────────────────────────────────────┐
│  🎯 GemEx Control Panel (Sidebar)                   │
│  ├─ 📊 Dashboard                                    │
│  ├─ 🌅 Daily Cycle                                  │
│  ├─ 🔄 Weekly Reflection                            │
│  ├─ 📚 Playbook                                     │
│  └─ 📈 Charts & Data                                │
│                                                      │
│  📊 Quick Stats                                     │
│  ├─ Playbook Version: 1.0                          │
│  ├─ Total Bullets: 15                              │
│  └─ Last Session: 2025-10-27                       │
│                                                      │
│  ⚙️ System Status                                   │
│  ├─ ✓ Gemini API Connected                         │
│  └─ ⚠ Telegram Not Configured                      │
└─────────────────────────────────────────────────────┘
```

## 📊 Dashboard Page

**What You See:**
- System status (Active/Inactive)
- Current playbook statistics
- Recent sessions count
- Latest trading plan summary
- Recent performance table
- Win/loss metrics

**What You Can Do:**
- Quick overview of system health
- View latest trading bias
- Check recent P&L
- Access latest charts

## 🌅 Daily Cycle Page

**Purpose:** Run daily trading analysis

**Workflow:**
1. Click "▶️ Run Daily Cycle" button
2. Wait 1-2 minutes for completion
3. Review generated trading plan
4. View charts and execution log

**Generated Files:**
- `trading_plan.json` - Structured plan
- `trade_log.json` - Execution results
- `*.png` - Chart images

## 🔄 Weekly Reflection Page

**Purpose:** Analyze weekly performance and update playbook

**Workflow:**
1. Click "▶️ Run Weekly Reflection" button
2. Wait 2-3 minutes for analysis
3. Review insights and recommendations
4. Check updated playbook

**Best Time:** Friday 5:00 PM EST

## 📚 Playbook Page

**What You See:**
- Playbook version and metadata
- Strategies and hard rules
- Code templates
- Troubleshooting tips
- Helpful/harmful counts

**What You Can Do:**
- Browse all trading strategies
- See which rules are most effective
- Track strategy usage
- View raw JSON

## 📈 Charts & Data Page

**Available Charts:**
- EURUSD 15M (day trading)
- EURUSD 1H (intraday)
- EURUSD 4H (swing)
- EURUSD Daily (trend)

**Available Data:**
- Viper Packet (market snapshot)
- Trading Plan (AI strategy)
- Trade Log (execution details)
- Review Scores (quality metrics)

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+R` | Refresh page |
| `Ctrl+Shift+R` | Hard refresh |
| `F5` | Reload data |
| `Ctrl+C` | Stop server (in terminal) |

## 🎨 Visual Indicators

### Status Colors
- 🟢 Green = Go/Active/Success
- 🟡 Yellow = Wait/Warning
- 🔴 Red = Stop/Error/Failed
- ⚪ Gray = Neutral/Inactive

### Emojis Legend
- ✅ Success/Completed
- ⚠️ Warning/Attention needed
- ❌ Error/Failed
- 📊 Data/Analytics
- 📈 Bullish/Up
- 📉 Bearish/Down
- ➡️ Neutral/Sideways
- 🎯 Decision/Action
- 💡 Insight/Tip

## 🔧 Common Tasks

### View Today's Trading Plan
1. Go to **Dashboard**
2. Scroll to "Latest Trading Plan"
3. Click "View Rationale" to expand

### Run Daily Analysis
1. Go to **Daily Cycle**
2. Click "▶️ Run Daily Cycle"
3. Wait for completion
4. Review results

### Check Playbook Updates
1. Go to **Playbook**
2. Look at version number
3. Expand bullets to see details
4. Check helpful/harmful counts

### Browse Historical Charts
1. Go to **Charts & Data**
2. Select date from dropdown
3. Click timeframe tabs
4. View chart images

### Review Weekly Performance
1. Go to **Weekly Reflection**
2. View "Latest Reflection" section
3. Read insights and recommendations
4. Check summary statistics

## 📋 File Locations

```
trading_session/
├── YYYY_MM_DD/              # Daily sessions
│   ├── trading_plan.json   # Trading plan
│   ├── trading_plan.md     # Human-readable plan
│   ├── trade_log.json      # Execution log
│   ├── viper_packet.json   # Market data
│   ├── review_scores.json  # Quality scores
│   └── *.png               # Chart images
│
weekly_reflections/
└── YYYY_WNN_reflection.json # Weekly analysis

data/
├── playbook.json            # Current playbook
└── playbook_history/        # Version backups
    └── playbook_vX.X.json
```

## 🐛 Troubleshooting

### UI Won't Start
**Solution:** `pip install streamlit`

### No Data Showing
**Solution:** Run Daily Cycle at least once

### API Key Warning
**Solution:** `export GEMINI_API_KEY="your_key"`

### Timeout Error
**Solution:** Check internet connection, wait and retry

### Charts Not Loading
**Solution:** Re-run Daily Cycle to regenerate

## 💡 Best Practices

### Daily Routine
1. ✅ Launch UI in morning (before 8 AM EST)
2. ✅ Run Daily Cycle
3. ✅ Review trading plan
4. ✅ Check charts for confirmation
5. ✅ Monitor execution throughout day

### Weekly Routine
1. ✅ Run Weekly Reflection on Friday
2. ✅ Review insights carefully
3. ✅ Note playbook changes
4. ✅ Plan adjustments for next week
5. ✅ Archive old sessions if needed

### Data Management
1. ✅ Keep 30 days of session history
2. ✅ Archive older sessions monthly
3. ✅ Backup playbook before major changes
4. ✅ Review version history periodically
5. ✅ Monitor disk space (charts use space)

## 📞 Support

### Documentation
- `README.md` - Main documentation
- `ACE_README.md` - ACE system details
- `UI_GUIDE.md` - Full UI documentation
- `PRODUCTION_GUIDE.md` - Deployment guide

### Streamlit Help
- Docs: https://docs.streamlit.io/
- Forum: https://discuss.streamlit.io/

## ⚡ Performance Tips

### Faster Loading
- UI caches loaded data automatically
- Only 5 recent sessions loaded by default
- Charts loaded on-demand

### Memory Efficiency
- Large files streamed, not loaded fully
- JSON parsed only when viewed
- Browser caching helps repeated access

## 🔒 Security Notes

### Default Configuration
- ✅ Local access only (localhost)
- ✅ No external connections
- ✅ Safe for personal use

### If Enabling Remote Access
- ⚠️ Use firewall protection
- ⚠️ Consider VPN access only
- ⚠️ Don't expose to public internet

### API Key Protection
- ✅ Use .env files (in .gitignore)
- ✅ Never commit keys to git
- ✅ Rotate keys regularly
- ✅ Monitor API usage

## 📊 Metrics Explained

### Win Rate
`(Wins / Total Trades) × 100%`

### Total P&L
Sum of all pips/USD across sessions

### Helpful Count
Times a strategy led to profit

### Harmful Count
Times a strategy led to loss

### Execution Quality
AI assessment of how well plan was followed:
- `excellent` - Perfect execution
- `good` - Minor deviations
- `fair` - Some issues
- `poor` - Significant problems

---

**Quick Start:** `./scripts/launch_ui.sh` → Open browser → Navigate → Enjoy! 🚀
