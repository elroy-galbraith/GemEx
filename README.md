# GemEx - AI-Powered Forex Trading Analysis System

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

GemEx is an advanced, AI-powered forex trading analysis system that combines quantitative market data with large language model (LLM) intelligence to generate comprehensive trading strategies. The system operates under the codename "Viper" and provides institutional-grade market analysis for EURUSD trading.

> **📦 Package Structure Update**: GemEx now uses a professional Python package structure! All code is organized under `gemex/` with subpackages for ACE (`gemex/ace/`) and UI (`gemex/ui/`). Old imports still work via symlinks. See [PYTHON_REORGANIZATION_COMPLETE.md](PYTHON_REORGANIZATION_COMPLETE.md) for details.

## 🆕 ACE Trading System (Proof of Concept)

**NEW**: GemEx now includes an **ACE (Agentic Context Engineering)** trading system that evolves a comprehensive trading "Playbook" through daily market analysis and weekly reflection cycles. This system maintains an evolving knowledge base that accumulates strategies, patterns, and lessons over time without requiring model weight updates.

### Key Features of ACE System

- **🧠 Evolving Playbook**: Structured knowledge base that grows and improves over time
- **📊 Daily Cycle**: Generates trading plans using playbook + market data
- **🔄 Weekly Reflection**: Analyzes performance and updates playbook automatically
- **🎯 Realistic Simulation**: Paper trading validated with actual historical price data from Yahoo Finance
- **📈 Continuous Learning**: System improves from experience without retraining

### 🆕 Realistic Simulation Feature

The ACE system now uses **actual historical price data** to validate trading plans instead of random outcomes:

**How It Works:**
- ✅ Fetches real 15-minute EURUSD price data from Yahoo Finance
- ✅ Checks if price actually touched your entry zone
- ✅ Validates which hit first: stop loss or take profit
- ✅ Records exact entry/exit times and actual P&L
- ✅ Falls back gracefully when data unavailable (weekends/holidays)

**Benefits:**
- More realistic performance metrics without broker connection
- Validates AI-generated entry zones and stop losses
- Backtesting capability for strategy development
- Builds confidence before live trading

See **[REALISTIC_SIMULATION_UPGRADE.md](REALISTIC_SIMULATION_UPGRADE.md)** for complete documentation.

### Quick Start with ACE

**Option 1: Web UI (Recommended for Beginners)**
```bash
# Launch the interactive dashboard
./scripts/launch_ui.sh
# Or: streamlit run app.py
```

**Option 2: Command Line**
```bash
# Run daily trading cycle (generates plan and simulates execution)
python ace_main.py --cycle daily

# Run weekly reflection (analyzes performance and updates playbook)
python ace_main.py --cycle weekly

# Run tests
python tests/test_ace_components.py
```

📖 **Documentation:**
- [ACE_README.md](ACE_README.md) - Complete ACE system documentation
- [UI_GUIDE.md](UI_GUIDE.md) - Web interface user guide

## 🚀 Features

### Web Interface (NEW)
- **📊 Interactive Dashboard**: Streamlit-based web UI for easy system management
- **🎛️ One-Click Controls**: Run daily/weekly cycles with a single button
- **📈 Visual Analytics**: Charts, performance metrics, and playbook browser
- **🔍 Session Explorer**: Browse historical trading sessions and analysis
- **📱 Responsive Design**: Clean, modern interface optimized for desktop use

### Core Capabilities
- **Multi-Timeframe Analysis**: Daily, 4-hour, and 1-hour market structure analysis
- **AI-Powered Strategy Generation**: Uses Google Gemini Pro for intelligent trade planning
- **Automated Quality Review**: AI reviewer validates trading plans for consistency and logic
- **Real-time Market Data**: Integrates with Yahoo Finance for live market data
- **Economic Calendar Integration**: Scrapes Forex Factory for high-impact economic events
- **Technical Indicators**: EMA, RSI, ATR, and peak detection algorithms
- **Intermarket Analysis**: Correlates EURUSD with DXY, US10Y, EURJPY, and SPX500

### Trading Intelligence
- **Risk Management**: Enforces minimum 2.5:1 risk-reward ratios
- **Level Justification**: Every support/resistance level is backed by technical analysis
- **If/Then Logic**: Dynamic decision trees based on market conditions
- **Capital Protection**: Built-in risk controls and position sizing guidelines

## 🏗️ Architecture

### System Components

```
GemEx/
├── market_planner.py          # Main application entry point
├── requirements.txt           # Python dependencies
├── trading_session/           # Output directory for analysis
│   ├── YYYY_MM_DD/          # Date-based subdirectories
│   │   ├── viper_packet.json # Raw market data analysis
│   │   ├── trade_plan.md     # Generated trading strategy
│   │   ├── review_scores.json # AI quality assessment
│   │   └── mt5_alerts.json   # MT5 price alert instructions
│   └── [current session files]
└── gemx_venv/                # Python virtual environment
```

### Data Flow Pipeline

1. **Data Collection** → Market data from Yahoo Finance
2. **Technical Analysis** → EMA, RSI, ATR, support/resistance calculation
3. **Data Packet Generation** → Structured JSON with all analysis
4. **AI Strategy Generation** → Gemini Pro creates trading plan
5. **Quality Review** → AI reviewer validates plan consistency
6. **Execution Decision** → Go/No-Go recommendation based on scores

## 📊 Market Analysis Features

### Technical Indicators
- **Exponential Moving Averages**: 50 and 200 period EMAs
- **Relative Strength Index**: 14-period RSI with overbought/oversold levels
- **Average True Range**: 14-period ATR for volatility measurement
- **Peak Detection**: Automated support and resistance identification

### Market Structure Analysis
- **Trend Classification**: Bullish, Bearish, or Consolidating based on EMA relationships
- **Key Levels**: Top 3 support and resistance levels per timeframe
- **Volatility Metrics**: Daily ATR in pips and predicted price ranges
- **Intermarket Confluence**: Correlation analysis with related instruments

### Fundamental Integration
- **Economic Calendar**: High and medium-impact EUR/USD events
- **News Filtering**: Automated relevance scoring for trading impact
- **Event Timing**: UTC-based scheduling for global market coordination

## 📄 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

### ⚠️ Important Disclaimers

**EDUCATIONAL PURPOSE ONLY**: This software is provided STRICTLY FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY. It is NOT intended for actual trading, investment decisions, or financial advice.

**NO FINANCIAL ADVICE**: This software does not constitute financial advice, investment recommendations, or trading signals. Any analysis, predictions, or outputs generated should NOT be used to make actual trading decisions.

**USE AT YOUR OWN RISK**: By using this software, you acknowledge that you understand the risks involved and agree to use it entirely at your own risk. The authors and contributors shall not be liable for any losses, damages, or financial harm.

**For complete disclaimers and legal information, please read the full [LICENSE](LICENSE) file.**

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.12 or higher
- Google Gemini API key
- Virtual environment (recommended)

### Quick Start

1. **Clone and Setup Environment**
   ```bash
   cd GemEx
   python -m venv gemx_venv
   source gemx_venv/bin/activate  # On Windows: gemx_venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure API Key**
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   # Or create a .env file with: GEMINI_API_KEY=your_api_key_here
   ```

3. **Run Analysis**
   ```bash
   python market_planner.py
   ```

### Environment Variables
- `GEMINI_API_KEY`: Required for AI strategy generation
- `GOOGLE_API_KEY`: Alternative environment variable name

## 📈 Usage

### Daily Trading Session

1. **Execute Analysis**
   ```bash
   python market_planner.py
   ```

2. **Review Outputs**
   - Check `trading_session/YYYY_MM_DD/viper_packet.json` for raw data
   - Review `trade_plan.md` for trading strategy
   - Examine `review_scores.json` for quality assessment

3. **Execution Decision**
   - **Green (GO)**: Quality ≥6 AND Confidence ≥6
   - **Yellow (WAIT)**: Quality ≥6 BUT Confidence <6
   - **Red (NO-GO)**: Quality <6 OR Confidence <6

### Output Structure

#### Viper Data Packet (`viper_packet.json`)
```json
{
  "marketSnapshot": {
    "pair": "EURUSD",
    "currentPrice": 1.1691,
    "currentTimeUTC": "2025-08-31T09:16:34.244162+00:00"
  },
  "multiTimeframeAnalysis": {
    "Daily": { "trendDirection": "Bullish", "keySupportLevels": [...], ... },
    "H4": { "trendDirection": "Bullish", "keySupportLevels": [...], ... },
    "H1": { "trendDirection": "Bullish", "keySupportLevels": [...], ... }
  },
  "volatilityMetrics": { "atr_14_daily_pips": 88, ... },
  "fundamentalAnalysis": { "keyEconomicEvents": [...] },
  "intermarketConfluence": { "DXY_trend": "Bearish", ... }
}
```

#### Trading Plan (`trade_plan.md`)
- Daily market thesis and narrative
- Key support/resistance levels with justifications
- Primary trade idea (Plan A) with entry/exit protocols
- Contingency trade idea (Plan B)
- Risk management and execution protocols

#### Review Scores (`review_scores.json`)
```json
{
  "planQualityScore": { "score": 7, "justification": "..." },
  "confidenceScore": { "score": 6, "justification": "..." }
}
```

#### MT5 Price Alerts (`mt5_alerts.json`)
```json
{
  "alerts": [
    {
      "symbol": "EURUSD",
      "price": 1.1234,
      "condition": "bid_above|bid_below|ask_above|ask_below",
      "action": "notification",
      "enabled": true,
      "comment": "Plan A Entry Level Reached - Value Zone Retest",
      "category": "entry|exit|level",
      "priority": "high|medium|low"
    }
  ],
  "metadata": {
    "generated_at": "2025-01-03T10:00:00.000Z",
    "symbol": "EURUSD",
    "current_price": 1.1200,
    "total_alerts": 8
  }
}
```

The MT5 alerts file contains:
- **Structured price alert data** for import into MetaTrader 5
- **Entry/exit level notifications** for both Plan A and Plan B setups
- **Key level alerts** for support, resistance, and pivot points
- **Human-readable comments** for each alert with justification
- **Priority levels** to help focus on the most important price levels

### Using MT5 Price Alerts

1. **Manual Setup in MT5:**
   - Open MT5 Terminal → Tools → Options → Events
   - Enable "Alert" sound notifications
   - In Navigator panel → right-click "Alerts" → "Create"
   - Set Symbol: EURUSD, Condition: "Bid >" or "Bid <", Value: price level
   - Set Action: "Sound" and/or "Notification"
   - Copy alert comments exactly as provided in the trading plan

2. **Automated Import (Advanced):**
   - Use MT5 Expert Advisor to read the JSON file
   - Automatically create price alerts from the structured data
   - Enable audio/visual notifications when price levels are reached
   - **Note: These are alerts only - no automatic trading**

## 🔧 Configuration

### Market Symbols
Edit the `SYMBOLS` dictionary in `market_planner.py`:
```python
SYMBOLS = {
    "EURUSD": "EURUSD=X",
    "DXY": "DX-Y.NYB",
    "US10Y": "^TNX",
    "EURJPY": "EURJPY=X",
    "SPX500": "^GSPC"
}
```

### Timeframe Analysis
Modify the `analyze_timeframe()` function parameters:
- EMA periods (currently 50, 200)
- RSI period (currently 14)
- ATR period (currently 14)
- Peak detection sensitivity

### AI Model Configuration
```python
MODEL_NAME = "gemini-1.5-pro-latest"  # Change model as needed
```

## 📚 Dependencies

### Core Libraries
- **yfinance**: Market data retrieval
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **scipy**: Signal processing and peak detection
- **google-generativeai**: Gemini AI integration

### Web Scraping
- **cloudscraper**: Economic calendar scraping
- **beautifulsoup4**: HTML parsing

### Utilities
- **python-dotenv**: Environment variable management
- **pathlib**: Cross-platform path handling

## 🎯 Trading Strategy Philosophy

### Core Principles
1. **Data-Driven Decisions**: All analysis based on quantitative market data
2. **Risk Management First**: Minimum 2.5:1 risk-reward ratios
3. **Multi-Timeframe Confirmation**: Daily, H4, and H1 alignment
4. **Intermarket Confluence**: Correlation with related instruments
5. **Fundamental Context**: Economic events and news impact

### Risk Controls
- Maximum daily loss: 1.25% of capital
- Position sizing: 0.75% risk on primary trades, 0.5% on contingency
- Stop loss management: Move to breakeven at first profit target
- Partial profit taking: Close 50% at TP1

## 🚨 Disclaimer

**This software is for educational and research purposes only. It is not financial advice and should not be used for actual trading without proper risk management and professional guidance.**

- Past performance does not guarantee future results
- Forex trading involves substantial risk of loss
- Always use proper position sizing and risk management
- Consult with qualified financial professionals before trading

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Review the code comments for implementation details
- Check the trading session outputs for debugging

## 🔮 Future Enhancements

- [ ] Additional currency pairs support
- [ ] Real-time data streaming
- [ ] Advanced risk management algorithms
- [ ] Portfolio optimization features
- [ ] Machine learning model integration
- [ ] Web-based dashboard interface
- [ ] Mobile application
- [ ] Backtesting and performance analytics

---

**Built with ❤️ for the trading community**

*"Viper" - Precision trading through AI-powered analysis*

## Telegram Integration Setup

To receive trading analysis results via Telegram messages, follow these steps:

### 1. Create a Telegram Bot
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Choose a name for your bot (e.g., "GemEx Trading Bot")
4. Choose a username (must end with 'bot', e.g., "gemex_trading_bot")
5. Save the bot token provided by BotFather

### 2. Get Your Chat ID
1. Start a chat with your bot by clicking the bot link
2. Send any message to the bot
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for the `"chat":{"id":123456789}` in the response
5. Save this chat ID number

### 3. Set Environment Variables
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

Or add to your `.env` file:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### 4. Test the Integration
Run your script and you should receive formatted messages with:

#### New Concise Format (v2.0)
- **Primary Summary**: Scannable decision summary (< 250 chars)
  - Market snapshot with current price
  - Clear GO/WAIT/SKIP decision with reasoning  
  - Quality and confidence scores
  - Market bias and next action steps
- **Technical Details** (GO decisions only): Key support/resistance levels
- **Psychology Tip**: Daily rotating trading discipline reminder
- **Execution Plan** (GO decisions only): Abbreviated key execution details

#### Message Types by Decision:
- **✅ GO**: Summary + Technical Details + Psychology Tip + Execution Plan
- **⏸️ WAIT**: Summary + Psychology Tip only  
- **❌ SKIP**: Summary + Psychology Tip only
- **🚨 Critical Warnings**: Override with full details when risk >3% or quality <4

#### Benefits of New Format:
- **39% shorter** primary messages for faster scanning
- **Smart filtering** shows only relevant information per decision type
- **Visual hierarchy** with consistent emoji indicators
- **Context-aware** psychology tips based on market conditions
- **Error-resilient** with graceful fallback messaging

### 5. GitHub Actions Setup (Future)
When you're ready to automate with GitHub Actions, add these secrets to your repository:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

The bot will automatically send results after each analysis run.

## 🚀 GitHub Actions Automation Setup

Automate your trading analysis to run daily with GitHub Actions:

### 1. Repository Secrets Setup
Go to your GitHub repository → Settings → Secrets and variables → Actions, then add:

**Required Secrets:**
- `GEMINI_API_KEY` - Your Google Gemini API key
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `TELEGRAM_CHAT_ID` - Your Telegram chat ID

### 2. Workflow Configuration
The workflow (`.github/workflows/daily-trading-analysis.yml`) is already configured to:
- **Run at 7:00 PM Japan Standard Time (UTC+9) on weekdays only** (Monday-Friday)
- **Allow manual triggering** via "Run workflow" button
- **Install all dependencies** from requirements.txt
- **Execute the analysis** with proper environment variables
- **Send results to Telegram** automatically
- **Save artifacts** for 30 days
- **Commit results** back to the repository (optional)

### 3. Customize Schedule
Edit the cron schedule in `.github/workflows/daily-trading-analysis.yml`:
```yaml
- cron: '0 8 * * *'  # Daily at 8:00 AM UTC
```

**Current schedule:**
- `'0 10 * * 1-5'` - Weekdays at 7:00 PM JST (10:00 AM UTC)

**Other schedule examples:**
- `'0 8 * * *'` - Daily at 8:00 AM UTC
- `'0 9 * * 1-5'` - Weekdays at 9:00 AM UTC
- `'0 */6 * * *'` - Every 6 hours
- `'0 8,20 * * *'` - Twice daily at 8:00 AM and 8:00 PM UTC

### 4. Manual Execution
Trigger the workflow manually anytime:
1. Go to Actions tab in your repository
2. Click "Daily Trading Analysis"
3. Click "Run workflow" button
4. Select branch and click "Run workflow"

### 5. Monitor Execution
- **Actions tab** shows workflow runs and logs
- **Telegram notifications** confirm successful execution
- **Artifacts** store trading session files
- **Repository commits** track analysis history


### 6. Troubleshooting
- **Check Actions logs** for detailed error messages
- **Verify secrets** are correctly set
- **Test locally** before pushing to GitHub
- **Check Telegram bot** is active and accessible

The workflow will automatically run your analysis daily and deliver results directly to your Telegram, making it perfect for automated trading analysis!

## 📚 Documentation

### Main Documentation
- **[README.md](README.md)** - This file, complete project overview
- **[ACE_README.md](ACE_README.md)** - Complete ACE trading system documentation
- **[LICENSE](LICENSE)** - Apache 2.0 license

### Feature Guides
- **[UI_GUIDE.md](UI_GUIDE.md)** - Web interface user guide
- **[UI_QUICK_REFERENCE.md](UI_QUICK_REFERENCE.md)** - Quick UI commands
- **[REALISTIC_SIMULATION_UPGRADE.md](REALISTIC_SIMULATION_UPGRADE.md)** - Realistic simulation documentation
- **[TRADING_JOURNAL_TEMPLATE.md](TRADING_JOURNAL_TEMPLATE.md)** - Trading journal template

### Development & Deployment
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Testing procedures and guidelines
- **[PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md)** - Production deployment guide
- **[VALIDATION_REPORT.md](VALIDATION_REPORT.md)** - System validation report
- **[REORGANIZATION_COMPLETE.md](REORGANIZATION_COMPLETE.md)** - Scripts reorganization summary
- **[PYTHON_REORGANIZATION_COMPLETE.md](PYTHON_REORGANIZATION_COMPLETE.md)** - Package structure migration guide
- **[PYTHON_REORGANIZATION_VISUAL.md](PYTHON_REORGANIZATION_VISUAL.md)** - Visual package structure guide
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Package structure quick reference

### Scripts
- **[scripts/README.md](scripts/README.md)** - Shell scripts documentation

## 🗂️ Project Structure

```
gemex/                          # Main Python package
├── ace/                        # ACE system subpackage
│   ├── components.py           # Core ACE components
│   ├── main.py                 # Daily/weekly cycle runner
│   ├── integrated.py           # Integrated ACE functions
│   ├── persistence.py          # Artifact persistence
│   └── demo.py                 # Demo mode
├── ui/                         # Web interface
│   └── app.py                  # Streamlit dashboard
├── market_planner.py           # Market analysis engine
├── prompts.py                  # AI system prompts
└── config.py                   # Configuration constants

scripts/                        # Shell scripts
├── launch_ui.sh               # Launch web UI
├── run_daily.sh               # Run daily cycle
└── ...

tests/                          # Test suite
data/                          # Playbook storage
trading_session/               # Generated plans
weekly_reflections/            # Weekly analysis
```

