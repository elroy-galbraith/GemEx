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
from prompts import PLANNER_SYSTEM_PROMPT, REVIEWER_SYSTEM_PROMPT
load_dotenv()

# --- 0. MASTER CONFIGURATION ---

# --- API and Model Setup ---
# To run locally, set your API key as an environment variable:
# export GOOGLE_API_KEY="your_api_key_here"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") #, userdata.get('GEMINI_API_KEY'))

# Only configure Gemini if we're actually running the main analysis
# This allows testing modules to import without requiring the API key
def configure_gemini():
    """Configure Gemini API - only call this when actually needed."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found. Please set it as an environment variable.")
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-1.5-pro-latest")

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

def escape_markdown(text):
    """Escape special Markdown characters to prevent parsing errors."""
    if not text:
        return text
    
    # Characters that need escaping in Markdown
    escape_chars = ['*', '_', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def send_telegram_message(message, parse_mode="Markdown"):
    """Send a message to Telegram via bot API."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.")
        return False
    
    # Split long messages into chunks (Telegram limit is 4096 characters)
    max_length = 4000  # Leave some buffer for safety
    
    if len(message) <= max_length:
        # Single message - send normally
        return _send_single_message(message, parse_mode)
    else:
        # Split into multiple messages
        return _send_split_messages(message, parse_mode, max_length)

def _send_single_message(message, parse_mode):
    """Send a single message to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # If Markdown parsing fails, fall back to plain text
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
        if parse_mode == "Markdown":
            print(f"❌ Markdown parsing failed, retrying with plain text: {e}")
            # Retry without parse_mode
            data_plain = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message
            }
            try:
                response = requests.post(url, data=data_plain, timeout=10)
                response.raise_for_status()
                print("✅ Telegram message sent successfully (plain text)")
                return True
            except requests.exceptions.RequestException as e2:
                print(f"❌ Failed to send Telegram message (plain text): {e2}")
                return False
        else:
            print(f"❌ Failed to send Telegram message: {e}")
            return False

def _send_split_messages(message, parse_mode, max_length):
    """Split and send long messages in chunks."""
    print(f"📤 Splitting long message into chunks (total length: {len(message)} chars)")
    
    # Split by lines to avoid breaking in the middle of content
    lines = message.split('\n')
    chunks = []
    current_chunk = ""
    
    for line in lines:
        # If adding this line would exceed limit, start new chunk
        if len(current_chunk) + len(line) + 1 > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line
        else:
            current_chunk += '\n' + line if current_chunk else line
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # Send all chunks
    success_count = 0
    for i, chunk in enumerate(chunks, 1):
        chunk_header = f"📄 *Part {i} of {len(chunks)}*\n\n"
        full_chunk = chunk_header + chunk
        
        if _send_single_message(full_chunk, parse_mode):
            success_count += 1
        else:
            print(f"❌ Failed to send chunk {i}")
    
    print(f"✅ Sent {success_count}/{len(chunks)} message chunks successfully")
    return success_count == len(chunks)

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
        
        # Create summary message with safer formatting
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

📋 *Complete Trade Plan*
```
{trade_plan}
```
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
    """
    Correctly scrapes the Forex Factory economic calendar by handling
    different row types and propagating the date correctly.
    """
    print("Fetching economic calendar...")
    try:
        scraper = cloudscraper.create_scraper()
        url = 'https://www.forexfactory.com/calendar'
        response = scraper.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='calendar__table')
        
        if not table:
            print("Could not find the calendar table.")
            return []

        calendar_data = []
        # Find all rows, including day-breakers and event rows
        rows = table.find_all('tr', class_='calendar__row')

        # This variable will hold the date as we iterate through the rows
        current_date = "Unknown"

        # Use Linux-friendly date formatting (GitHub Actions runs on Linux by default)
        today_str = datetime.now(timezone.utc).strftime('%a %b %-d').lstrip()
        print(f"Filtering for today's date: '{today_str}'")

        for row in rows:
            # --- 1. Check if the row is a "day-breaker" ---
            # These rows only contain the date (e.g., "Tue Aug 12")
            if 'calendar__row--day-breaker' in row.get('class', []):
                date_cell = row.find('td', class_='calendar__cell')
                if date_cell:
                    # Update the current date and skip to the next row
                    current_date = date_cell.text.strip()
                continue

            # --- 2. If it's not a day-breaker, try to parse it as an event row ---
            # We check for a currency cell as a reliable sign of an event row
            currency_cell = row.find('td', class_='calendar__currency')
            if not currency_cell:
                continue # Skip rows that are not events (e.g., empty day rows)

            # Only process events for today and for EUR/USD currencies
            if current_date.strip() != today_str or currency_cell.text.strip() not in ['EUR', 'USD']:
                continue

            # --- 3. Extract data from the event row safely ---
            # Using .find() and then checking existence avoids errors
            time_cell = row.find('td', class_='calendar__time')
            impact_cell = row.find('td', class_='calendar__impact')
            event_cell = row.find('td', class_='calendar__event')
            forecast_cell = row.find('td', class_='calendar__forecast')
            previous_cell = row.find('td', class_='calendar__previous')

            # Safely get text, providing a default empty string if a cell is missing
            time = time_cell.text.strip() if time_cell else ''
            currency = currency_cell.text.strip()

            # Improved impact extraction
            impact = 'No Impact'  # Default value
            if impact_cell:
                # Look specifically for span with class 'icon' and title attribute
                impact_span = impact_cell.find('span', class_='icon')
                if impact_span and impact_span.get('title'):
                    impact = impact_span['title']
                else:
                    # Fallback: look for any span with title attribute
                    title_spans = impact_cell.find_all('span', title=True)
                    if title_spans:
                        impact = title_spans[0]['title']
                    else:
                        # Last resort: check for class-based impact indication
                        if impact_cell.find('span', class_=lambda x: x and 'ff-impact-red' in str(x)):
                            impact = 'High Impact Expected'
                        elif impact_cell.find('span', class_=lambda x: x and 'ff-impact-ora' in str(x)):
                            impact = 'Medium Impact Expected'
                        elif impact_cell.find('span', class_=lambda x: x and 'ff-impact-yel' in str(x)):
                            impact = 'Low Impact Expected'

            # Only include high impact events
            if impact != 'High Impact Expected':
                continue

            event = event_cell.text.strip() if event_cell else 'N/A'
            forecast = forecast_cell.text.strip() if forecast_cell else ''
            previous = previous_cell.text.strip() if previous_cell else ''

            calendar_data.append({
                "eventName": event,
                "timeUTC": time,
                "impact": "High",
                "forecast": forecast,
                "previous": previous,
                "potentialDeviationScenario": "Awaiting LLM analysis."
            })

        print(f"Found {len(calendar_data)} high impact events for today.")
        return calendar_data
    except Exception as e:
        print(f"Could not fetch economic calendar: {e}")
        return []

def download_previous_session_artifacts():
    """Download previous session data from GitHub Actions artifacts or remote storage."""
    print("Attempting to download previous session data...")
    
    # Check if we're running in GitHub Actions
    if os.environ.get('GITHUB_ACTIONS'):
        print("Running in GitHub Actions - attempting to download previous artifacts...")
        return download_from_github_artifacts()
    else:
        print("Running locally - checking local files...")
        return load_local_previous_session()

def download_from_github_artifacts():
    """Download previous session data from GitHub Actions artifacts."""
    try:
        import requests
        import zipfile
        import tempfile
        
        # Get GitHub token and repository info
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            print("Warning: No GITHUB_TOKEN found. Cannot download previous artifacts.")
            return None
            
        # Get repository info
        github_repo = os.environ.get('GITHUB_REPOSITORY')
        if not github_repo:
            print("Warning: No GITHUB_REPOSITORY found.")
            return None
        
        # Get yesterday's date
        from datetime import timedelta
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y_%m_%d")
        
        # Try to find recent artifacts (last 7 days)
        headers = {'Authorization': f'token {github_token}'}
        artifacts_url = f"https://api.github.com/repos/{github_repo}/actions/artifacts"
        
        response = requests.get(artifacts_url, headers=headers)
        if response.status_code != 200:
            print(f"Warning: Could not fetch artifacts list: {response.status_code}")
            if response.status_code == 403:
                print("This might be due to insufficient permissions. The GITHUB_TOKEN may not have access to artifacts.")
            return None
            
        artifacts = response.json().get('artifacts', [])
        
        # Find the most recent trading session artifact
        trading_artifacts = [a for a in artifacts if a['name'].startswith('trading-session-')]
        if not trading_artifacts:
            print("No previous trading session artifacts found.")
            return None
            
        # Get the most recent artifact
        latest_artifact = max(trading_artifacts, key=lambda x: x['created_at'])
        print(f"Found previous artifact: {latest_artifact['name']}")
        
        # Download the artifact
        download_url = latest_artifact['archive_download_url']
        print(f"Downloading artifact from: {download_url}")
        download_response = requests.get(download_url, headers=headers)
        
        if download_response.status_code != 200:
            print(f"Warning: Could not download artifact: {download_response.status_code}")
            print(f"Response content: {download_response.text[:200]}")
            return None
        
        print(f"✅ Successfully downloaded artifact ({len(download_response.content)} bytes)")
        
        # Extract the zip file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            tmp_file.write(download_response.content)
            tmp_file_path = tmp_file.name
        
        with tempfile.TemporaryDirectory() as extract_dir:
            print(f"Extracting to: {extract_dir}")
            with zipfile.ZipFile(tmp_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # List extracted contents for debugging
            extract_path = Path(extract_dir)
            print(f"Extracted contents: {list(extract_path.iterdir())}")
            
            # Look for trading_session directory first (expected structure)
            trading_session_path = extract_path / "trading_session"
            if trading_session_path.exists():
                print(f"Found trading_session directory: {list(trading_session_path.iterdir())}")
                
                # Look for yesterday's session data
                yesterday_dir = trading_session_path / yesterday
                if yesterday_dir.exists():
                    print(f"Found yesterday's session: {yesterday_dir}")
                    return load_session_data_from_path(yesterday_dir)
                else:
                    # If yesterday's data isn't available, try to find the most recent session
                    session_dirs = list(trading_session_path.glob("20*"))
                    if session_dirs:
                        latest_session = max(session_dirs, key=lambda x: x.name)
                        print(f"Using most recent session data: {latest_session.name}")
                        return load_session_data_from_path(latest_session)
                    else:
                        print("No session directories found in trading_session")
            else:
                print("No trading_session directory found in artifact")
                
                # Check if date folders are directly in the root (alternative structure)
                session_dirs = list(extract_path.glob("20*"))
                if session_dirs:
                    print(f"Found date directories directly in artifact: {[d.name for d in session_dirs]}")
                    
                    # Look for yesterday's session data
                    yesterday_dir = extract_path / yesterday
                    if yesterday_dir.exists():
                        print(f"Found yesterday's session: {yesterday_dir}")
                        return load_session_data_from_path(yesterday_dir)
                    else:
                        # Use the most recent session
                        latest_session = max(session_dirs, key=lambda x: x.name)
                        print(f"Using most recent session data: {latest_session.name}")
                        return load_session_data_from_path(latest_session)
                else:
                    print("No date directories found in artifact")
        
        # Clean up
        os.unlink(tmp_file_path)
        
    except Exception as e:
        print(f"Warning: Could not download previous artifacts: {e}")
        return None

def load_local_previous_session():
    """Load previous session data from local files."""
    from datetime import timedelta
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y_%m_%d")
    yesterday_dir = OUTPUT_DIR / yesterday
    
    if yesterday_dir.exists():
        return load_session_data_from_path(yesterday_dir)
    return None

def load_session_data_from_path(session_path):
    """Load session data from a specific path."""
    try:
        print(f"Loading session data from: {session_path}")
        print(f"Session path exists: {session_path.exists()}")
        
        if not session_path.exists():
            print(f"Session path does not exist: {session_path}")
            return None
        
        # List contents of the session directory
        session_contents = list(session_path.iterdir())
        print(f"Session directory contents: {[f.name for f in session_contents]}")
        
        previous_context = {
            "previousSessionDate": session_path.name,
            "previousPlanExists": True,
            "previousMarketSnapshot": None,
            "previousKeyLevels": None,
            "previousPlanOutcome": None,
            "previousPlanContent": None
        }
        
        # Load previous viper packet
        prev_packet_path = session_path / "viper_packet.json"
        print(f"Looking for viper_packet.json: {prev_packet_path}")
        print(f"viper_packet.json exists: {prev_packet_path.exists()}")
        
        if prev_packet_path.exists():
            with open(prev_packet_path, 'r') as f:
                prev_packet = json.load(f)
            
            previous_context["previousMarketSnapshot"] = prev_packet.get("marketSnapshot")
            previous_context["previousKeyLevels"] = {
                "support": prev_packet.get("multiTimeframeAnalysis", {}).get("Daily", {}).get("keySupportLevels", []),
                "resistance": prev_packet.get("multiTimeframeAnalysis", {}).get("Daily", {}).get("keyResistanceLevels", [])
            }
            print("✅ Loaded viper_packet.json")
        else:
            print("⚠️  viper_packet.json not found")
        
        # Load previous trade plan
        prev_plan_path = session_path / "trade_plan.md"
        print(f"Looking for trade_plan.md: {prev_plan_path}")
        print(f"trade_plan.md exists: {prev_plan_path.exists()}")
        
        if prev_plan_path.exists():
            with open(prev_plan_path, 'r') as f:
                previous_context["previousPlanContent"] = f.read()
            print("✅ Loaded trade_plan.md")
        else:
            print("⚠️  trade_plan.md not found")
        
        # Load previous review scores
        prev_review_path = session_path / "review_scores.json"
        print(f"Looking for review_scores.json: {prev_review_path}")
        print(f"review_scores.json exists: {prev_review_path.exists()}")
        
        if prev_review_path.exists():
            with open(prev_review_path, 'r') as f:
                previous_context["previousPlanOutcome"] = json.load(f)
            print("✅ Loaded review_scores.json")
        else:
            print("⚠️  review_scores.json not found")
        
        print(f"✅ Successfully loaded previous session data from {session_path.name}")
        return previous_context
        
    except Exception as e:
        print(f"Warning: Could not load session data from {session_path}: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_fallback_previous_context():
    """Create a fallback context when no previous session data is available."""
    from datetime import timedelta
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y_%m_%d")
    
    return {
        "previousSessionDate": yesterday,
        "previousPlanExists": False,
        "previousMarketSnapshot": None,
        "previousKeyLevels": None,
        "previousPlanOutcome": None,
        "marketEvolution": None,
        "fallbackMode": True
    }

def get_previous_session_analysis():
    """Analyzes the previous trading session to provide context for current analysis."""
    print("Analyzing previous session context...")
    
    # Try to get previous session data
    previous_context = download_previous_session_artifacts()
    
    if previous_context is None:
        # Fallback: create empty context
        previous_context = create_fallback_previous_context()
        print("⚠️  No previous session data available - starting fresh analysis")
        print("💡 This is normal for the first run or when no recent artifacts exist")
    
    return previous_context

def analyze_market_thesis_evolution(previous_context):
    """Analyzes how the market thesis has evolved from previous sessions."""
    if not previous_context.get("previousPlanExists"):
        return {"thesisEvolution": "No previous session data available"}
    
    thesis_evolution = {
        "previousThesis": None,
        "thesisContinuity": None,
        "thesisModification": None,
        "invalidationRisk": None
    }
    
    try:
        # Extract previous thesis from previous plan content
        if previous_context.get("previousPlanContent"):
            prev_plan = previous_context["previousPlanContent"]
            
            # Look for thesis indicators in the previous plan
            if prev_plan and isinstance(prev_plan, str) and "Overarching Bias:" in prev_plan:
                # Extract the bias from previous plan
                lines = prev_plan.split('\n')
                for i, line in enumerate(lines):
                    if "Overarching Bias:" in line:
                        thesis_evolution["previousThesis"] = line.split("Overarching Bias:")[-1].strip()
                        break
            
            # Analyze thesis continuity
            if "Bullish" in thesis_evolution.get("previousThesis", ""):
                thesis_evolution["thesisContinuity"] = "Bullish bias from previous session"
            elif "Bearish" in thesis_evolution.get("previousThesis", ""):
                thesis_evolution["thesisContinuity"] = "Bearish bias from previous session"
            else:
                thesis_evolution["thesisContinuity"] = "Neutral/Range-bound bias from previous session"
        
        # Check if previous plan had high quality scores (indicating strong thesis)
        if previous_context.get("previousPlanOutcome"):
            prev_scores = previous_context["previousPlanOutcome"]
            quality_score = prev_scores.get("planQualityScore", {}).get("score", 0)
            confidence_score = prev_scores.get("confidenceScore", {}).get("score", 0)
            
            if quality_score >= 7 and confidence_score >= 7:
                thesis_evolution["thesisModification"] = "Previous thesis was strong - consider continuation"
            elif quality_score < 5 or confidence_score < 5:
                thesis_evolution["thesisModification"] = "Previous thesis was weak - consider revision"
            else:
                thesis_evolution["thesisModification"] = "Previous thesis was moderate - monitor for changes"
        
    except Exception as e:
        print(f"Warning: Could not analyze thesis evolution: {e}")
        thesis_evolution["error"] = str(e)
    
    return thesis_evolution

def analyze_market_evolution(current_data, previous_context):
    """Analyzes how the market has evolved since the previous session."""
    if not previous_context.get("previousPlanExists"):
        return {"evolution": "No previous session data available"}
    
    evolution = {
        "priceMovement": None,
        "levelBreaks": [],
        "trendContinuity": None,
        "volatilityChange": None,
        "keyObservations": []
    }
    
    try:
        # Compare current vs previous price
        current_price = current_data["marketSnapshot"]["currentPrice"]
        prev_price = previous_context["previousMarketSnapshot"]["currentPrice"]
        price_change = current_price - prev_price
        price_change_pips = round(price_change * 10000, 1)
        
        evolution["priceMovement"] = {
            "change": price_change,
            "changePips": price_change_pips,
            "direction": "Bullish" if price_change > 0 else "Bearish" if price_change < 0 else "Neutral"
        }
        
        # Check for key level breaks
        prev_support = previous_context["previousKeyLevels"]["support"]
        prev_resistance = previous_context["previousKeyLevels"]["resistance"]
        
        for level in prev_support:
            if current_price < level:
                evolution["levelBreaks"].append(f"Support broken: {level}")
        
        for level in prev_resistance:
            if current_price > level:
                evolution["levelBreaks"].append(f"Resistance broken: {level}")
        
        # Analyze trend continuity
        current_trend = current_data["multiTimeframeAnalysis"]["Daily"]["trendDirection"]
        evolution["trendContinuity"] = current_trend
        
        # Generate key observations
        if abs(price_change_pips) > 50:
            evolution["keyObservations"].append(f"Significant price movement: {price_change_pips} pips")
        
        if evolution["levelBreaks"]:
            evolution["keyObservations"].append(f"Key levels broken: {len(evolution['levelBreaks'])}")
        
        if current_trend != "Consolidating":
            evolution["keyObservations"].append(f"Clear directional bias: {current_trend}")
            
    except Exception as e:
        print(f"Warning: Could not analyze market evolution: {e}")
        evolution["error"] = str(e)
    
    return evolution

def generate_viper_packet():
    """Orchestrates the creation of the structured data packet."""
    print("\n--- STAGE 1: GENERATING VIPER DATA PACKET ---")
    
    # Get previous session context
    previous_context = get_previous_session_analysis()
    
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

    # Create the base packet
    packet = {
        "marketSnapshot": {"pair": "EURUSD", "currentPrice": last_close, "currentTimeUTC": datetime.now(timezone.utc).isoformat()},
        "multiTimeframeAnalysis": multi_tf,
        "volatilityMetrics": volatility,
        "fundamentalAnalysis": {"keyEconomicEvents": get_economic_calendar()},
        "intermarketConfluence": get_intermarket_analysis({k: v for k, v in SYMBOLS.items() if k != 'EURUSD'})
    }
    
    # Add temporal analysis
    market_evolution = analyze_market_evolution(packet, previous_context)
    thesis_evolution = analyze_market_thesis_evolution(previous_context)
    packet["temporalAnalysis"] = {
        "previousSessionContext": previous_context,
        "marketEvolution": market_evolution,
        "thesisEvolution": thesis_evolution
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

def call_llm(system_prompt: str, user_prompt: str) -> str:
    """A simple wrapper for calling the Gemini model."""
    print("...")
    try:
        model = configure_gemini()
        response = model.generate_content(user_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"An error occurred during the LLM call: {e}")
        return ""

def clean_json_output(raw_output: str) -> str:
    """Clean and extract JSON from LLM output."""
    if not raw_output:
        return ""
    
    # Remove markdown code blocks
    cleaned = raw_output.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    
    # Remove any leading/trailing whitespace
    cleaned = cleaned.strip()
    
    # Try to find JSON object boundaries
    start_idx = cleaned.find('{')
    end_idx = cleaned.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        cleaned = cleaned[start_idx:end_idx + 1]
    else:
        # If no JSON found, only convert when this looks like a reviewer analysis
        if is_reviewer_analysis_text(raw_output):
            return convert_analysis_to_json(raw_output)
        # Otherwise, return original text unchanged
        return raw_output
    
    return cleaned

def is_reviewer_analysis_text(analysis_text: str) -> bool:
    """Heuristically detect if text is the Reviewer analysis (markdown prose with scores).

    We only attempt markdown->JSON conversion when these cues are present to avoid
    converting arbitrary non-JSON strings.
    """
    if not analysis_text:
        return False
    lowered = analysis_text.lower()
    cues = [
        "analysis of the trade plan",
        "scoring (out of 5)",
        "market analysis:",
        "strategy development:",
        "risk management:",
        "overall:",
        "strengths:",
        "weaknesses:",
        "suggestions for improvement:"
    ]
    return any(cue in lowered for cue in cues)

def convert_analysis_to_json(analysis_text: str) -> str:
    """Convert markdown analysis text to JSON format."""
    try:
        # Extract scores from the analysis text
        import re
        
        # Look for multiple possible scoring patterns the reviewer may use
        # Pattern A: Market Analysis, Strategy Development, Risk Management, Overall (x/5 or x/10)
        def find_score(pattern: str) -> tuple[float | None, float | None]:
            m = re.search(pattern, analysis_text, re.IGNORECASE)
            if not m:
                return None, None
            num = float(m.group(1))
            denom = float(m.group(2)) if m.group(2) else 10.0
            return num, denom

        market_val, market_den = find_score(r'(?:\*?\*?Market Analysis:\*?\*?|Market Analysis:)\s*(\d+(?:\.\d+)?)/(\d+)?')
        strategy_val, strategy_den = find_score(r'(?:\*?\*?Strategy Development:\*?\*?|Strategy Development:)\s*(\d+(?:\.\d+)?)/(\d+)?')
        risk_val, risk_den = find_score(r'(?:\*?\*?Risk Management:\*?\*?|Risk Management:)\s*(\d+(?:\.\d+)?)/(\d+)?')
        overall_val, overall_den = find_score(r'(?:\*?\*?Overall:\*?\*?|Overall:)\s*(\d+(?:\.\d+)?)/(\d+)?')

        # Pattern B: Data Packet Score, Trade Plan Score (x/5 or x/10)
        data_packet_val, data_packet_den = find_score(r'(?:Data Packet Score:)\s*(\d+(?:\.\d+)?)/(\d+)?')
        trade_plan_val, trade_plan_den = find_score(r'(?:Trade Plan Score:)\s*(\d+(?:\.\d+)?)/(\d+)?')

        def to_ten_scale(value: float | None, denom: float | None) -> int | None:
            if value is None:
                return None
            d = denom if denom and denom > 0 else 10.0
            scaled = value * (10.0 / d)
            return int(round(scaled))

        # Determine plan quality and confidence scores (1..10)
        plan_quality_10 = None
        confidence_10 = None

        # Prefer explicit fields; otherwise fall back to trade plan score or market analysis
        if market_val is not None:
            plan_quality_10 = to_ten_scale(market_val, market_den)
        if overall_val is not None:
            confidence_10 = to_ten_scale(overall_val, overall_den)

        # Fall back to Trade Plan Score for quality if not found
        if plan_quality_10 is None and trade_plan_val is not None:
            plan_quality_10 = to_ten_scale(trade_plan_val, trade_plan_den)

        # Fall back to Data Packet Score or plan quality for confidence if not found
        if confidence_10 is None:
            if data_packet_val is not None:
                confidence_10 = to_ten_scale(data_packet_val, data_packet_den)
            elif plan_quality_10 is not None:
                confidence_10 = plan_quality_10
        
        # Last resort defaults if nothing parsed
        if plan_quality_10 is None:
            plan_quality_10 = 0
        if confidence_10 is None:
            confidence_10 = 0
        
        # Extract decision heuristic
        decision = "NO-GO"
        upper_text = analysis_text.upper()
        if "GO" in upper_text and "NO-GO" not in upper_text:
            decision = "GO"
        
        # Create JSON structure
        json_data = {
            "planQualityScore": {
                "score": plan_quality_10,
                "justification": "Summarized from reviewer analysis"
            },
            "confidenceScore": {
                "score": confidence_10,
                "justification": "Summarized from reviewer analysis"
            },
            "decision": decision,
            "reasoning": "Converted from markdown analysis",
            "suggestions": ["Reviewer returned markdown instead of JSON - converted automatically"]
        }
        
        return json.dumps(json_data, indent=2)
        
    except Exception as e:
        print(f"Warning: Could not convert analysis to JSON: {e}")
        # Return a fallback JSON
        return json.dumps({
            "planQualityScore": {"score": 0.0, "reasoning": "JSON conversion failed"},
            "strategyScore": {"score": 0.0, "reasoning": "JSON conversion failed"},
            "riskManagementScore": {"score": 0.0, "reasoning": "JSON conversion failed"},
            "confidenceScore": {"score": 0.0, "reasoning": "JSON conversion failed"},
            "decision": "NO-GO",
            "reasoning": "JSON conversion failed",
            "suggestions": ["Reviewer output could not be parsed"]
        }, indent=2)

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
        # Clean up the review output using the dedicated function
        cleaned_output = clean_json_output(review_output_raw)
        
        if not cleaned_output:
            raise ValueError("Empty or invalid output from reviewer")
        
        # Try to parse the JSON
        review_scores = json.loads(cleaned_output)
        
        # Validate the structure
        if 'planQualityScore' not in review_scores or 'confidenceScore' not in review_scores:
            raise KeyError("Missing required score fields")
        
        # Save the scores
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
        print("--- End Raw Output ---")
        
        # Create fallback review scores to prevent file not found errors
        fallback_scores = {
            "planQualityScore": {
                "score": 1,
                "justification": "Reviewer failed to provide valid analysis - fallback scores applied"
            },
            "confidenceScore": {
                "score": 1,
                "justification": "Reviewer failed to provide valid analysis - fallback scores applied"
            },
            "error": {
                "type": str(type(e).__name__),
                "message": str(e),
                "raw_output": review_output_raw
            }
        }
        
        # Save fallback scores
        with open(REVIEW_OUTPUT_PATH, 'w') as f:
            json.dump(fallback_scores, f, indent=2)
        print(f"⚠️  Fallback scores saved to: {REVIEW_OUTPUT_PATH.name}")
        
        # Show fallback decision
        print("\n--- FALLBACK DECISION ---")
        print("🔴 DECISION: NO-GO. DISCARD PLAN. Reviewer analysis failed.")
        print("-" * 50)


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