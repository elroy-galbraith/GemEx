# GemEx UI Visual Guide

## 🎨 Interface Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         🎯 GemEx Trading System                         │
│                 AI-Powered Forex Trading Analysis System                │
├──────────────┬──────────────────────────────────────────────────────────┤
│              │                                                           │
│  SIDEBAR     │                    MAIN CONTENT AREA                     │
│              │                                                           │
│ ┌──────────┐ │  ┌─────────────────────────────────────────────────┐    │
│ │Navigation│ │  │                                                 │    │
│ ├──────────┤ │  │         Page-Specific Content                  │    │
│ │📊Dashboard│ │  │         (Changes based on sidebar selection)    │    │
│ │🌅Daily    │ │  │                                                 │    │
│ │🔄Weekly   │ │  │         - Metrics and stats                    │    │
│ │📚Playbook │ │  │         - Interactive controls                 │    │
│ │📈Charts   │ │  │         - Data visualizations                  │    │
│ └──────────┘ │  │         - Tables and JSON viewers              │    │
│              │  │                                                 │    │
│ ┌──────────┐ │  └─────────────────────────────────────────────────┘    │
│ │Quick Stats│ │                                                          │
│ ├──────────┤ │  ┌─────────────────────────────────────────────────┐    │
│ │Version:1.0│ │  │                                                 │    │
│ │Bullets: 15│ │  │         Additional Content                     │    │
│ │Last:10-27│ │  │         (Scrollable)                            │    │
│ └──────────┘ │  │                                                 │    │
│              │  └─────────────────────────────────────────────────┘    │
│ ┌──────────┐ │                                                          │
│ │  Status  │ │  ┌─────────────────────────────────────────────────┐    │
│ ├──────────┤ │  │                 Footer                          │    │
│ │✓ Gemini  │ │  │   GemEx - For Educational Purposes Only        │    │
│ │⚠Telegram │ │  └─────────────────────────────────────────────────┘    │
│ └──────────┘ │                                                          │
└──────────────┴──────────────────────────────────────────────────────────┘
```

## 📊 Dashboard Page Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  📊 GemEx Trading Dashboard                                         │
│  AI-Powered Forex Trading Analysis System                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  System  │  │ Playbook │  │  Recent  │  │   Last   │          │
│  │  Status  │  │ Bullets  │  │ Sessions │  │Reflection│          │
│  │          │  │          │  │          │  │          │          │
│  │🟢 Active │  │    15    │  │    5     │  │ 2025-W43 │          │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  📋 Latest Trading Plan                                            │
├─────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────┐  ┌───────────────────────┐     │
│  │ Date: 2025-10-27              │  │                       │     │
│  │ Bias: BULLISH 📈              │  │   [EURUSD 4H Chart]   │     │
│  │ Confidence: HIGH              │  │                       │     │
│  │                               │  │                       │     │
│  │ ▼ View Rationale              │  └───────────────────────┘     │
│  │   AI analysis indicates...    │                                │
│  └───────────────────────────────┘                                │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  📈 Recent Performance                                             │
├─────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐    │
│  │ Date       │ Outcome │ Pips  │ USD     │ Quality       │    │
│  ├───────────────────────────────────────────────────────────┤    │
│  │ 2025-10-27 │ win     │ +45.2 │ $452.00 │ excellent    │    │
│  │ 2025-10-26 │ loss    │ -20.1 │ -$201.00│ good         │    │
│  │ 2025-10-25 │ no_trade│  0.0  │  $0.00  │ N/A          │    │
│  └───────────────────────────────────────────────────────────┘    │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                        │
│  │  Wins    │  │  Losses  │  │Total Pips│                        │
│  │    3     │  │    2     │  │  +45.7   │                        │
│  └──────────┘  └──────────┘  └──────────┘                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 🌅 Daily Cycle Page Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  🌅 Daily Trading Cycle                                             │
│  Run the daily trading analysis and plan generation.               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ▼ ℹ️ How Daily Cycle Works                                        │
│    The Daily Cycle performs the following steps:                   │
│    1. Load Playbook - Retrieves current strategies                 │
│    2. Gather Market Data - Fetches EURUSD, DXY, SPX500, US10Y     │
│    3. Generate Charts - Creates technical analysis charts          │
│    4. Create Trading Plan - AI generates plan using playbook       │
│    5. Simulate Execution - Paper trades the plan                   │
│    6. Send Notifications - Sends plan to Telegram                  │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐   │
│  │                          │  │                              │   │
│  │  ▶️ Run Daily Cycle      │  │  💡 The daily cycle will    │   │
│  │                          │  │  generate charts, create a   │   │
│  │  [Primary Button]        │  │  trading plan, and simulate  │   │
│  │                          │  │  execution.                  │   │
│  └──────────────────────────┘  └──────────────────────────────┘   │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  📅 Today's Session                                                │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────┐  ┌─────────────────────────┐     │
│  │  Trading Plan               │  │  Charts                 │     │
│  │  {                          │  │  ┌───────────────────┐  │     │
│  │    "date": "2025-10-27",   │  │  │ EURUSD 15M        │  │     │
│  │    "bias": "bullish",      │  │  │ [Chart Image]     │  │     │
│  │    "confidence": "high"    │  │  └───────────────────┘  │     │
│  │  }                         │  │  ┌───────────────────┐  │     │
│  └─────────────────────────────┘  │  │ EURUSD 1H         │  │     │
│                                   │  │ [Chart Image]     │  │     │
│  ┌─────────────────────────────┐  │  └───────────────────┘  │     │
│  │  Execution Log              │  └─────────────────────────┘     │
│  │  {                          │                                  │
│  │    "outcome": "win",       │                                  │
│  │    "pnl_pips": 45.2        │                                  │
│  │  }                         │                                  │
│  └─────────────────────────────┘                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔄 Weekly Reflection Page Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  🔄 Weekly Reflection                                               │
│  Analyze weekly performance and update the playbook.               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐   │
│  │                          │  │                              │   │
│  │  ▶️ Run Weekly Reflection│  │  💡 The weekly reflection    │   │
│  │                          │  │  analyzes your trading       │   │
│  │  [Primary Button]        │  │  performance and evolves     │   │
│  │                          │  │  the playbook.               │   │
│  └──────────────────────────┘  └──────────────────────────────┘   │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  📊 Latest Reflection                                              │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────┐  ┌─────────────────────────┐     │
│  │  Summary                    │  │  Market Regime          │     │
│  │  ┌──────────┐              │  │                         │     │
│  │  │  Total   │              │  │  Trending market with   │     │
│  │  │  Trades  │              │  │  high volatility.       │     │
│  │  │    5     │              │  │  Strong USD correlation.│     │
│  │  └──────────┘              │  │                         │     │
│  │  ┌──────────┐              │  └─────────────────────────┘     │
│  │  │Win Rate  │              │                                  │
│  │  │  60.0%   │              │                                  │
│  │  └──────────┘              │                                  │
│  │  ┌──────────┐              │                                  │
│  │  │Total P&L │              │                                  │
│  │  │ +45.7    │              │                                  │
│  │  └──────────┘              │                                  │
│  └─────────────────────────────┘                                  │
│                                                                     │
│  Insights                                                          │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  1. Bullish setups performed well this week                │  │
│  │  2. News-driven volatility increased win rate              │  │
│  │  3. Late-day entries showed lower success                  │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Recommendations                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  1. Add rule: Avoid entries after 3:00 PM EST              │  │
│  │  2. Increase position size during high volatility          │  │
│  │  3. Update stop-loss strategy for trending markets         │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 📚 Playbook Page Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  📚 Trading Playbook                                                │
│  View and understand your evolving trading strategies.             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                        │
│  │ Version  │  │  Total   │  │  Last    │                        │
│  │   1.0    │  │ Bullets  │  │ Updated  │                        │
│  │          │  │    15    │  │2025-10-27│                        │
│  └──────────┘  └──────────┘  └──────────┘                        │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  🎯 Strategies and Hard Rules                                      │
├─────────────────────────────────────────────────────────────────────┤
│  ▼ strat-001 - Only trade during NY session (9:30 AM - 4:00...    │
│    Content: Only trade during NY session (9:30 AM - 4:00 PM EST)  │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│    │ Helpful  │  │ Harmful  │  │Last Used │                      │
│    │    5     │  │    0     │  │2025-10-27│                      │
│    └──────────┘  └──────────┘  └──────────┘                      │
│                                                                     │
│  ▼ strat-002 - Avoid trading 30min before/after high-impact...    │
│  ▼ strat-003 - Minimum risk-reward ratio: 1:1.5...                │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  💻 Useful Code and Templates                                      │
├─────────────────────────────────────────────────────────────────────┤
│  ▼ code-001 - Position sizing: (account_balance * risk_pct)...    │
│    position_size = (account_balance * risk_pct) / (entry - stop)  │
│    ┌──────────┐  ┌──────────┐                                     │
│    │ Helpful  │  │ Harmful  │                                     │
│    │    8     │  │    0     │                                     │
│    └──────────┘  └──────────┘                                     │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  ⚠️ Troubleshooting and Pitfalls                                   │
├─────────────────────────────────────────────────────────────────────┤
│  ▼ pit-001 - Low liquidity after 3:00 PM EST - avoid new...       │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  ▼ 📄 View Raw Playbook JSON                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 📈 Charts & Data Page Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  📈 Charts & Market Data                                            │
│  View technical analysis charts and market data from recent sessions│
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Select Trading Session: [2025-10-27 ▼]                           │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  📊 Technical Charts                                               │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────┬─────┬─────┬─────┐                                        │
│  │ 15M │ 1H  │ 4H  │Daily│  [Tab Navigation]                      │
│  └─────┴─────┴─────┴─────┘                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                                                             │  │
│  │                   EURUSD 4H Chart                           │  │
│  │                   [Chart Image]                             │  │
│  │                                                             │  │
│  │                   Candlesticks with:                        │  │
│  │                   - EMA 50 (blue)                           │  │
│  │                   - EMA 200 (red)                           │  │
│  │                   - Support/Resistance levels               │  │
│  │                                                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  📄 Session Data                                                   │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────┐  ┌─────────────────────────┐     │
│  │ ▼ 🐍 Viper Packet          │  │ ▼ 📊 Trade Log         │     │
│  │   (Market Data)            │  │                         │     │
│  │   {                        │  │   {                     │     │
│  │     "marketSnapshot": {    │  │     "outcome": "win",  │     │
│  │       "price": 1.0850,    │  │     "pnl_pips": 45.2   │     │
│  │       ...                 │  │   }                     │     │
│  │     }                     │  │                         │     │
│  │   }                       │  └─────────────────────────┘     │
│  └─────────────────────────────┘                                  │
│  ┌─────────────────────────────┐  ┌─────────────────────────┐     │
│  │ ▼ 📋 Trading Plan          │  │ ▼ ⭐ Review Scores      │     │
│  │   {                        │  │   {                     │     │
│  │     "bias": "bullish",    │  │     "quality": 8,      │     │
│  │     "confidence": "high"  │  │     "confidence": 7    │     │
│  │   }                       │  │   }                     │     │
│  └─────────────────────────────┘  └─────────────────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 🎨 Color Scheme

```
Primary Colors:
  🔵 Blue (#1f77b4)    - Headers, primary actions
  🟢 Green (#28a745)   - Success, wins, positive
  🟡 Yellow (#ffc107)  - Warnings, waiting
  🔴 Red (#dc3545)     - Errors, losses, negative

Background Colors:
  ⚪ White (#ffffff)   - Main background
  ⬜ Light Gray (#f0f2f6) - Card backgrounds
  ⬛ Dark Gray (#262730) - Text

Accent Colors:
  💙 Light Blue (#d4edda) - Success boxes
  💛 Light Yellow (#fff3cd) - Warning boxes
  ❤️ Light Red (#f8d7da) - Danger boxes
```

## 🔤 Typography

```
Headers:
  H1: 2.5rem, bold (Page titles)
  H2: 2.0rem, bold (Section headers)
  H3: 1.5rem, bold (Subsections)

Body:
  Normal: 1.0rem (Regular text)
  Small: 0.875rem (Metadata, timestamps)
  Code: monospace (JSON, data)

Metrics:
  Large: 2.0rem, bold (Main metric value)
  Medium: 1.5rem, bold (Card metrics)
  Small: 1.0rem (Inline metrics)
```

## 📐 Spacing

```
Padding:
  Cards: 1rem
  Sections: 1.5rem
  Container: 2rem

Margins:
  Between sections: 2rem
  Between elements: 1rem
  Between cards: 0.5rem

Border Radius:
  Cards: 0.5rem
  Buttons: 0.25rem
  Inputs: 0.25rem
```

## 🖱️ Interactive Elements

```
Buttons:
  Primary: Blue, full-width in column
  Secondary: Gray, inline
  Danger: Red, for destructive actions

Expandables:
  ▼ Closed (click to expand)
  ▲ Open (click to collapse)

Tabs:
  Active: Blue underline
  Inactive: Gray text

Dropdowns:
  Select box with down arrow
  Options list on click
```

This visual guide should help you understand the UI layout and design! 🎨✨
