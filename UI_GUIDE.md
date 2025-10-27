# GemEx Web UI Guide

## Overview

The GemEx Web UI is a simple, elegant Streamlit-based dashboard that provides a graphical interface for managing and monitoring your AI-powered forex trading system.

## Features

### 📊 Dashboard
- **System Overview**: View system status, playbook stats, and recent performance
- **Latest Trading Plan**: Quick access to today's trading analysis
- **Recent Performance**: Track wins, losses, and P&L across recent sessions
- **Visual Metrics**: Color-coded cards for quick status checks

### 🌅 Daily Cycle
- **One-Click Execution**: Run the complete daily trading cycle with a single button
- **Real-time Progress**: Watch the analysis process with live console output
- **Session Review**: View today's trading plan, charts, and execution logs
- **Automated Workflow**: Handles data gathering, chart generation, and plan creation

### 🔄 Weekly Reflection
- **Performance Analysis**: AI-powered review of weekly trading performance
- **Insights & Recommendations**: Actionable feedback from your trading history
- **Playbook Evolution**: Automatic updates to your trading strategies
- **Historical Tracking**: Access to past reflections and performance trends

### 📚 Playbook Management
- **Browse Strategies**: View all trading rules and strategies
- **Track Effectiveness**: See helpful/harmful counts for each rule
- **Usage Analytics**: Understand which strategies are actively used
- **Organized Sections**: Strategies, code templates, and pitfall warnings

### 📈 Charts & Data
- **Multi-Timeframe Analysis**: View 15M, 1H, 4H, and Daily charts
- **Session History**: Browse charts and data from any past session
- **Interactive Tabs**: Organized chart viewing by timeframe
- **Data Export**: Access raw JSON data for all sessions

## Installation

### 1. Install Dependencies

If you haven't already installed the requirements:

```bash
pip install -r requirements.txt
```

This will install Streamlit along with all other dependencies.

### 2. Verify Installation

```bash
streamlit --version
```

You should see something like: `Streamlit, version 1.28.0`

## Running the UI

### Basic Usage

From the GemEx directory, run:

```bash
streamlit run app.py
```

The dashboard will automatically open in your default web browser at `http://localhost:8501`

### Custom Port

To run on a different port:

```bash
streamlit run app.py --server.port 8080
```

### Remote Access

To allow remote access (use with caution):

```bash
streamlit run app.py --server.address 0.0.0.0
```

## Navigation

### Sidebar Controls

The sidebar provides:
- **Navigation Menu**: Switch between different pages
- **Quick Stats**: Real-time system metrics
- **System Status**: API and configuration checks

### Main Pages

1. **Dashboard** - Overview and recent activity
2. **Daily Cycle** - Run and view daily trading analysis
3. **Weekly Reflection** - Analyze performance and update playbook
4. **Playbook** - Browse and understand trading strategies
5. **Charts & Data** - View historical charts and session data

## Workflow

### Daily Trading Routine

1. **Morning (8:00 AM EST)**
   - Open the UI: `streamlit run app.py`
   - Navigate to **Daily Cycle**
   - Click "▶️ Run Daily Cycle"
   - Wait 1-2 minutes for completion
   - Review the generated trading plan
   - Check charts on the **Charts & Data** page

2. **Throughout the Day**
   - Monitor execution in the **Dashboard**
   - Reference the trading plan as needed

### Weekly Review (Friday EOD)

1. **Friday (5:00 PM EST)**
   - Navigate to **Weekly Reflection**
   - Click "▶️ Run Weekly Reflection"
   - Wait 2-3 minutes for analysis
   - Review insights and recommendations
   - Check updated playbook on **Playbook** page

## Features in Detail

### Dashboard Page

**Metrics Display:**
- System status indicator (🟢 Active)
- Current playbook bullet count
- Number of recent sessions
- Last reflection date

**Latest Trading Plan:**
- Trading bias (Bullish/Bearish/Neutral)
- Confidence level
- Rationale and reasoning
- Associated chart preview

**Recent Performance:**
- Last 5 trading sessions
- Win/loss outcomes
- P&L in pips and USD
- Execution quality ratings

### Daily Cycle Page

**Process Steps:**
1. Load playbook
2. Gather market data (EURUSD, DXY, SPX500, US10Y)
3. Generate technical charts
4. Create AI trading plan
5. Simulate execution
6. Send Telegram notifications

**Output Files:**
- `trading_plan.json` - Structured plan data
- `trading_plan.md` - Human-readable plan
- `trade_log.json` - Execution results
- `*.png` - Technical analysis charts

### Weekly Reflection Page

**Analysis Components:**
- Total trades for the week
- Win rate calculation
- Total P&L in pips
- Market regime identification
- Pattern recognition
- Strategy effectiveness

**Playbook Updates:**
- Add successful new strategies
- Remove harmful rules
- Update helpful/harmful counts
- Version control with backups

### Playbook Page

**Section Organization:**

1. **Strategies and Hard Rules**
   - Entry/exit criteria
   - Risk management rules
   - Session timing rules
   - News avoidance protocols

2. **Useful Code and Templates**
   - Position sizing formulas
   - Risk calculation snippets
   - Common trading calculations

3. **Troubleshooting and Pitfalls**
   - Common mistakes to avoid
   - Market condition warnings
   - Technical gotchas

**Bullet Tracking:**
- Helpful count (how many times it led to profit)
- Harmful count (how many times it led to loss)
- Last used timestamp
- Creation date

### Charts & Data Page

**Available Charts:**
- EURUSD 15-minute (day trading)
- EURUSD 1-hour (intraday)
- EURUSD 4-hour (swing)
- EURUSD Daily (trend)
- Intermarket correlation charts

**Data Files:**
- **Viper Packet**: Complete market snapshot
- **Trading Plan**: AI-generated strategy
- **Trade Log**: Execution details
- **Review Scores**: Quality metrics

## Troubleshooting

### UI Won't Start

**Problem:** `streamlit: command not found`

**Solution:**
```bash
pip install streamlit
# or
pip install -r requirements.txt
```

### API Key Warnings

**Problem:** "Gemini API Not Configured" in sidebar

**Solution:**
```bash
export GEMINI_API_KEY="your_api_key_here"
# Or add to .env file
echo "GEMINI_API_KEY=your_api_key_here" >> .env
```

### No Data Displayed

**Problem:** "No trading plan available"

**Solution:** Run the Daily Cycle at least once to generate data

### Command Timeout

**Problem:** Daily/Weekly cycle times out

**Solution:** The timeout is set to 5 minutes. If operations consistently take longer, you may need to:
- Check internet connection
- Verify API rate limits
- Run commands manually to debug

## Performance Tips

### Faster Loading

1. **Cache Data**: Streamlit automatically caches loaded data
2. **Limit History**: The UI only loads the 5 most recent sessions by default
3. **Lazy Loading**: Charts and data are loaded only when viewed

### Memory Management

- Large chart files are streamed, not loaded into memory
- JSON files are read on-demand
- Browser caching helps with repeated views

## Security Considerations

### Local Use Only (Default)

By default, the UI only accepts connections from `localhost`. This is safe for personal use.

### Remote Access

If you enable remote access:
```bash
streamlit run app.py --server.address 0.0.0.0
```

**⚠️ WARNING:** This allows anyone on your network to access the UI. Consider:
- Running behind a firewall
- Using authentication (Streamlit Cloud has built-in auth)
- Limiting to VPN access only

### API Key Security

- Never commit API keys to git
- Use `.env` files (already in `.gitignore`)
- Rotate keys regularly
- Monitor API usage for anomalies

## Customization

### Changing Theme

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### Modifying Layout

Edit `app.py`:
- Adjust column widths in `st.columns()`
- Change metric positions
- Add new pages to navigation
- Customize CSS in the `st.markdown()` blocks

### Adding Features

The UI is built modularly. To add a new page:

```python
elif page == "My New Page":
    st.markdown('<p class="main-header">📊 My New Page</p>', unsafe_allow_html=True)
    # Your custom code here
```

## Integration with Existing Workflows

### Command Line + UI Hybrid

You can use both:

```bash
# Run daily cycle from terminal
python ace_main.py --cycle daily

# Then view results in UI
streamlit run app.py
```

### Automated + Manual

- Let GitHub Actions run scheduled cycles
- Use UI for manual analysis and review
- Best of both worlds

### Telegram + UI

- Telegram for mobile notifications
- UI for detailed desktop analysis
- Both work independently

## Support and Documentation

### Main Documentation
- [README.md](README.md) - Full system overview
- [ACE_README.md](ACE_README.md) - ACE system details
- [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md) - Production deployment
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing procedures

### Streamlit Resources
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Gallery](https://streamlit.io/gallery)
- [Streamlit Community](https://discuss.streamlit.io/)

## Limitations

### Current Limitations

1. **Single User**: Not designed for multi-user access
2. **No Authentication**: Local access only by default
3. **No Real-time Updates**: Refresh needed to see new data
4. **No Trade Execution**: Display only, no direct MT5 integration
5. **Educational Use**: Not for production trading

### Future Enhancements

Potential improvements (not yet implemented):
- [ ] Real-time data streaming
- [ ] Multi-user support with authentication
- [ ] Advanced performance analytics
- [ ] Backtesting integration
- [ ] Direct broker API integration
- [ ] Mobile-responsive design
- [ ] Custom alert configuration
- [ ] Portfolio management

## Best Practices

### Daily Usage

1. ✅ Run Daily Cycle before market opens
2. ✅ Review plan thoroughly before trading
3. ✅ Check system status in sidebar
4. ✅ Verify chart generation succeeded
5. ✅ Monitor execution quality

### Weekly Usage

1. ✅ Run Weekly Reflection every Friday
2. ✅ Review insights carefully
3. ✅ Understand playbook changes
4. ✅ Track performance trends
5. ✅ Adjust strategies based on data

### Data Management

1. ✅ Keep session history for at least 30 days
2. ✅ Archive old sessions periodically
3. ✅ Backup playbook before major changes
4. ✅ Review playbook version history
5. ✅ Monitor disk space usage

## Troubleshooting Common Issues

### Issue: Button Clicks Don't Work

**Cause:** Streamlit session state conflict

**Solution:** Refresh the page (F5)

### Issue: Charts Not Displaying

**Cause:** Missing PNG files

**Solution:** Run Daily Cycle to regenerate charts

### Issue: JSON Load Errors

**Cause:** Corrupted or incomplete JSON files

**Solution:** Re-run the cycle that generated the file

### Issue: Slow Performance

**Cause:** Too many historical sessions

**Solution:** Archive or delete old session folders

## Conclusion

The GemEx Web UI provides an intuitive, visual interface to your AI-powered trading system. It's designed to:

- **Simplify** complex trading workflows
- **Visualize** market data and analysis
- **Track** performance over time
- **Manage** your evolving trading playbook

Enjoy trading with a clearer view of your system! 📊✨

---

**Remember:** This is for educational purposes only. Never trade with money you can't afford to lose.
