# GemEx - AI-Powered Forex Trading Analysis System

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

GemEx is an advanced, AI-powered forex trading analysis system that combines quantitative market data with large language model (LLM) intelligence to generate comprehensive trading strategies. The system operates under the codename "Viper" and provides institutional-grade market analysis for EURUSD trading.

## 🚀 Features

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
│   │   └── review_scores.json # AI quality assessment
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
Run your script and you should receive a formatted message with:
- Market snapshot (EURUSD price, trends)
- Analysis scores (Plan Quality & Confidence)
- Trading decision (GO/WAIT/NO-GO)
- File generation confirmation

### 5. GitHub Actions Setup (Future)
When you're ready to automate with GitHub Actions, add these secrets to your repository:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

The bot will automatically send results after each analysis run.
