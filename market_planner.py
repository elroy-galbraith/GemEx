import yfinance as yf
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from datetime import datetime, timezone
import os
import json
from pathlib import Path
import cloudscraper
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
import requests
load_dotenv()

# --- 0. MASTER CONFIGURATION ---

# --- API and Model Setup ---
# To run locally, set your API key as an environment variable:
# export GOOGLE_API_KEY="your_api_key_here"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") #, userdata.get('GEMINI_API_KEY'))
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please set it as an environment variable.")
genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-1.5-pro-latest"

# --- Telegram Configuration ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- File Path Setup ---
OUTPUT_DIR = Path("trading_session")
# Create date-based subfolder (e.g., trading_session/2025_08_31)
CURRENT_DATE = datetime.now().strftime("%Y_%m_%d")
DATE_OUTPUT_DIR = OUTPUT_DIR / CURRENT_DATE
DATA_PACKET_PATH = DATE_OUTPUT_DIR / "viper_packet.json"
PLAN_OUTPUT_PATH = DATE_OUTPUT_DIR / "trade_plan.md"
REVIEW_OUTPUT_PATH = DATE_OUTPUT_DIR / "review_scores.json"

# --- Market Symbols ---
SYMBOLS = {
    "EURUSD": "EURUSD=X",
    "DXY": "DX-Y.NYB",
    "US10Y": "^TNX",
    "EURJPY": "EURJPY=X",
    "SPX500": "^GSPC"
}

# --- Telegram Functions ---

def send_telegram_message(message, parse_mode="Markdown"):
    """Send a message to Telegram via bot API."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": parse_mode
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        print("✅ Telegram message sent successfully")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send Telegram message: {e}")
        return False

def send_trading_summary(data_packet, trade_plan_path, review_scores_path):
    """Send a summary of the trading analysis to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    try:
        # Read the trade plan
        with open(trade_plan_path, 'r') as f:
            trade_plan = f.read()
        
        # Read the review scores
        with open(review_scores_path, 'r') as f:
            review_scores = json.load(f)
        
        # Extract key information
        current_price = data_packet["marketSnapshot"]["currentPrice"]
        current_time = data_packet["marketSnapshot"]["currentTimeUTC"]
        daily_trend = data_packet["multiTimeframeAnalysis"]["Daily"]["trendDirection"]
        h4_trend = data_packet["multiTimeframeAnalysis"]["H4"]["trendDirection"]
        
        quality_score = review_scores['planQualityScore']['score']
        confidence_score = review_scores['confidenceScore']['score']
        
        # Create summary message
        message = f"""🚀 *GemEx Trading Analysis Complete*

📊 *Market Snapshot*
• EURUSD: {current_price}
• Daily Trend: {daily_trend}
• H4 Trend: {h4_trend}
• Time: {current_time[:19]} UTC

📈 *Analysis Scores*
• Plan Quality: {quality_score}/10
• Confidence: {confidence_score}/10

🎯 *Decision*
"""
        
        if quality_score >= 6 and confidence_score >= 6:
            message += "🟢 *GO FOR EXECUTION* - Plan is solid and conviction is high"
        elif quality_score >= 6 and confidence_score < 6:
            message += "🟡 *WAIT AND SEE* - Plan is solid, but market feel is off"
        else:
            message += "🔴 *NO-GO* - DISCARD PLAN - Quality or Confidence too low"
        
        message += f"""

📁 *Files Generated*
• Data Packet: `viper_packet.json`
• Trade Plan: `trade_plan.md`
• Review Scores: `review_scores.json`

🔗 Check your local files for full analysis details.
"""
        
        return send_telegram_message(message)
        
    except Exception as e:
        print(f"❌ Error creating Telegram summary: {e}")
        return False


# --- 1. DATA ENGINEERING MODULE ---

def calculate_ema(data, length):
    """Calculate Exponential Moving Average."""
    return data.ewm(span=length, adjust=False).mean()

def calculate_rsi(data, length=14):
    """Calculate Relative Strength Index."""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/length, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/length, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_atr(high, low, close, length=14):
    """Calculate Average True Range."""
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.ewm(alpha=1/length, adjust=False).mean()

def get_market_data(symbol, period, interval):
    """Fetches and cleans historical market data."""
    print(f"Fetching {interval} data for {symbol}...")
    data = yf.download(tickers=symbol, period=period, interval=interval, progress=False, auto_adjust=True)
    
    # Handle MultiIndex columns (common in newer yfinance versions)
    if isinstance(data.columns, pd.MultiIndex):
        # Flatten MultiIndex columns by taking the first level (column name)
        data.columns = data.columns.get_level_values(0)
    
    # Ensure we have the required columns with proper names
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    available_columns = list(data.columns)
    
    # Check if we have the required columns
    missing_columns = [col for col in required_columns if col not in available_columns]
    if missing_columns:
        print(f"Warning: Missing columns: {missing_columns}")
        
        # Try to map common variations
        if 'Close' not in available_columns and 'Adj Close' in available_columns:
            data = data.rename(columns={'Adj Close': 'Close'})
        
        # If no volume data, create a dummy column
        if 'Volume' not in available_columns:
            data['Volume'] = 0
    
    return data.dropna()

def analyze_timeframe(df, timeframe_name):
    """Analyzes a single timeframe DataFrame to extract key metrics."""
    if df.empty or len(df) < 200:
        print(f"Warning: Insufficient data for {timeframe_name} analysis.")
        return None

    df['EMA_50'] = calculate_ema(df['Close'], 50)
    df['EMA_200'] = calculate_ema(df['Close'], 200)
    df['RSI_14'] = calculate_rsi(df['Close'], 14)

    last_row = df.iloc[-1]
    close = last_row['Close']

    trend = "Consolidating"
    if close > last_row['EMA_50'] and last_row['EMA_50'] > last_row['EMA_200']:
        trend = "Bullish"
    elif close < last_row['EMA_50'] and last_row['EMA_50'] < last_row['EMA_200']:
        trend = "Bearish"

    ema_status = {
        "50_ema": "Price is Above" if close > last_row['EMA_50'] else "Price is Below",
        "200_ema": "Price is Above" if close > last_row['EMA_200'] else "Price is Below"
    }
    
    recent_data = df.tail(180)
    high_peaks, _ = find_peaks(recent_data['High'], distance=5, prominence=0.001)
    low_peaks, _ = find_peaks(-recent_data['Low'], distance=5, prominence=0.001)

    resistance = sorted([round(p, 4) for p in recent_data['High'].iloc[high_peaks].nlargest(3).tolist()])
    support = sorted([round(p, 4) for p in recent_data['Low'].iloc[low_peaks].nsmallest(3).tolist()])

    return {
        "trendDirection": trend,
        "keySupportLevels": support,
        "keyResistanceLevels": resistance,
        "emaStatus": ema_status,
        "rsi_14": round(last_row['RSI_14'], 2) if pd.notna(last_row['RSI_14']) else None
    }

def get_intermarket_analysis(symbols_dict):
    """Provides trend analysis for related markets."""
    analysis = {}
    data = yf.download(list(symbols_dict.values()), period="6mo", interval="1d", progress=False, auto_adjust=True)['Close']
    for name, symbol in symbols_dict.items():
        if symbol in data:
            df = data[symbol].dropna().to_frame()
            df.columns = ['Close']
            df['EMA_50'] = calculate_ema(df['Close'], 50)
            if not df.empty:
                last_close = df.iloc[-1]['Close']
                last_ema = df.iloc[-1]['EMA_50']
                analysis[f"{name}_trend"] = "Bullish" if last_close > last_ema else "Bearish"
    return analysis

def get_economic_calendar():
    """Scrapes Forex Factory for relevant economic events."""
    print("Fetching economic calendar...")
    try:
        scraper = cloudscraper.create_scraper()
        url = 'https://www.forexfactory.com/calendar'
        response = scraper.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='calendar__table')
        
        events = []
        current_date = "Unknown"
        today_str = datetime.now(timezone.utc).strftime("%a %b %d").lstrip("0")

        for row in table.find_all('tr', class_='calendar__row'):
            if 'calendar__row--day-breaker' in row.get('class', []):
                current_date = row.find('td').text.strip()
                continue
            
            if today_str not in current_date:
                continue

            currency_cell = row.find('td', class_='calendar__currency')
            if not currency_cell or currency_cell.text.strip() not in ['EUR', 'USD']:
                continue

            impact_span = row.find('span', title=lambda t: t and "Impact" in t)
            if not impact_span or any(x in impact_span.get('title', '') for x in ['Holiday', 'Low']):
                continue

            events.append({
                "eventName": row.find('td', class_='calendar__event').text.strip(),
                "timeUTC": row.find('td', class_='calendar__time').text.strip(),
                "impact": "High" if "High" in impact_span['title'] else "Medium",
                "forecast": row.find('td', class_='calendar__forecast').text.strip(),
                "previous": row.find('td', class_='calendar__previous').text.strip(),
                "potentialDeviationScenario": "Awaiting LLM analysis."
            })
        print(f"Found {len(events)} relevant events for today.")
        return events
    except Exception as e:
        print(f"Could not fetch economic calendar: {e}")
        return []

def generate_viper_packet():
    """Orchestrates the creation of the structured data packet."""
    print("\n--- STAGE 1: GENERATING VIPER DATA PACKET ---")
    eurusd_d1 = get_market_data(SYMBOLS["EURUSD"], "2y", "1d")
    eurusd_d1['ATR_14'] = calculate_atr(eurusd_d1['High'], eurusd_d1['Low'], eurusd_d1['Close'], 14)
    
    eurusd_h1_raw = get_market_data(SYMBOLS["EURUSD"], "120d", "1h")
    
    # Ensure we have the required columns before resampling
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in eurusd_h1_raw.columns for col in required_cols):
        print(f"Error: Missing required columns for resampling. Available: {list(eurusd_h1_raw.columns)}")
        # Try to use only available columns
        available_cols = [col for col in required_cols if col in eurusd_h1_raw.columns]
        if len(available_cols) >= 4:  # Need at least Open, High, Low, Close
            agg_dict = {}
            if 'Open' in available_cols:
                agg_dict['Open'] = 'first'
            if 'High' in available_cols:
                agg_dict['High'] = 'max'
            if 'Low' in available_cols:
                agg_dict['Low'] = 'min'
            if 'Close' in available_cols:
                agg_dict['Close'] = 'last'
            if 'Volume' in available_cols:
                agg_dict['Volume'] = 'sum'
            
            eurusd_h4 = eurusd_h1_raw.resample('4h').agg(agg_dict).dropna()
        else:
            raise ValueError(f"Insufficient columns for resampling. Need at least 4 of {required_cols}, got {available_cols}")
    else:
        eurusd_h4 = eurusd_h1_raw.resample('4h').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
    
    multi_tf = {
        "Daily": analyze_timeframe(eurusd_d1.copy(), "Daily"),
        "H4": analyze_timeframe(eurusd_h4.copy(), "H4"),
        "H1": analyze_timeframe(eurusd_h1_raw.tail(720).copy(), "H1") # Use last 30 days of 1H data
    }
    
    last_atr = eurusd_d1['ATR_14'].iloc[-1]
    last_close = eurusd_d1.iloc[-1]['Close']
    volatility = {
        "atr_14_daily_pips": int(last_atr * 10000),
        "predictedDailyRange": [round(last_close - last_atr, 4), round(last_close + last_atr, 4)]
    }

    packet = {
        "marketSnapshot": {"pair": "EURUSD", "currentPrice": last_close, "currentTimeUTC": datetime.now(timezone.utc).isoformat()},
        "multiTimeframeAnalysis": multi_tf,
        "volatilityMetrics": volatility,
        "fundamentalAnalysis": {"keyEconomicEvents": get_economic_calendar()},
        "intermarketConfluence": get_intermarket_analysis({k: v for k, v in SYMBOLS.items() if k != 'EURUSD'})
    }

    # Ensure both the main trading_session directory and the date subdirectory exist
    OUTPUT_DIR.mkdir(exist_ok=True)
    DATE_OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"📁 Creating date-based folder: {DATE_OUTPUT_DIR}")
    
    with open(DATA_PACKET_PATH, 'w') as f:
        json.dump(packet, f, indent=2)
    print(f"✅ Viper Data Packet saved to: {DATA_PACKET_PATH}")
    return packet


# --- 2. LLM ORCHESTRATION MODULE ---

PLANNER_SYSTEM_PROMPT = """
**Persona:** You are "Viper," a lead trader and strategist for a high-frequency quant fund. You operate with extreme precision and a zero-tolerance policy for ambiguity. Your analysis blends quantitative data, market structure, and fundamental narratives into a coherent, actionable playbook. You think in terms of probabilities, asymmetry, and if/then scenarios. Your tone is direct, concise, and professional.
**Core Task:** Analyze the provided structured market data (JSON). Synthesize this data into a comprehensive, robust, and actionable **intraday trading playbook for EURUSD**. The output must be a professional markdown document designed for execution by a junior trader who needs absolute clarity.
**Guiding Principles:**
- **The "Why" is Mandatory:** Every key level or zone mentioned **must** be justified (e.g., "Daily Resistance," "4H Order Block").
- **Asymmetry is Everything:** All primary trade ideas must have a calculated Risk/Reward (R:R) ratio of **2.5:1 or greater**.
- **If/Then Logic:** This is not a static prediction. Frame the plan as a series of decisions. "If price does X, then we execute Y."
- **Clarity Over Clutter:** Use precise language.
---
### **1. Daily Market Thesis & Narrative**
- **Overarching Bias:** State your primary directional bias.
- **Primary Narrative:** In 1-2 sentences, synthesize the fundamental and technical picture.
- **Decisive Catalyst:** Identify the day's key event/data release and its expected impact.
---
### **2. The Battlefield: Key Levels & Zones**
- **Upper Bound / Major Resistance:** Price (`X.XXXX`). **Justification:**
- **Lower Bound / Major Support:** Price (`X.XXXX`). **Justification:**
- **Bull/Bear Pivot ("Line in the Sand"):** Price (`X.XXXX`). **Justification:**
- **Primary Value Zone:** A **10-15 pip range** (`X.XXXX - X.XXXX`). **Justification:**
---
### **3. Plan A: The Primary Trade Idea**
- **Trade Objective:** Clear goal (e.g., **Long from Value Zone after liquidity grab**).
- **Entry Protocol:** Condition and Trigger (e.g., "Price must pull back to Value Zone, execute on 15m bullish engulfing candle").
- **Stop Loss (SL):** Price (`X.XXXX`). **Justification:**
- **Take Profit 1 (TP1):** Price (`X.XXXX`). **Justification:**
- **Take Profit 2 (TP2):** Price (`X.XXXX`). **Justification:**
- **Risk/Reward (to TP2):** Calculated ratio.
---
### **4. Plan B: The Contingency Trade Idea**
- **Trade Objective:** Clear goal (e.g., **Short on a failed breakout of Major Resistance**).
- **Entry Protocol:** Condition and Trigger.
- **Stop Loss (SL):** Price (`X.XXXX`). **Justification:**
- **Take Profit (TP):** Price (`X.XXXX`). **Justification:**
- **Risk/Reward:** Calculated ratio.
---
### **5. Execution & Risk Protocols**
- **Capital at Risk:** "Risk **0.75%** on Plan A. Risk **0.5%** on Plan B. Maximum daily loss is **1.25%**."
- **Active Trade Management:** "At TP1, close **50%** and move SL to **breakeven**."
- **Execution Mandate:** A final, direct order.
"""

REVIEWER_SYSTEM_PROMPT = """
You are an expert system designed to emulate a grizzled, veteran foreign exchange (FX) trader. Your call sign is "Viper." Your primary job is to protect capital. You are skeptical by nature. Your sole function is to analyze a trading plan and its underlying data, then assign two critical scores.
---
## Your Task
Analyze the user-provided trade plan AND the original data packet. Check for inconsistencies, flawed logic, or overly optimistic assumptions. Return a JSON object containing two scores.
### 1. Plan Quality Score (The "Science" 🧪)
Is the plan a **logical conclusion** from the data? Does it adhere to its own rules (R:R > 2.5)? Are the justifications for levels found within the data packet?
### 2. Confidence Score (The "Art" 🎨)
Does the plan reflect the **overall feel** of the data? Does it prudently account for conflicting signals (e.g., bullish Daily but bearish H1 divergence)?
---
## Rules & Output Format
1.  **BE CRITICAL:** The plan was made by another AI. Your job is to find its flaws.
2.  **NO CONVERSATION:** Your response must **only** be the JSON object.
3.  **STRICT JSON OUTPUT:**
{
  "planQualityScore": { "score": <int>, "justification": "<str>" },
  "confidenceScore": { "score": <int>, "justification": "<str>" }
}
"""

def call_llm(system_prompt: str, user_prompt: str) -> str:
    """A simple wrapper for calling the Gemini model."""
    print("...")
    try:
        model = genai.GenerativeModel(MODEL_NAME, system_instruction=system_prompt)
        response = model.generate_content(user_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"An error occurred during the LLM call: {e}")
        return ""

def run_viper_coil(viper_packet):
    """Executes the Planner -> Reviewer LLM pipeline."""
    
    # --- Step 2: Engage the Planner ---
    print("\n--- STAGE 2: ENGAGING PLANNER LLM ---")
    planner_user_prompt = f"Here is the latest data packet. Generate the trading playbook.\n\n```json\n{json.dumps(viper_packet, indent=2)}\n```"
    trade_plan_md = call_llm(PLANNER_SYSTEM_PROMPT, planner_user_prompt)
    
    if not trade_plan_md:
        print("❌ Planner failed to generate a plan. Aborting.")
        return

    with open(PLAN_OUTPUT_PATH, 'w') as f:
        f.write(trade_plan_md)
    print(f"✅ Planner finished. Trade plan saved to: {PLAN_OUTPUT_PATH.name}")
    print("\n--- GENERATED PLAN ---\n")
    print(trade_plan_md)
    print("\n----------------------\n")

    # --- Step 3: Engage the Reviewer ---
    print("\n--- STAGE 3: ENGAGING REVIEWER LLM ---")
    reviewer_user_prompt = f"""
    Here is the original data packet and the proposed trade plan. Analyze both and provide your scores.

    ### ORIGINAL DATA PACKET
    ```json
    {json.dumps(viper_packet, indent=2)}
    ```

    ### PROPOSED TRADE PLAN
    ```markdown
    {trade_plan_md}
    ```
    """
    review_output_raw = call_llm(REVIEWER_SYSTEM_PROMPT, reviewer_user_prompt)

    # --- Step 4: Parse Review and Make Final Decision ---
    try:
        if review_output_raw.startswith("```json"):
            review_output_raw = review_output_raw[7:-3].strip()
        review_scores = json.loads(review_output_raw)
        
        with open(REVIEW_OUTPUT_PATH, 'w') as f:
            json.dump(review_scores, f, indent=2)
        print(f"✅ Scores parsed and saved to: {REVIEW_OUTPUT_PATH.name}")

        quality = review_scores['planQualityScore']['score']
        confidence = review_scores['confidenceScore']['score']
        
        print("\n--- FINAL REVIEW & DECISION ---")
        print(f"🔬 Plan Quality: {quality}/10")
        print(f"   Justification: {review_scores['planQualityScore']['justification']}")
        print(f"🎨 Confidence:   {confidence}/10")
        print(f"   Justification: {review_scores['confidenceScore']['justification']}")
        print("-" * 30)

        if quality >= 6 and confidence >= 6:
            print("🟢 DECISION: GO FOR EXECUTION. Plan is solid and conviction is high.")
        elif quality >= 6 and confidence < 6:
            print("🟡 DECISION: WAIT AND SEE. Plan is solid, but market feel is off. Consider reduced size or wait for confirmation.")
        else:
            print("🔴 DECISION: NO-GO. DISCARD PLAN. Quality or Confidence is too low.")
        print("-" * 50)

    except (json.JSONDecodeError, KeyError) as e:
        print(f"❌ ERROR: Reviewer returned invalid JSON or unexpected structure: {e}")
        print("--- Raw Reviewer Output ---")
        print(review_output_raw)


# --- 3. MAIN EXECUTION BLOCK ---

if __name__ == "__main__":
    print(f"📁 Output will be saved to: {DATE_OUTPUT_DIR}")
    print(f"📅 Date: {CURRENT_DATE}")
    print("-" * 50)
    
    # STAGE 1: Generate the data packet
    data_packet = generate_viper_packet()
    
    # STAGE 2 & 3: Run the Planner and Reviewer pipeline
    if data_packet:
        run_viper_coil(data_packet)
        send_trading_summary(data_packet, PLAN_OUTPUT_PATH, REVIEW_OUTPUT_PATH)
    else:
        print("❌ Could not generate data packet. Halting execution.")