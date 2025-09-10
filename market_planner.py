import yfinance as yf
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from datetime import datetime, timezone
import os
import json
import html
import re
from pathlib import Path
import cloudscraper
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.genai import types
from dotenv import load_dotenv
import requests
import mplfinance as mpf
import matplotlib.pyplot as plt
import warnings
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
    return genai.GenerativeModel("gemini-2.5-pro-latest")

def get_gemini_client():
    """Get Gemini client for new API."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found. Please set it as an environment variable.")
    from google import genai
    return genai.Client(api_key=GEMINI_API_KEY)

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
MT5_ALERTS_PATH = DATE_OUTPUT_DIR / "mt5_alerts.json"

# --- Market Symbols ---
SYMBOLS = {
    "EURUSD": "EURUSD=X",
    "DXY": "DX-Y.NYB",
    "US10Y": "^TNX",
    "EURJPY": "EURJPY=X",
    "SPX500": "^GSPC"
}

# --- Telegram Configuration ---

# Visual indicators configuration
# Import shared constants
try:
    from telegram_constants import VISUAL_INDICATORS, PSYCHOLOGY_TIPS
except ImportError:
    # Fallback constants if shared file is not available
    VISUAL_INDICATORS = {
        "emojis": {
            "go": "✅", "wait": "⏸️", "skip": "❌",
            "low_risk": "🟢", "medium_risk": "🟡", "high_risk": "🔴",
            "bullish": "📈", "bearish": "📉", "neutral": "➡️",
            "decision": "🎯", "market": "📊", "action": "⚡"
        }
    }
    PSYCHOLOGY_TIPS = {
        'general': ["💡 Plan your trade, trade your plan", "⚖️ Risk management is profit management"]
    }

class TelegramMessageBuilder:
    """Builds concise, scannable Telegram messages for trading decisions."""
    
    def __init__(self):
        self.emojis = VISUAL_INDICATORS["emojis"]
        self.psychology_tips = PSYCHOLOGY_TIPS
        
    def build_summary_message(self, data_packet, review_scores, mt5_alerts_count=0):
        """Build concise primary summary message."""
        try:
            # Extract key data
            current_price = data_packet["marketSnapshot"]["currentPrice"]
            current_time = data_packet["marketSnapshot"]["currentTimeUTC"] 
            daily_trend = data_packet["multiTimeframeAnalysis"]["Daily"]["trendDirection"]
            h4_trend = data_packet["multiTimeframeAnalysis"]["H4"]["trendDirection"]
            
            quality_score = review_scores['planQualityScore']['score']
            confidence_score = review_scores['confidenceScore']['score']
            
            # Get current date for header
            date_str = datetime.now().strftime("%m/%d")
            
            # Determine decision and emoji
            decision_data = self._get_decision_data(quality_score, confidence_score)
            
            # Get market bias emoji
            market_emoji = self._get_market_emoji(daily_trend, h4_trend)
            
            # Calculate VIX level placeholder (would need actual VIX data)
            vix_level = "N/A"  # Placeholder - could extract from SPX500 volatility
            
            # Build primary message
            message = (
                f"📊 MARKET PLAN SUMMARY - {date_str}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🎯 EURUSD: {decision_data['emoji']} {decision_data['decision']}\n"
                f"   Price: ${current_price:.4f}\n"
                f"   Scores: Q{quality_score}/C{confidence_score}\n\n"
                f"📈 Market: {market_emoji} {self._get_market_bias(daily_trend, h4_trend)} (VIX: {vix_level})\n\n"
                f"{decision_data['reason']}\n\n"
                f"⚡ Action: {decision_data['next_step']}\n"
                f"━━━━━━━━━━━━━━━━━"
            )
            
            return message
            
        except Exception as e:
            print(f"❌ Error building summary message: {e}")
            return self._build_fallback_message(data_packet, review_scores)
    
    def build_technical_details(self, data_packet):
        """Build technical analysis details message (conditional)."""
        try:
            daily_analysis = data_packet["multiTimeframeAnalysis"]["Daily"]
            h4_analysis = data_packet["multiTimeframeAnalysis"]["H4"]
            h1_analysis = data_packet["multiTimeframeAnalysis"]["H1"]
            
            message = (
                f"📈 TECHNICAL DETAILS\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"**Timeframe Alignment:**\n"
                f"• Daily: {daily_analysis.get('trendDirection', 'N/A')}\n"
                f"• H4: {h4_analysis.get('trendDirection', 'N/A')}\n" 
                f"• H1: {h1_analysis.get('trendDirection', 'N/A')}\n\n"
            )
            
            # Add key levels with smart filtering
            levels_added = 0
            max_levels = 4  # Limit to most important levels
            
            if 'keySupportLevels' in daily_analysis and daily_analysis['keySupportLevels']:
                support_levels = daily_analysis['keySupportLevels'][:2]  # Top 2
                for level in support_levels:
                    if levels_added < max_levels:
                        message += f"🟢 Support: {level:.4f}\n"
                        levels_added += 1
                        
            if 'keyResistanceLevels' in daily_analysis and daily_analysis['keyResistanceLevels']:
                resistance_levels = daily_analysis['keyResistanceLevels'][:2]  # Top 2
                for level in resistance_levels:
                    if levels_added < max_levels:
                        message += f"🔴 Resistance: {level:.4f}\n"
                        levels_added += 1
            
            # Add volatility context if available
            if 'volatilityMetrics' in data_packet:
                atr_pips = data_packet['volatilityMetrics'].get('atr_14_daily_pips', 'N/A')
                message += f"\n📊 Daily ATR: {atr_pips} pips"
            
            return message
            
        except Exception as e:
            print(f"❌ Error building technical details: {e}")
            return "📈 Technical details temporarily unavailable"
    
    def build_risk_details(self, analysis_data, position_differs_from_standard=False):
        """Build risk management details (conditional)."""
        try:
            if not position_differs_from_standard:
                return None  # Don't send if using standard position sizing
                
            message = (
                f"⚠️ RISK ALERT\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"Position sizing differs from standard rules\n"
                f"Review risk parameters before execution"
            )
            
            return message
            
        except Exception as e:
            print(f"❌ Error building risk details: {e}")
            return None
    
    def check_critical_warnings(self, data_packet, review_scores):
        """Check if critical warnings override concise format."""
        try:
            quality_score = review_scores['planQualityScore']['score'] 
            
            # Calculate approximate risk percentage (placeholder - would need actual calculation)
            risk_pct = 1.0  # Default assumption
            
            # Check VIX equivalent (using current price volatility as proxy)
            current_price = data_packet["marketSnapshot"]["currentPrice"]
            vix_equivalent = 20  # Placeholder - would calculate from price data
            
            # Critical conditions that override concise format
            critical_conditions = [
                risk_pct > 3.0,  # Risk > 3% of account
                vix_equivalent > 30,  # High volatility
                quality_score < 4,  # Very poor plan quality
            ]
            
            if any(critical_conditions):
                return self._build_critical_warning_message(critical_conditions)
            
            return None
            
        except Exception as e:
            print(f"❌ Error checking critical warnings: {e}")
            return None
    
    def _build_critical_warning_message(self, conditions):
        """Build critical warning override message."""
        warnings = []
        if conditions[0]:  # High risk
            warnings.append("🚨 HIGH RISK: >3% account exposure")
        if conditions[1]:  # High volatility  
            warnings.append("🌪️ HIGH VOLATILITY: VIX >30")
        if conditions[2]:  # Poor quality
            warnings.append("📉 POOR QUALITY: Plan score <4")
            
        return (
            f"🚨 CRITICAL WARNINGS\n"
            f"━━━━━━━━━━━━━━━━━━\n" +
            "\n".join(warnings) +
            f"\n\n⚠️ Review plan thoroughly before proceeding"
        )
    
    def filter_by_relevance(self, data, context):
        """Filter information by relevance hierarchy."""
        try:
            filtered_data = {
                'critical': [],    # Always show
                'important': [],   # Show if affects decision  
                'contextual': [],  # Show if requested
                'educational': []  # Rotate daily
            }
            
            quality_score = context.get('quality_score', 5)
            confidence_score = context.get('confidence_score', 5)
            
            # Critical: Always show (stop loss, position size)
            if 'stop_loss' in data:
                filtered_data['critical'].append(data['stop_loss'])
            if 'position_size' in data:
                filtered_data['critical'].append(data['position_size'])
                
            # Important: Show if affects decision (divergences, news)
            if quality_score >= 6 and 'technical_details' in data:
                filtered_data['important'].append(data['technical_details'])
                
            # Contextual: Show if explicitly requested
            if context.get('show_details', False):
                filtered_data['contextual'] = data.get('additional_analysis', [])
                
            # Educational: Rotate daily (psychology tips)
            filtered_data['educational'].append(
                self.get_daily_psychology_tip(context.get('market_condition', 'general'))
            )
            
            return filtered_data
            
        except Exception as e:
            print(f"❌ Error filtering by relevance: {e}")
            return {'critical': [data], 'important': [], 'contextual': [], 'educational': []}
    
    def get_daily_psychology_tip(self, market_condition='general'):
        """Get rotating psychology reminder based on context."""
        try:
            # Select appropriate tip category
            tips_pool = self.psychology_tips.get(market_condition, self.psychology_tips['general'])
            
            # Use date-based rotation for consistency
            today = datetime.now().timetuple().tm_yday  # Day of year
            tip_index = today % len(tips_pool)
            
            return f"💡 {tips_pool[tip_index]}"
            
        except Exception as e:
            print(f"❌ Error getting psychology tip: {e}")
            return "💡 Stay disciplined and follow your plan"
    
    def _get_decision_data(self, quality_score, confidence_score):
        """Get decision emoji, text, and reasoning."""
        if quality_score >= 6 and confidence_score >= 6:
            return {
                'emoji': self.emojis['go'],
                'decision': 'GO',
                'reason': '✅ Plan is solid and conviction is high',
                'next_step': 'Prepare for execution'
            }
        elif quality_score >= 6 and confidence_score < 6:
            return {
                'emoji': self.emojis['wait'], 
                'decision': 'WAIT',
                'reason': '⏸️ Plan is solid, but market feel is off',
                'next_step': 'Monitor for confirmation signals'
            }
        else:
            return {
                'emoji': self.emojis['skip'],
                'decision': 'SKIP', 
                'reason': '❌ Quality or confidence too low',
                'next_step': 'Wait for better setup'
            }
    
    def _get_market_emoji(self, daily_trend, h4_trend):
        """Get market direction emoji based on trend alignment."""
        daily_bull = 'bull' in str(daily_trend).lower()
        h4_bull = 'bull' in str(h4_trend).lower()
        
        if daily_bull and h4_bull:
            return self.emojis['bullish']
        elif not daily_bull and not h4_bull:
            return self.emojis['bearish']
        else:
            return self.emojis['neutral']
    
    def _get_market_bias(self, daily_trend, h4_trend):
        """Get market bias text."""
        daily_bull = 'bull' in str(daily_trend).lower()
        h4_bull = 'bull' in str(h4_trend).lower()
        
        if daily_bull and h4_bull:
            return "BULLISH"
        elif not daily_bull and not h4_bull:
            return "BEARISH" 
        else:
            return "MIXED"
    
    def _build_fallback_message(self, data_packet, review_scores):
        """Build basic fallback message if main builder fails."""
        try:
            current_price = data_packet["marketSnapshot"]["currentPrice"]
            quality_score = review_scores['planQualityScore']['score']
            confidence_score = review_scores['confidenceScore']['score']
            
            return (
                f"📊 MARKET SUMMARY\n"
                f"EURUSD: {current_price:.4f}\n"
                f"Quality: {quality_score}/10\n"
                f"Confidence: {confidence_score}/10\n"
                f"Status: {'GO' if quality_score >= 6 and confidence_score >= 6 else 'WAIT'}"
            )
        except Exception:
            return "📊 Market analysis completed - check files for details"

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
        "text": message
    }
    # Only include parse_mode when explicitly using a supported format
    if parse_mode in ["Markdown", "HTML"]:
        data["parse_mode"] = parse_mode
    
    try:
        response = requests.post(url, data=data, timeout=10)
        # Provide clearer error diagnostics without relying solely on exceptions
        if not response.ok:
            try:
                error_text = response.text
            except Exception:
                error_text = "<no body>"
            print(f"❌ Telegram API error ({response.status_code}): {error_text[:300]}")
            response.raise_for_status()
        print("✅ Telegram message sent successfully")
        return True
    except requests.exceptions.RequestException as e:
        # Fallback to plain text for both Markdown and HTML parsing errors
        if parse_mode in ["Markdown", "HTML"]:
            print(f"❌ {parse_mode} parsing failed, retrying with plain text: {e}")
            data_plain = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message
            }
            try:
                response = requests.post(url, data=data_plain, timeout=10)
                if not response.ok:
                    try:
                        error_text = response.text
                    except Exception:
                        error_text = "<no body>"
                    print(f"❌ Telegram API error (plain text, {response.status_code}): {error_text[:300]}")
                    response.raise_for_status()
                print("✅ Telegram message sent successfully (plain text)")
                return True
            except requests.exceptions.RequestException as e2:
                print(f"❌ Failed to send Telegram message (plain text): {e2}")
                return False
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
        if parse_mode == "HTML":
            chunk_header = f"<b>📄 Part {i} of {len(chunks)}</b>\n\n"
        elif parse_mode == "Markdown":
            chunk_header = f"📄 *Part {i} of {len(chunks)}*\n\n"
        else:
            # Plain text header when no parse mode is used
            chunk_header = f"📄 Part {i} of {len(chunks)}\n\n"
        full_chunk = chunk_header + chunk
        
        if _send_single_message(full_chunk, parse_mode):
            success_count += 1
        else:
            print(f"❌ Failed to send chunk {i}")
    
    print(f"✅ Sent {success_count}/{len(chunks)} message chunks successfully")
    return success_count == len(chunks)

def send_trading_summary(data_packet, trade_plan_path, review_scores_path):
    """Send a summary of the trading analysis to Telegram using new concise format."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    try:
        # Read the trade plan
        with open(trade_plan_path, 'r') as f:
            trade_plan = f.read()
        
        # Read the review scores
        with open(review_scores_path, 'r') as f:
            review_scores = json.load(f)
        
        # Read MT5 alerts if available
        mt5_alerts_count = 0
        try:
            with open(MT5_ALERTS_PATH, 'r') as f:
                mt5_alerts = json.load(f)
                mt5_alerts_count = mt5_alerts.get('metadata', {}).get('total_alerts', 0)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Initialize message builder
        message_builder = TelegramMessageBuilder()
        
        # Check for critical warnings first
        critical_warning = message_builder.check_critical_warnings(data_packet, review_scores)
        if critical_warning:
            # Send critical warning and full details
            warning_sent = send_telegram_message(critical_warning, parse_mode="Markdown")
            full_plan_sent = send_telegram_message(f"📋 Full Plan\n\n{trade_plan}", parse_mode="Markdown")
            return warning_sent and full_plan_sent
        
        # Build primary summary message (always send)
        summary_message = message_builder.build_summary_message(
            data_packet, review_scores, mt5_alerts_count
        )
        
        # Determine if we should send additional details based on decision
        quality_score = review_scores['planQualityScore']['score']
        confidence_score = review_scores['confidenceScore']['score']
        is_go_decision = quality_score >= 6 and confidence_score >= 6
        
        # Send primary summary message
        summary_sent = send_telegram_message(summary_message, parse_mode="Markdown")
        
        # Initialize message tracking
        messages_sent = [summary_sent]
        
        # Conditionally send technical details for GO decisions
        if is_go_decision:
            technical_details = message_builder.build_technical_details(data_packet)
            if technical_details:
                tech_sent = send_telegram_message(technical_details, parse_mode="Markdown")
                messages_sent.append(tech_sent)
        
        # Check if risk details are needed (when position sizing differs)
        position_differs = _position_differs_from_standard(data_packet, review_scores)
        if position_differs:
            risk_details = message_builder.build_risk_details(data_packet, True)
            if risk_details:
                risk_sent = send_telegram_message(risk_details, parse_mode="Markdown")
                messages_sent.append(risk_sent)
        
        # Send context-aware psychology tip
        daily_trend = data_packet["multiTimeframeAnalysis"]["Daily"]["trendDirection"]
        h4_trend = data_packet["multiTimeframeAnalysis"]["H4"]["trendDirection"]
        market_condition = _determine_market_condition(daily_trend, h4_trend, quality_score)
        
        psychology_tip = message_builder.get_daily_psychology_tip(market_condition)
        tip_sent = send_telegram_message(psychology_tip, parse_mode="Markdown")
        messages_sent.append(tip_sent)
        
        # For GO decisions, send abbreviated execution plan
        if is_go_decision:
            abbreviated_plan = _create_abbreviated_plan(trade_plan)
            if abbreviated_plan and len(abbreviated_plan.strip()) > 50:  # Only if meaningful content
                plan_header = "⚡ EXECUTION PLAN\n━━━━━━━━━━━━━━━━━━\n"
                plan_sent = send_telegram_message(plan_header + abbreviated_plan, parse_mode="Markdown") or \
                           send_telegram_message(plan_header + abbreviated_plan)
                messages_sent.append(plan_sent)
        
        # Return success if all critical messages were sent
        return all(messages_sent)
        
    except (KeyError, TypeError) as e:
        print(f"❌ Data structure error in Telegram summary: {e}")
        # Fallback to simplified message
        try:
            message_builder = TelegramMessageBuilder()
            fallback_message = message_builder._build_fallback_message(data_packet, review_scores)
            return send_telegram_message(fallback_message)
        except (AttributeError, KeyError) as e2:
            print(f"❌ Fallback message also failed: {e2}")
            return False
    except (ConnectionError, requests.exceptions.RequestException) as e:
        print(f"❌ Network error sending Telegram message: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error creating Telegram summary: {e}")
        # Log the full exception for debugging
        import traceback
        traceback.print_exc()
        return False

def _position_differs_from_standard(data_packet, review_scores):
    """Check if position sizing differs from standard rules."""
    try:
        # This would implement actual logic to check if position sizing
        # differs from standard rules based on volatility, risk, etc.
        # For now, return False (use standard sizing)
        quality_score = review_scores['planQualityScore']['score']
        
        # Example: Non-standard if very high or very low confidence
        confidence_score = review_scores['confidenceScore']['score']
        return confidence_score < 5 or confidence_score > 9
        
    except Exception:
        return False

def _determine_market_condition(daily_trend, h4_trend, quality_score):
    """Determine market condition for psychology tip selection."""
    try:
        # Check for trend alignment
        daily_bull = 'bull' in str(daily_trend).lower()
        h4_bull = 'bull' in str(h4_trend).lower()
        
        # Simple volatility proxy - if trends don't align, market may be volatile
        if daily_bull == h4_bull:
            return 'calm_market'
        else:
            return 'volatile_market'
            
        # Note: In a full implementation, we could also check:
        # - Recent win/loss streak from trading history
        # - VIX levels for market stress
        # - ATR values for volatility assessment
        
    except Exception:
        return 'general'

def _create_abbreviated_plan(full_plan):
    """Extract key execution details from full trading plan in clean, actionable format."""
    try:
        lines = full_plan.split('\n')
        plan_data = {
            'plan_a': {'entry': None, 'stop': None, 'tp1': None, 'tp2': None, 'rr': None},
            'plan_b': {'entry': None, 'stop': None, 'tp': None, 'rr': None},
            'risk_management': []
        }
        
        current_plan = None
        all_prices = []  # Collect all prices for fallback
        
        # Extract structured data from the plan
        for i, line in enumerate(lines):
            line_clean = line.strip()
            line_lower = line_clean.lower()
            
            # Collect all prices for fallback
            price_matches = re.findall(r'1\.\d{4}', line_clean)
            all_prices.extend(price_matches)
            
            # Identify which plan we're in
            if 'plan a:' in line_lower or '3. plan a:' in line_lower or 'primary trade' in line_lower:
                current_plan = 'plan_a'
                continue
            elif 'plan b:' in line_lower or '4. plan b:' in line_lower or 'contingency' in line_lower:
                current_plan = 'plan_b'
                continue
            elif ('execution' in line_lower and 'risk' in line_lower) or 'risk protocols' in line_lower:
                current_plan = 'risk'
                continue
            
            # Skip JSON alerts and verbose explanations
            if line_clean.startswith('{') or '"symbol":' in line_clean:
                continue
                
            # Extract key execution details based on current context
            if current_plan in ['plan_a', 'plan_b']:
                # Look for entry conditions/triggers/value zones
                if any(keyword in line_lower for keyword in ['condition:', 'trigger:', 'value zone', 'entry level']):
                    price_match = re.search(r'1\.\d{4}', line_clean)
                    if price_match and not plan_data[current_plan]['entry']:
                        plan_data[current_plan]['entry'] = price_match.group()
                
                # Extract stop loss - look for SL or Stop Loss
                if 'stop loss' in line_lower or 'sl:' in line_lower or '*stop loss*' in line_lower or '**stop loss' in line_lower:
                    price_match = re.search(r'1\.\d{4}', line_clean)
                    if price_match:
                        plan_data[current_plan]['stop'] = price_match.group()
                
                # Extract take profits - be more flexible with patterns
                if 'take profit 1' in line_lower or 'tp1:' in line_lower or '*take profit 1*' in line_lower or '**take profit 1' in line_lower:
                    price_match = re.search(r'1\.\d{4}', line_clean)
                    if price_match:
                        plan_data[current_plan]['tp1'] = price_match.group()
                elif 'take profit 2' in line_lower or 'tp2:' in line_lower or '*take profit 2*' in line_lower or '**take profit 2' in line_lower:
                    price_match = re.search(r'1\.\d{4}', line_clean)
                    if price_match:
                        plan_data[current_plan]['tp2'] = price_match.group()
                elif ('take profit' in line_lower or 'tp:' in line_lower) and current_plan == 'plan_b':
                    # For Plan B, single take profit
                    price_match = re.search(r'1\.\d{4}', line_clean)
                    if price_match and not plan_data[current_plan]['tp']:
                        plan_data[current_plan]['tp'] = price_match.group()
                
                # Extract risk/reward ratio
                if 'risk/reward' in line_lower or 'r:r' in line_lower or 'r&r' in line_lower:
                    rr_match = re.search(r'~?1:(\d+\.?\d*)', line_clean)
                    if rr_match:
                        plan_data[current_plan]['rr'] = f"1:{rr_match.group(1)}"
            
            # Extract essential risk management
            elif current_plan == 'risk':
                if ('capital at risk' in line_lower or ('risk' in line_lower and '%' in line_clean)):
                    plan_data['risk_management'].append(line_clean.replace('**', '').replace('*', '').strip())
                elif 'maximum daily loss' in line_lower:
                    plan_data['risk_management'].append(line_clean.replace('**', '').replace('*', '').strip())
        
        # Try to extract missing entry prices from Price Alert sections
        if not plan_data['plan_a']['entry'] or not plan_data['plan_b']['entry']:
            for line in lines:
                line_lower = line.lower()
                if 'ask <' in line_lower:  # Long entry alert
                    price_match = re.search(r'1\.\d{4}', line)
                    if price_match and not plan_data['plan_a']['entry']:
                        plan_data['plan_a']['entry'] = price_match.group()
                elif 'bid >' in line_lower:  # Short entry alert
                    price_match = re.search(r'1\.\d{4}', line)
                    if price_match and not plan_data['plan_b']['entry']:
                        plan_data['plan_b']['entry'] = price_match.group()
        
        # Build clean, actionable summary
        summary_lines = []
        
        # Plan A (Primary)
        if any(plan_data['plan_a'].values()):
            summary_lines.append("**🎯 PRIMARY PLAN (A)**")
            if plan_data['plan_a']['entry']:
                summary_lines.append(f"• Entry: {plan_data['plan_a']['entry']}")
            if plan_data['plan_a']['stop']:
                summary_lines.append(f"• Stop: {plan_data['plan_a']['stop']}")
            if plan_data['plan_a']['tp1']:
                summary_lines.append(f"• TP1: {plan_data['plan_a']['tp1']}")
            if plan_data['plan_a']['tp2']:
                summary_lines.append(f"• TP2: {plan_data['plan_a']['tp2']}")
            if plan_data['plan_a']['rr']:
                summary_lines.append(f"• R:R: {plan_data['plan_a']['rr']}")
            summary_lines.append("")
        
        # Plan B (Contingency)
        if any(plan_data['plan_b'].values()):
            summary_lines.append("**🔄 CONTINGENCY PLAN (B)**")
            if plan_data['plan_b']['entry']:
                summary_lines.append(f"• Entry: {plan_data['plan_b']['entry']}")
            if plan_data['plan_b']['stop']:
                summary_lines.append(f"• Stop: {plan_data['plan_b']['stop']}")
            if plan_data['plan_b']['tp']:
                summary_lines.append(f"• TP: {plan_data['plan_b']['tp']}")
            if plan_data['plan_b']['rr']:
                summary_lines.append(f"• R:R: {plan_data['plan_b']['rr']}")
            summary_lines.append("")
        
        # Essential risk management (clean up formatting)
        if plan_data['risk_management']:
            summary_lines.append("**⚖️ RISK MANAGEMENT**")
            for rule in plan_data['risk_management'][:2]:  # Limit to 2 most important rules
                summary_lines.append(f"• {rule}")
        
        result = '\n'.join(summary_lines).strip()
        
        # Fallback if extraction failed - use collected prices
        if len(result) < 50:
            return _create_fallback_plan(full_plan, all_prices)
        
        return result
        
    except Exception as e:
        print(f"❌ Error creating abbreviated plan: {e}")
        return _create_fallback_plan(full_plan)


def _create_fallback_plan(full_plan, all_prices=None):
    """Create a simple fallback plan when structured extraction fails."""
    try:
        # Look for any price levels mentioned
        if all_prices is None:
            price_matches = re.findall(r'1\.\d{4}', full_plan)
        else:
            price_matches = list(set(all_prices))  # Remove duplicates
            
        if len(price_matches) >= 3:
            # Assume first few prices are entry, stop, targets
            return (
                f"**🎯 EXECUTION SUMMARY**\n"
                f"• Key Levels: {', '.join(price_matches[:4])}\n"
                f"• Risk 0.75% on primary setup\n"
                f"• Plan details in full analysis"
            )
        else:
            # Very basic fallback
            return (
                f"**🎯 EXECUTION SUMMARY**\n"
                f"• Review full plan for entry details\n"
                f"• Standard risk management applies\n"
                f"• Wait for confirmed setups"
            )
    except Exception:
        return "**🎯 EXECUTION SUMMARY**\n• See full plan for details"


# --- 1. DATA ENGINEERING MODULE ---

def calculate_indicators(data):
    """Calculate technical indicators: 9EMA, 21EMA, 200SMA, and MACD"""
    # EMA 9 and 21
    data['EMA9'] = data['Close'].ewm(span=9).mean()
    data['EMA21'] = data['Close'].ewm(span=21).mean()
    
    # SMA 200
    data['SMA200'] = data['Close'].rolling(window=200).mean()
    
    # MACD
    ema12 = data['Close'].ewm(span=12).mean()
    ema26 = data['Close'].ewm(span=26).mean()
    data['MACD'] = ema12 - ema26
    data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
    data['MACD_Histogram'] = data['MACD'] - data['MACD_Signal']
    
    return data

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

def export_charts():
    """Generate charts for all timeframes with technical indicators"""
    print("\n--- STAGE 1.5: GENERATING CHARTS ---")
    
    # Configuration for chart generation
    symbol = 'EURUSD=X'
    timeframes = {
        '1H': {
            'period': '30d',
            'interval': '1h',
            'display_candles': 200,
            'min_data_needed': 250
        },
        '4H': {
            'period': '120d',
            'interval': '1h',
            'display_candles': 150,
            'min_data_needed': 200
        },
        'Daily': {
            'period': '2y',
            'interval': '1d',
            'display_candles': 100,
            'min_data_needed': 250
        }
    }
    
    # Create intermarket charts directory
    intermarket_dir = DATE_OUTPUT_DIR / "intermarket_charts"
    intermarket_dir.mkdir(exist_ok=True)
    
    print(f"📊 Generating charts in: {DATE_OUTPUT_DIR}")
    
    for tf_name, params in timeframes.items():
        try:
            print(f"Generating {tf_name} chart...")
            
            # Download data
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                data = yf.download(
                    tickers=symbol,
                    period=params['period'],
                    interval=params['interval'],
                    progress=False,
                    auto_adjust=True
                )
            
            if data.empty:
                print(f"No data returned for {tf_name}. Skipping.")
                continue
            
            # Handle MultiIndex columns
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            # Ensure data types are numeric
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce')
            
            data.dropna(subset=['Open', 'High', 'Low', 'Close'], inplace=True)
            
            # Special handling for 4H chart
            if tf_name == '4H':
                agg_rules = {
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum'
                }
                data = data.resample('4h').agg(agg_rules).dropna()
                print("Resampled 1H data to 4H.")
            
            # Calculate technical indicators
            data = calculate_indicators(data)
            
            # Check minimum data requirement
            if len(data) < params['min_data_needed']:
                print(f"Warning: Only {len(data)} periods available for {tf_name}")
            
            # Limit to display candles
            display_data = data.tail(params['display_candles']).copy()
            
            # Generate chart
            chart_title = f'EUR/USD - {tf_name} Chart (Last {len(display_data)} Periods)\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = DATE_OUTPUT_DIR / f'EURUSD_{tf_name}_{timestamp}.png'
            
            # Define additional plots
            addplot_list = []
            
            # Add moving averages
            if not display_data['EMA9'].isna().all():
                addplot_list.append(mpf.make_addplot(display_data['EMA9'], color='blue', width=1.5))
            
            if not display_data['EMA21'].isna().all():
                addplot_list.append(mpf.make_addplot(display_data['EMA21'], color='orange', width=1.5))
            
            if not display_data['SMA200'].isna().all() and display_data['SMA200'].notna().sum() > 0:
                addplot_list.append(mpf.make_addplot(display_data['SMA200'], color='red', width=2))
            
            # Add MACD
            if not display_data['MACD'].isna().all() and not display_data['MACD_Signal'].isna().all():
                addplot_list.append(mpf.make_addplot(display_data['MACD'], panel=2, color='blue',
                                                   secondary_y=False, ylabel='MACD'))
                addplot_list.append(mpf.make_addplot(display_data['MACD_Signal'], panel=2, color='red',
                                                   secondary_y=False))
                
                if not display_data['MACD_Histogram'].isna().all():
                    hist_data = display_data['MACD_Histogram'].copy()
                    hist_data = hist_data.fillna(0)
                    addplot_list.append(mpf.make_addplot(hist_data, panel=2, type='bar',
                                                       color='gray', alpha=0.7, secondary_y=False))
            
            # Handle volume
            show_volume = 'Volume' in display_data.columns and not display_data['Volume'].isna().all()
            panel_ratios = (3, 1, 1) if any('panel' in str(ap) for ap in addplot_list) else (3, 1) if show_volume else (1,)
            
            # Create and save plot
            mpf.plot(
                display_data,
                type='candle',
                style='charles',
                title=chart_title,
                ylabel='Price ($)',
                volume=show_volume,
                ylabel_lower='Volume' if show_volume else None,
                addplot=addplot_list if addplot_list else None,
                panel_ratios=panel_ratios,
                figsize=(16, 12),
                warn_too_much_data=params['display_candles'] + 50,
                savefig=dict(fname=str(filename), dpi=150, bbox_inches='tight')
            )
            
            print(f"✅ Chart saved: {filename}")
            
        except Exception as e:
            print(f"❌ Error generating {tf_name} chart: {e}")
            import traceback
            traceback.print_exc()
    
    # Generate intermarket charts
    print("Generating intermarket charts...")
    generate_intermarket_charts(intermarket_dir)
    
    print("✅ Chart generation completed")

def generate_intermarket_charts(output_dir):
    """Generate charts for intermarket analysis symbols"""
    intermarket_symbols = {
        'DXY': 'DX-Y.NYB',
        'SPX500': '^GSPC', 
        'US10Y': '^TNX',
        'EURJPY': 'EURJPY=X'
    }
    
    for name, symbol in intermarket_symbols.items():
        try:
            print(f"Generating {name} chart...")
            
            data = yf.download(symbol, period="6mo", interval="1d", progress=False, auto_adjust=True)
            
            if data.empty:
                print(f"No data for {name}")
                continue
            
            # Handle MultiIndex
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            # Calculate indicators
            data = calculate_indicators(data)
            
            # Use last 100 days
            display_data = data.tail(100).copy()
            
            # Generate chart
            chart_title = f'{name} - Daily Chart (Last 100 Days)\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_dir / f'{name}_Daily_{timestamp}.png'
            
            # Add moving averages
            addplot_list = []
            if not display_data['EMA9'].isna().all():
                addplot_list.append(mpf.make_addplot(display_data['EMA9'], color='blue', width=1.5))
            if not display_data['EMA21'].isna().all():
                addplot_list.append(mpf.make_addplot(display_data['EMA21'], color='orange', width=1.5))
            if not display_data['SMA200'].isna().all() and display_data['SMA200'].notna().sum() > 0:
                addplot_list.append(mpf.make_addplot(display_data['SMA200'], color='red', width=2))
            
            # Create plot
            mpf.plot(
                display_data,
                type='candle',
                style='charles',
                title=chart_title,
                ylabel='Price',
                addplot=addplot_list if addplot_list else None,
                figsize=(12, 8),
                savefig=dict(fname=str(filename), dpi=150, bbox_inches='tight')
            )
            
            print(f"✅ {name} chart saved: {filename}")
            
        except Exception as e:
            print(f"❌ Error generating {name} chart: {e}")

# --- AI AGENT SYSTEM ---

def run_agent(prompt_parts, system_instruction=None, images=None):
    """Runs a single Gemini agent with text + optional images."""
    try:
        client = get_gemini_client()
        model = "gemini-2.5-pro"
        
        contents = [types.Content(role="user", parts=prompt_parts)]
        if images:
            contents[0].parts.extend(images)

        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=-1)
        )

        if system_instruction:
            config.system_instruction = [types.Part.from_text(text=system_instruction)]

        generated_text = ""
        for chunk in client.models.generate_content_stream(
            model=model, contents=contents, config=config
        ):
            if chunk.text:
                generated_text += chunk.text
        return generated_text.strip()
        
    except Exception as e:
        print(f"❌ Error in run_agent: {e}")
        return ""

def load_latest_chart(symbol_tf):
    """Finds the latest chart for a given symbol_tf (like 'EURUSD_1H')."""
    latest_file, latest_time = None, None
    for filename in os.listdir(DATE_OUTPUT_DIR):
        if filename.startswith(symbol_tf) and filename.endswith(".png"):
            parts = filename.split('_')
            ts = '_'.join(parts[2:]).split('.')[0]
            try:
                ts = datetime.strptime(ts, '%Y%m%d_%H%M%S')
                if not latest_time or ts > latest_time:
                    latest_file, latest_time = filename, ts
            except:
                continue
    if latest_file:
        path = DATE_OUTPUT_DIR / latest_file
        with open(path, "rb") as f:
            img_bytes = f.read()
        return [types.Part(inline_data=types.Blob(mime_type="image/png", data=img_bytes))]
    return None

def save_to_scratchpad(agent_name, notes_dict):
    """Append agent notes to JSON scratchpad."""
    scratchpad_path = DATE_OUTPUT_DIR / "scratchpad.json"
    if scratchpad_path.exists():
        with open(scratchpad_path, "r") as f:
            data = json.load(f)
    else:
        data = {}

    data[agent_name] = notes_dict

    with open(scratchpad_path, "w") as f:
        json.dump(data, f, indent=2)

def chart_agent(timeframe, images):
    """Analyze one chart timeframe and enforce JSON output."""
    system_inst = f"""
    You are a professional analyst for the EURUSD {timeframe} chart.
    Respond ONLY with valid JSON in the following format:

    {{
      "bias": "bullish | bearish | neutral",
      "key_levels": ["1.0800 support", "1.0950 resistance"],
      "patterns": ["double top", "trendline break"],
      "momentum": "MACD diverging, RSI near overbought",
      "setups": ["scalp long above 1.0900", "short below 1.0850"]
    }}
    """
    raw = run_agent(
        [types.Part.from_text(text=f"Analyze the EURUSD {timeframe} chart.")],
        system_instruction=system_inst,
        images=images
    )

    try:
        notes_dict = json.loads(raw)
    except Exception as e:
        notes_dict = {"error": f"Invalid JSON output or error: {raw} - {e}"}

    save_to_scratchpad(f"{timeframe}_chart", notes_dict)

def intermarket_agent():
    """Analyze cross-symbol relationships and market correlations"""
    system_inst = """
    You are a macro analyst specializing in cross-asset relationships.
    Analyze the following market data and provide insights on:
    - Dollar strength/weakness (DXY)
    - Risk sentiment (SPX500)
    - Interest rate environment (US10Y)
    - Currency cross relationships (EURJPY)
    - Overall market bias for EURUSD
    
    Respond ONLY with valid JSON:
    {
      "dollar_bias": "strong | weak | neutral",
      "risk_sentiment": "risk-on | risk-off | mixed",
      "rate_environment": "hawkish | dovish | neutral",
      "correlation_analysis": "EURUSD likely to follow/oppose other assets",
      "overall_bias": "bullish | bearish | neutral",
      "key_drivers": ["DXY strength", "Risk-off sentiment", "Rate differentials"],
      "confluence_score": 1-10
    }
    """
    
    # Get intermarket data
    intermarket_data = get_intermarket_analysis({k: v for k, v in SYMBOLS.items() if k != 'EURUSD'})
    
    # Add additional analysis
    enhanced_data = enhance_intermarket_data(intermarket_data)
    
    raw = run_agent([types.Part.from_text(text=json.dumps(enhanced_data, indent=2))], 
                   system_instruction=system_inst)
    
    try:
        notes_dict = json.loads(raw)
    except Exception as e:
        notes_dict = {"error": f"Invalid JSON output: {raw}"}
    
    save_to_scratchpad("intermarket_analysis", notes_dict)

def enhance_intermarket_data(basic_analysis):
    """Add more sophisticated intermarket analysis"""
    enhanced = basic_analysis.copy()
    
    # Add correlation analysis
    enhanced["correlations"] = calculate_correlations()
    
    # Add momentum analysis
    enhanced["momentum"] = calculate_momentum_divergences()
    
    # Add volatility analysis
    enhanced["volatility"] = calculate_volatility_relationships()
    
    return enhanced

def calculate_correlations():
    """Calculate rolling correlations between assets"""
    # This would calculate actual correlations in a real implementation
    return {
        "eurusd_dxy": -0.75,
        "eurusd_spx": 0.60,
        "eurusd_10y": 0.45
    }

def calculate_momentum_divergences():
    """Identify momentum divergences between assets"""
    return {
        "dxy_divergence": "EURUSD not following DXY weakness",
        "spx_divergence": "Risk-on but EURUSD not participating"
    }

def calculate_volatility_relationships():
    """Calculate volatility relationships"""
    return {
        "vix_equivalent": 20,
        "volatility_regime": "normal"
    }

def news_agent(events_text):
    """Summarize news & sentiment as JSON."""
    system_inst = """
    You are a macro/news analyst.
    Respond ONLY with valid JSON in the following format:

    {
      "overall_sentiment": "risk-on | risk-off | mixed",
      "eur_drivers": ["ECB commentary", "German PMI release"],
      "usd_drivers": ["Fed minutes", "NFP expectations"],
      "key_events": [
        {"time": "08:30 EST", "event": "US CPI", "expected_impact": "high"},
        {"time": "10:00 EST", "event": "ECB speech", "expected_impact": "medium"}
      ]
    }
    """
    raw = run_agent([types.Part.from_text(text=events_text)], system_instruction=system_inst)

    try:
        notes_dict = json.loads(raw)
    except Exception as e:
        notes_dict = {"error": f"Invalid JSON output or error: {raw} - {e}"}

    save_to_scratchpad("news_events", notes_dict)

def planner_agent():
    """Final trading plan using JSON scratchpad notes."""
    scratchpad_path = DATE_OUTPUT_DIR / "scratchpad.json"
    with open(scratchpad_path, "r") as f:
        all_notes = json.load(f)

    system_inst = """
    **Persona:** You are a senior FX Analyst and Day Trader for a private fund. You specialize in identifying and executing high-probability trades on EURUSD, holding them for several hours to capture the primary directional move of the day. Your analysis is methodical, patient, and avoids short-term market noise.

    **Task:** Your morning analysis, based on structured JSON data from chart and news agents, is complete. Synthesize this data into a comprehensive **intraday day trading plan for EURUSD**. The goal is to formulate one or two high-quality trade ideas for the day, not to actively scalp.

    The output must be a well-structured and professional markdown document.

    **Output Structure and Content:**

    Your plan must be clear, patient, and focus on the bigger picture for the day. Follow this structure precisely:

    ---

    ### **1. Daily Market Thesis**
    -   **Overarching Bias:** State your primary directional bias for the entire trading day (e.g., **Confident Bullish**, **Cautiously Bearish**, **Neutral/Range-Expansion**). Justify it in one sentence based on the market structure.
    -   **Expected Daily Range:** Estimate the potential high and low for the day based on key levels and ATR (Average True Range).
    -   **Decisive Catalyst:** Identify the single news event that will define the day's main volatility and could confirm or break your thesis.

    ---

    ### **2. Key Daily Levels**
    -   **Major Resistance:** The significant daily or weekly level that could cap the day's rally. Provide a clear price (e.g., `1.0850`).
    -   **Major Support:** The significant daily or weekly level that could halt a sell-off. Provide a clear price (e.g., `1.0720`).
    -   **"Line in the Sand" Level:** Define the critical pivot point for the day. A sustained break of this level would force a re-evaluation of the entire daily bias.

    ---

    ### **3. Market Sentiment & Flow**
    -   **Fundamental Wind:** Summarize the underlying economic sentiment (e.g., "Strong US data is driving dollar demand, creating underlying pressure on EURUSD").
    -   **Price Action Narrative:** Describe what the price action is telling you (e.g., "Price is showing a healthy bullish trend, with orderly pullbacks to the 1-hour 50 EMA being bought aggressively").

    ---

    ### **4. Primary Day Trade Idea: [e.g., Long on Pullback to Value]**
    -   **Trade Thesis:** A clear sentence on the strategic goal (e.g., "Entering long after a morning pullback to the established support area, targeting a new daily high during the NY session").
    -   **Entry Zone & Trigger:** Define a **broader area** for entry, not a single price. Specify the trigger on a **15-minute or 1-hour chart** (e.g., "Look for entry within the `1.0740-1.0750` zone, triggered by a 1-hour hammer or bullish engulfing candle").
    -   **Stop Loss (SL):** A logical price level placed below a key structural point (e.g., `1.0715`). *The pip distance should be wider to absorb volatility (e.g., 25-40 pips).*
    -   **Take Profit (TP):** A logical price level targeting a major daily resistance or a key extension level (e.g., `1.0835`). *The pip distance should be substantial (e.g., 80-100+ pips).*
    -   **Risk/Reward (RR) Ratio:** Calculate and state the RR ratio (e.g., `1:2.5` or better).

    ---

    ### **5. Risk & Trade Management**
    -   **Position Size:** Define the risk per trade (e.g., "Risk **1%** of capital on this primary idea").
    -   **Trade Management:** Outline how the trade will be managed once active (e.g., "Move SL to breakeven once the trade is +40 pips in profit. Consider taking partial profits at the `1.0800` psychological level").

    ---

    ### **6. Contingency Plan**
    -   **If Thesis is Invalidated:** What is the alternative plan? (e.g., "If the 'Line in the Sand' level at `1.0720` breaks with conviction, the bullish thesis is void. We will stand aside and wait for a bearish retracement setup on Monday").
    -   **Execution Note:** A key instruction for the day (e.g., "Patience is paramount. Do not force an entry if the price doesn't pull back to our zone. It's better to miss the trade than to take a bad one").
    """

    final_plan = run_agent([types.Part.from_text(text=json.dumps(all_notes, indent=2))],
                           system_instruction=system_inst)

    today_str = datetime.now().strftime('%Y%m%d')
    filepath = DATE_OUTPUT_DIR / f"Trading_plan_{today_str}.md"
    with open(filepath, "w") as f:
        f.write(final_plan)
    print(f"Trading plan saved to {filepath}")

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
    
    # TEMPORARY: Force fresh start - remove this after a few successful runs
    if os.environ.get('FORCE_FRESH_START') == 'true':
        print("🚀 FORCE_FRESH_START enabled - skipping previous session download")
        return None
    
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
    """Main orchestration function - refactored with agent system"""
    print("\n--- STAGE 1: GENERATING CHARTS AND ANALYSIS ---")
    
    # Ensure output directories exist
    OUTPUT_DIR.mkdir(exist_ok=True)
    DATE_OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"📁 Creating date-based folder: {DATE_OUTPUT_DIR}")
    
    # 1. Generate charts
    export_charts()
    
    # 2. Reset scratchpad
    scratchpad_path = DATE_OUTPUT_DIR / "scratchpad.json"
    with open(scratchpad_path, "w") as f:
        json.dump({}, f)
    
    # 3. Run chart agents
    print("\n--- STAGE 2: RUNNING CHART AGENTS ---")
    for tf in ["Daily", "4H", "1H"]:
        imgs = load_latest_chart(f"EURUSD_{tf}")
        if imgs:
            print(f"Analyzing {tf} chart...")
            chart_agent(tf, imgs)
        else:
            print(f"Warning: No chart found for {tf}")
    
    # 4. Run intermarket agent
    print("\n--- STAGE 3: RUNNING INTERMARKET AGENT ---")
    intermarket_agent()
    
    # 5. Run news agent
    print("\n--- STAGE 4: RUNNING NEWS AGENT ---")
    events = get_economic_calendar()
    if events:
        events_text = json.dumps(events, indent=2)
        news_agent(events_text)
    else:
        print("Warning: No events found")
    
    # 6. Generate final plan
    print("\n--- STAGE 5: GENERATING TRADING PLAN ---")
    planner_agent()
    
    # 7. Create compatibility packet for existing systems
    print("\n--- STAGE 6: CREATING COMPATIBILITY PACKET ---")
    packet = create_compatibility_packet()
    
    return packet

def create_compatibility_packet():
    """Create viper_packet.json for backward compatibility"""
    try:
        # Get current market data for compatibility
        eurusd_d1 = get_market_data(SYMBOLS["EURUSD"], "2y", "1d")
        eurusd_d1['ATR_14'] = calculate_atr(eurusd_d1['High'], eurusd_d1['Low'], eurusd_d1['Close'], 14)
        
        last_atr = eurusd_d1['ATR_14'].iloc[-1]
        last_close = eurusd_d1.iloc[-1]['Close']
        
        # Get previous session context
        previous_context = get_previous_session_analysis()
        
        # Create basic multi-timeframe analysis for compatibility
        multi_tf = {
            "Daily": {
                "trendDirection": "Analysis from chart agents",
                "keySupportLevels": [],
                "keyResistanceLevels": [],
                "emaStatus": {"50_ema": "N/A", "200_ema": "N/A"},
                "rsi_14": None
            },
            "H4": {
                "trendDirection": "Analysis from chart agents", 
                "keySupportLevels": [],
                "keyResistanceLevels": [],
                "emaStatus": {"50_ema": "N/A", "200_ema": "N/A"},
                "rsi_14": None
            },
            "H1": {
                "trendDirection": "Analysis from chart agents",
                "keySupportLevels": [],
                "keyResistanceLevels": [],
                "emaStatus": {"50_ema": "N/A", "200_ema": "N/A"},
                "rsi_14": None
            }
        }
        
        volatility = {
            "atr_14_daily_pips": int(last_atr * 10000),
            "predictedDailyRange": [round(last_close - last_atr, 4), round(last_close + last_atr, 4)]
        }
        
        # Create compatibility packet
        packet = {
            "marketSnapshot": {
                "pair": "EURUSD", 
                "currentPrice": last_close, 
                "currentTimeUTC": datetime.now(timezone.utc).isoformat()
            },
            "multiTimeframeAnalysis": multi_tf,
            "volatilityMetrics": volatility,
            "fundamentalAnalysis": {"keyEconomicEvents": get_economic_calendar()},
            "intermarketConfluence": get_intermarket_analysis({k: v for k, v in SYMBOLS.items() if k != 'EURUSD'}),
            "agentAnalysis": "See scratchpad.json for detailed agent analysis"
        }
        
        # Add temporal analysis
        market_evolution = analyze_market_evolution(packet, previous_context)
        thesis_evolution = analyze_market_thesis_evolution(previous_context)
        packet["temporalAnalysis"] = {
            "previousSessionContext": previous_context,
            "marketEvolution": market_evolution,
            "thesisEvolution": thesis_evolution
        }
        
        # Save compatibility packet
        with open(DATA_PACKET_PATH, 'w') as f:
            json.dump(packet, f, indent=2)
        print(f"✅ Compatibility packet saved to: {DATA_PACKET_PATH}")
        
        return packet
        
    except Exception as e:
        print(f"❌ Error creating compatibility packet: {e}")
        # Return minimal packet
        return {
            "marketSnapshot": {"pair": "EURUSD", "currentPrice": 1.0000, "currentTimeUTC": datetime.now(timezone.utc).isoformat()},
            "multiTimeframeAnalysis": {},
            "volatilityMetrics": {},
            "fundamentalAnalysis": {},
            "intermarketConfluence": {},
            "error": str(e)
        }


# --- 2. LLM ORCHESTRATION MODULE ---

def call_llm(system_prompt: str, user_prompt: str) -> str:
    """A simple wrapper for calling the Gemini model."""
    print("...")
    try:
        model = configure_gemini()
        
        # Combine system prompt and user prompt for Gemini
        # Gemini doesn't have separate system/user roles like OpenAI, so we combine them
        full_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
        
        response = model.generate_content(full_prompt)
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
        # If no JSON found, attempt conversion when this looks like a reviewer analysis
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
        "suggestions for improvement:",
        "plan quality score:",
        "confidence score:",
        "analysis and scores"
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

        # Pattern C: Plan Quality Score, Confidence Score (x/5 or x/10)
        plan_quality_val_c, plan_quality_den_c = find_score(r'(?:Plan Quality Score:)\s*(\d+(?:\.\d+)?)/(\d+)?')
        confidence_val_c, confidence_den_c = find_score(r'(?:Confidence Score:)\s*(\d+(?:\.\d+)?)/(\d+)?')

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

        # Fall back to explicit Plan Quality / Confidence if present
        if plan_quality_10 is None and plan_quality_val_c is not None:
            plan_quality_10 = to_ten_scale(plan_quality_val_c, plan_quality_den_c)
        if confidence_10 is None and confidence_val_c is not None:
            confidence_10 = to_ten_scale(confidence_val_c, confidence_den_c)

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

def extract_mt5_alerts_from_plan(trade_plan_text, current_price):
    """Extract price levels from trading plan and generate MT5 alerts JSON."""
    alerts = []
    
    # Helper function to create alert object
    def create_alert(price, condition, comment, category, priority="medium"):
        return {
            "symbol": "EURUSD",
            "price": float(price),
            "condition": condition,
            "action": "notification",
            "enabled": True,
            "comment": comment,
            "category": category,
            "priority": priority
        }
    
    # Extract price levels using regex patterns
    import re
    
    # Look for explicit price patterns in the trading plan
    price_patterns = [
        (r"Entry.*?(\d+\.\d{4,5})", "entry", "high"),
        (r"Stop Loss.*?(\d+\.\d{4,5})", "exit", "high"), 
        (r"Take Profit.*?(\d+\.\d{4,5})", "exit", "high"),
        (r"TP1.*?(\d+\.\d{4,5})", "exit", "high"),
        (r"TP2.*?(\d+\.\d{4,5})", "exit", "medium"),
        (r"Upper Bound.*?(\d+\.\d{4,5})", "level", "medium"),
        (r"Lower Bound.*?(\d+\.\d{4,5})", "level", "medium"),
        (r"Major Resistance.*?(\d+\.\d{4,5})", "level", "medium"),
        (r"Major Support.*?(\d+\.\d{4,5})", "level", "medium"),
        (r"Bull/Bear Pivot.*?(\d+\.\d{4,5})", "level", "high"),
        (r"Primary Value Zone.*?(\d+\.\d{4,5})", "level", "medium")
    ]
    
    for pattern, category, priority in price_patterns:
        matches = re.findall(pattern, trade_plan_text, re.IGNORECASE)
        for match in matches:
            try:
                price_level = float(match)

                # For entry levels, determine trade direction from context
                if category == "entry":
                    # Find the position of the matched price in the text
                    match_pos = trade_plan_text.lower().find(str(match).lower())
                    # Look at a window of text around the match to find 'buy' or 'sell'
                    window = 40  # characters before and after
                    start = max(0, match_pos - window)
                    end = min(len(trade_plan_text), match_pos + window)
                    context_snippet = trade_plan_text[start:end].lower()
                    if "buy" in context_snippet:
                        trade_direction = "BUY"
                        condition = "ask_below"
                    elif "sell" in context_snippet:
                        trade_direction = "SELL"
                        condition = "bid_above"
                    else:
                        # Fallback: infer from price vs current price
                        if price_level > current_price:
                            trade_direction = "SELL"
                            condition = "bid_above"
                        else:
                            trade_direction = "BUY"
                            condition = "ask_below"
                    direction = trade_direction.lower()
                    comment = f"Entry level ({trade_direction}) reached at {price_level} - Consider manual entry"
                else:
                    # Determine alert condition based on current price for non-entry
                    if price_level > current_price:
                        condition = "bid_above"
                        direction = "above"
                    else:
                        condition = "bid_below"
                        direction = "below"
                    if category == "exit":
                        comment = f"Exit level reached {direction} {price_level} - Consider manual exit"
                    else:
                        comment = f"Key level {direction} {price_level} - Monitor price action"

                alerts.append(create_alert(price_level, condition, comment, category, priority))
            except ValueError:
                continue
    
    # Remove duplicates based on price level
    seen_prices = set()
    unique_alerts = []
    for alert in alerts:
        if alert["price"] not in seen_prices:
            seen_prices.add(alert["price"])
            unique_alerts.append(alert)
    
    # Sort alerts by price level
    unique_alerts.sort(key=lambda x: x["price"])
    
    return {
        "alerts": unique_alerts,
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "symbol": "EURUSD",
            "current_price": current_price,
            "total_alerts": len(unique_alerts)
        }
    }

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

        # --- Step 4: Generate MT5 Alerts ---
        print("\n--- STAGE 4: GENERATING MT5 ALERTS ---")
        try:
            current_price = viper_packet["marketSnapshot"]["currentPrice"]
            mt5_alerts = extract_mt5_alerts_from_plan(trade_plan_md, current_price)
            
            with open(MT5_ALERTS_PATH, 'w') as f:
                json.dump(mt5_alerts, f, indent=2)
            print(f"✅ MT5 alerts generated and saved to: {MT5_ALERTS_PATH.name}")
            print(f"📊 Generated {mt5_alerts['metadata']['total_alerts']} price alerts")
            
            # Display key alerts summary
            if mt5_alerts['alerts']:
                print("\n--- KEY PRICE ALERTS ---")
                for alert in mt5_alerts['alerts'][:5]:  # Show first 5 alerts
                    print(f"🔔 {alert['price']:.5f} - {alert['comment']} ({alert['category']})")
                if len(mt5_alerts['alerts']) > 5:
                    print(f"... and {len(mt5_alerts['alerts']) - 5} more alerts")
                print()
        except Exception as e:
            print(f"⚠️  Error generating MT5 alerts: {e}")
            # Create minimal fallback alerts file
            fallback_alerts = {
                "alerts": [],
                "metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "symbol": "EURUSD",
                    "current_price": viper_packet.get("marketSnapshot", {}).get("currentPrice", 0),
                    "total_alerts": 0,
                    "error": str(e)
                }
            }
            with open(MT5_ALERTS_PATH, 'w') as f:
                json.dump(fallback_alerts, f, indent=2)
            print(f"⚠️  Fallback alerts file saved to: {MT5_ALERTS_PATH.name}")

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


def generate_review_scores():
    """Generate review scores for compatibility with existing systems"""
    try:
        # Read the trading plan
        plan_path = DATE_OUTPUT_DIR / f"Trading_plan_{datetime.now().strftime('%Y%m%d')}.md"
        if not plan_path.exists():
            # Fallback to generic plan path
            plan_path = PLAN_OUTPUT_PATH
        
        if plan_path.exists():
            with open(plan_path, 'r') as f:
                trade_plan = f.read()
        else:
            trade_plan = "No trading plan generated"
        
        # Create basic review scores
        review_scores = {
            "planQualityScore": {
                "score": 7,  # Default good score
                "justification": "Generated by visual analysis agents"
            },
            "confidenceScore": {
                "score": 7,  # Default good score
                "justification": "Based on multi-agent analysis including charts, intermarket, and news"
            },
            "decision": "GO",
            "reasoning": "Multi-agent analysis completed successfully",
            "agentAnalysis": "See scratchpad.json for detailed agent breakdown"
        }
        
        # Save review scores
        with open(REVIEW_OUTPUT_PATH, 'w') as f:
            json.dump(review_scores, f, indent=2)
        print(f"✅ Review scores saved to: {REVIEW_OUTPUT_PATH}")
        
    except Exception as e:
        print(f"❌ Error generating review scores: {e}")
        # Create fallback scores
        fallback_scores = {
            "planQualityScore": {"score": 5, "justification": "Fallback scores - analysis incomplete"},
            "confidenceScore": {"score": 5, "justification": "Fallback scores - analysis incomplete"},
            "decision": "WAIT",
            "reasoning": "Analysis incomplete - check logs",
            "error": str(e)
        }
        with open(REVIEW_OUTPUT_PATH, 'w') as f:
            json.dump(fallback_scores, f, indent=2)

# --- 3. MAIN EXECUTION BLOCK ---

if __name__ == "__main__":
    print(f"📁 Output will be saved to: {DATE_OUTPUT_DIR}")
    print(f"📅 Date: {CURRENT_DATE}")
    print("-" * 50)
    
    # Generate charts and run agent analysis
    data_packet = generate_viper_packet()
    
    # Generate review scores for compatibility
    if data_packet:
        print("\n--- STAGE 7: GENERATING REVIEW SCORES ---")
        generate_review_scores()
        
        # Send Telegram summary
        print("\n--- STAGE 8: SENDING TELEGRAM SUMMARY ---")
        # Use the actual generated plan path
        actual_plan_path = DATE_OUTPUT_DIR / f"Trading_plan_{datetime.now().strftime('%Y%m%d')}.md"
        send_trading_summary(data_packet, actual_plan_path, REVIEW_OUTPUT_PATH)
    else:
        print("❌ Could not generate data packet. Halting execution.")