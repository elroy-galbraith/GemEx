"""
ACE (Agentic Context Engineering) Components for Forex Trading System

This module implements the core ACE architecture:
- Playbook management (load, save, initialize)
- Generator (trading plan creation)
- Executor (simulated trade execution)
- Reflector (weekly performance analysis)
- Curator (playbook updates)
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Optional imports - only needed when actually running LLM components
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Configuration ---
PLAYBOOK_PATH = Path("data/playbook.json")
PLAYBOOK_HISTORY_DIR = Path("data/playbook_history")
WEEKLY_REFLECTIONS_DIR = Path("weekly_reflections")
TRADING_SESSIONS_DIR = Path("trading_session")

# Ensure directories exist
for directory in [PLAYBOOK_PATH.parent, PLAYBOOK_HISTORY_DIR, WEEKLY_REFLECTIONS_DIR, TRADING_SESSIONS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# --- Playbook Management ---

def initialize_playbook() -> Dict[str, Any]:
    """
    Create initial playbook with basic trading rules.
    This is only run once on first execution.
    """
    initial_playbook = {
        "metadata": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            "total_bullets": 5
        },
        "sections": {
            "strategies_and_hard_rules": [
                {
                    "id": "strat-001",
                    "content": "Only trade during NY session (9:30 AM - 4:00 PM EST)",
                    "helpful_count": 0,
                    "harmful_count": 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "last_used": None
                },
                {
                    "id": "strat-002",
                    "content": "Avoid trading 30min before/after high-impact news",
                    "helpful_count": 0,
                    "harmful_count": 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "last_used": None
                },
                {
                    "id": "strat-003",
                    "content": "Minimum risk-reward ratio: 1:1.5",
                    "helpful_count": 0,
                    "harmful_count": 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "last_used": None
                }
            ],
            "useful_code_and_templates": [
                {
                    "id": "code-001",
                    "content": "Position sizing: (account_balance * risk_pct) / (entry - stop)",
                    "helpful_count": 0,
                    "harmful_count": 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "last_used": None
                }
            ],
            "troubleshooting_and_pitfalls": [
                {
                    "id": "pit-001",
                    "content": "Low liquidity after 3:00 PM EST - avoid new entries",
                    "helpful_count": 0,
                    "harmful_count": 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "last_used": None
                }
            ]
        }
    }
    
    return initial_playbook


def load_playbook() -> Dict[str, Any]:
    """Load playbook from file, or create if doesn't exist."""
    if PLAYBOOK_PATH.exists():
        with open(PLAYBOOK_PATH, 'r') as f:
            return json.load(f)
    else:
        print("📚 Initializing new playbook...")
        playbook = initialize_playbook()
        save_playbook(playbook)
        return playbook


def save_playbook(playbook: Dict[str, Any]) -> None:
    """Save playbook to file and create versioned backup."""
    # Update metadata
    playbook["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
    
    # Save current playbook
    with open(PLAYBOOK_PATH, 'w') as f:
        json.dump(playbook, f, indent=2)
    
    # Create versioned backup
    version = playbook["metadata"]["version"]
    backup_path = PLAYBOOK_HISTORY_DIR / f"playbook_v{version}.json"
    with open(backup_path, 'w') as f:
        json.dump(playbook, f, indent=2)
    
    print(f"✅ Playbook saved (version {version})")


def generate_bullet_id(section: str) -> str:
    """Generate a unique bullet ID."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    prefix = section[:4]
    return f"{prefix}-{timestamp}"


# --- Generator Component ---

GENERATOR_SYSTEM_PROMPT = """
You are an educational market analysis assistant studying EURUSD trading patterns for learning purposes.

**IMPORTANT**: This is a paper trading simulation for educational purposes only. 
Generate an analytical trading plan as a learning exercise, not financial advice.

**Your Inputs**:
1. **Playbook**: A reference collection of historical trading patterns and observations
2. **Market Data**: Current price action, correlations (DXY, SPX500, US10Y), economic events
3. **Chart Context**: Technical analysis from 15M/1H/4H timeframes for pattern recognition

**Your Educational Task**:
Analyze current market structure and identify what hypothetical conditions would suggest different trading biases.
This is a simulation exercise for the NY session timeframe (9:30 AM - 4:00 PM EST).

**Analysis Output Format** (strict JSON):
```json
{
  "date": "2025-01-05",
  "bias": "bullish_pattern|bearish_pattern|neutral_observation",
  "entry_zone": [1.0485, 1.0495],
  "stop_loss": 1.0465,
  "take_profit_1": 1.0535,
  "take_profit_2": 1.0565,
  "position_size_pct": 0.75,
  "risk_reward": "1:2.5",
  "rationale": "Educational analysis: DXY correlation pattern + SPX intermarket relationship + EMA structure observation",
  "playbook_bullets_used": ["strat-001", "code-001", "pit-003"],
  "confidence": "high_probability|medium_probability|low_probability"
}
```

**Educational Analysis Guidelines**:
1. **Reference Historical Patterns**: Cite which playbook bullet IDs match current market structure
2. **Risk-Reward Analysis**: For learning purposes, analyze hypothetical position sizing (0.75% max) and minimum 1:1.5 R:R ratios
3. **Event Awareness**: Note proximity to high-impact economic events and how that affects pattern analysis
4. **Pattern Recognition**: If market structure doesn't match historical playbook patterns, document as "neutral_observation"
5. **Probability Assessment**: Rate the historical probability of this pattern (high/medium/low) based on playbook data

**Learning Process**:
1. Review playbook for similar historical market structures and their outcomes
2. Identify any historical pitfalls or risk factors documented in the playbook
3. Construct analysis that demonstrates understanding of pattern recognition
4. Cite specific bullet IDs to show analytical reasoning based on historical data

Educational Focus: This simulation helps understand how historical patterns in the playbook relate to current market structure. 
All analysis is hypothetical and for learning pattern recognition skills.
"""


def run_generator(playbook: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a trading plan using the playbook and current market data.
    
    Args:
        playbook: Current playbook state
        market_data: Market snapshot including price, trends, news
        
    Returns:
        Trading plan as a dictionary
    """
    # Check if Gemini is available
    if not GENAI_AVAILABLE:
        print("⚠️  Google Generative AI not available - using mock plan")
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "bias": "neutral",
            "rationale": "Google Generative AI not installed - install with: pip install google-generativeai",
            "confidence": "low",
            "playbook_bullets_used": []
        }
    
    # Configure Gemini
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  GEMINI_API_KEY not found - using mock plan")
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "bias": "neutral",
            "rationale": "GEMINI_API_KEY not configured",
            "confidence": "low",
            "playbook_bullets_used": []
        }
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-pro")
    
    # Format playbook for prompt
    playbook_text = json.dumps(playbook, indent=2)
    market_text = json.dumps(market_data, indent=2)
    
    user_prompt = f"""
        Analyze EURUSD market structure for this educational simulation exercise:

        **HISTORICAL PLAYBOOK REFERENCE**:
        {playbook_text}

        **CURRENT MARKET DATA FOR ANALYSIS**:
        {market_text}

        Provide your educational market analysis in strict JSON format as specified in the system prompt. 
        No markdown formatting, just raw JSON output.
        Remember: This is a paper trading simulation for learning pattern recognition.
        """
    
    try:
        # Generate plan
        response = model.generate_content(
            [{"role": "user", "parts": [{"text": GENERATOR_SYSTEM_PROMPT}]},
             {"role": "model", "parts": [{"text": "I understand. I will analyze market patterns and provide educational trading simulations in strict JSON format, referencing historical playbook data for learning purposes."}]},
             {"role": "user", "parts": [{"text": user_prompt}]}],
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 2048,
            }
        )
        
        # Check for blocked response
        if not response.parts:
            # Response was blocked by safety filters
            finish_reason = getattr(response.candidates[0], 'finish_reason', None) if response.candidates else None
            safety_ratings = getattr(response.candidates[0], 'safety_ratings', []) if response.candidates else []
            
            error_msg = f"Response blocked (finish_reason={finish_reason})"
            if safety_ratings:
                blocked_categories = [r.category for r in safety_ratings if r.blocked]
                if blocked_categories:
                    error_msg += f" - Blocked categories: {blocked_categories}"
            
            print(f"⚠️  {error_msg}")
            print("⚠️  This is likely due to Gemini's safety filters. Using neutral plan.")
            
            return {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "bias": "neutral",
                "rationale": "Response blocked by safety filters - regenerate with adjusted prompt",
                "confidence": "low",
                "playbook_bullets_used": [],
                "error": error_msg
            }
        
        # Parse response
        plan_text = response.text.strip()
        
        # Save raw response for debugging
        debug_dir = Path("trading_session") / "debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        debug_file = debug_dir / f"raw_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(debug_file, 'w') as f:
                f.write(plan_text)
            print(f"📝 Raw response saved to: {debug_file}")
        except Exception as debug_e:
            print(f"⚠️  Could not save debug file: {debug_e}")
        
        # Clean JSON if wrapped in markdown
        if plan_text.startswith("```"):
            # Split by ``` and get the content between markers
            parts = plan_text.split("```")
            if len(parts) >= 2:
                plan_text = parts[1]
                # Remove language identifier if present (json, JSON, etc.)
                if plan_text.strip().startswith("json"):
                    plan_text = plan_text.strip()[4:].strip()
                elif plan_text.strip().startswith("JSON"):
                    plan_text = plan_text.strip()[4:].strip()
        
        # Remove any trailing markdown markers
        if plan_text.endswith("```"):
            plan_text = plan_text[:-3].strip()
        
        # Try to parse JSON
        try:
            plan = json.loads(plan_text)
        except json.JSONDecodeError as json_err:
            print(f"❌ JSON parsing failed: {json_err}")
            print(f"📄 First 500 chars of response: {plan_text[:500]}")
            print(f"📄 Last 200 chars of response: {plan_text[-200:]}")
            raise  # Re-raise to be caught by outer exception handler
        
        # Update playbook usage
        if "playbook_bullets_used" in plan:
            for bullet_id in plan["playbook_bullets_used"]:
                update_bullet_usage(playbook, bullet_id)
        
        return plan
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        print(f"⚠️  The AI model returned malformed JSON. This is saved in the debug folder for inspection.")
        # Return neutral plan with detailed error
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "bias": "neutral",
            "rationale": f"JSON parsing error: {str(e)}. The AI response was malformed. Check debug logs.",
            "confidence": "low",
            "playbook_bullets_used": [],
            "error": f"JSONDecodeError: {str(e)}"
        }
    except Exception as e:
        print(f"❌ Error generating plan: {e}")
        # Return neutral plan
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "bias": "neutral",
            "rationale": f"Error generating plan: {e}",
            "confidence": "low",
            "playbook_bullets_used": [],
            "error": str(e)
        }


def update_bullet_usage(playbook: Dict[str, Any], bullet_id: str) -> None:
    """Update last_used timestamp for a bullet."""
    for section in playbook["sections"].values():
        for bullet in section:
            if bullet["id"] == bullet_id:
                bullet["last_used"] = datetime.now(timezone.utc).isoformat()
                return


# --- Executor Component ---

def simulate_trade_execution(trading_plan: Dict[str, Any], market_price_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Simulate trade execution for paper trading.
    
    Args:
        trading_plan: The trading plan to execute
        market_price_history: Optional list of price ticks for simulation
        
    Returns:
        Trade log with execution details
    """
    trade_log = {
        "plan_id": trading_plan.get("date", datetime.now().strftime("%Y-%m-%d")),
        "execution": None,
        "feedback": {
            "entry_quality": "not_triggered",
            "exit_timing": "n/a",
            "unexpected_events": [],
            "playbook_bullets_feedback": {}
        }
    }
    
    # If no trade zone (neutral bias), mark as no trade
    # Handle both old format ("neutral") and new format ("neutral_observation")
    bias = trading_plan.get("bias", "neutral")
    if "neutral" in bias.lower() or "entry_zone" not in trading_plan:
        trade_log["execution"] = {
            "status": "no_trade",
            "reason": "Neutral bias or no entry criteria met"
        }
        return trade_log
    
    # For now, create a simulated outcome based on plan quality
    # In production, this would monitor real price action
    confidence = trading_plan.get("confidence", "medium")
    
    # Simulate based on confidence (this is placeholder logic)
    if confidence == "high":
        outcome = "win" if hash(trading_plan["date"]) % 3 != 0 else "loss"
    elif confidence == "medium":
        outcome = "win" if hash(trading_plan["date"]) % 2 == 0 else "loss"
    else:
        outcome = "loss"
    
    # Create simulated execution
    if "entry_zone" in trading_plan:
        entry_price = sum(trading_plan["entry_zone"]) / 2
        
        if outcome == "win":
            exit_price = trading_plan.get("take_profit_1", entry_price * 1.002)
            pnl_pips = int((exit_price - entry_price) * 10000)
        else:
            exit_price = trading_plan.get("stop_loss", entry_price * 0.998)
            pnl_pips = int((exit_price - entry_price) * 10000)
        
        trade_log["execution"] = {
            "entry_time": f"{trading_plan['date']}T14:00:00Z",
            "entry_price": entry_price,
            "exit_time": f"{trading_plan['date']}T16:30:00Z",
            "exit_price": exit_price,
            "pnl_pips": pnl_pips,
            "pnl_usd": pnl_pips * 10,  # Assuming $10/pip
            "outcome": outcome
        }
        
        trade_log["feedback"]["entry_quality"] = "good" if confidence != "low" else "poor"
        trade_log["feedback"]["exit_timing"] = "good" if outcome == "win" else "stopped_out"
    
    return trade_log


def save_trade_log(trade_log: Dict[str, Any], date: str = None) -> None:
    """Save trade log to the appropriate daily folder."""
    if date is None:
        date = datetime.now().strftime("%Y_%m_%d")
    
    session_dir = TRADING_SESSIONS_DIR / date
    session_dir.mkdir(parents=True, exist_ok=True)
    
    log_path = session_dir / "trade_log.json"
    with open(log_path, 'w') as f:
        json.dump(trade_log, f, indent=2)
    
    print(f"✅ Trade log saved to: {log_path}")


# --- Reflector Component ---

REFLECTOR_SYSTEM_PROMPT = """
You are a trading performance analyst. Your job is to review a week of trading logs and identify patterns that should update the Playbook.

**Your Inputs**:
1. **Weekly Trade Logs**: 5 days of trading plans and execution outcomes
2. **Current Playbook**: The existing collection of strategies and lessons

**Your Task**:
Analyze the week's performance and suggest specific playbook updates.

**Output Format** (strict JSON):
```json
{
  "week_ending": "2025-01-05",
  "summary": {
    "total_trades": 5,
    "win_rate": 0.60,
    "avg_rr": 1.8,
    "total_pips": 85
  },
  "insights": [
    {
      "type": "success_pattern|failure_pattern|execution_issue|outdated_rule|playbook_validation",
      "observation": "Description of what was observed",
      "suggested_action": "add_bullet|review_bullet|increment_helpful|increment_harmful",
      "section": "strategies_and_hard_rules|useful_code_and_templates|troubleshooting_and_pitfalls",
      "content": "New bullet content if adding",
      "bullet_id": "Existing bullet ID if updating",
      "priority": "high|medium|low",
      "confidence": "Description of evidence strength"
    }
  ],
  "recommendations": [
    "Key recommendations for next week"
  ],
  "market_regime_notes": "Description of market conditions this week"
}
```

**Analysis Guidelines**:
1. **Success Patterns**: What worked consistently? (≥2 wins with same setup)
2. **Failure Patterns**: What caused losses? (≥2 losses with same mistake)
3. **Execution Quality**: Did we follow the plan? Exit too early/late?
4. **Playbook Validation**: Which bullets were helpful vs. harmful?
5. **Outdated Rules**: Which bullets no longer apply?

Return ONLY the JSON reflection. No markdown formatting.
"""


def run_reflector(weekly_logs: List[Dict[str, Any]], current_playbook: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze weekly performance and generate insights.
    
    Args:
        weekly_logs: List of trade logs from the week
        current_playbook: Current playbook state
        
    Returns:
        Reflection with insights and suggested updates
    """
    # Check if Gemini is available
    if not GENAI_AVAILABLE:
        print("⚠️  Google Generative AI not available - using basic reflection")
        return {
            "week_ending": datetime.now().strftime("%Y-%m-%d"),
            "summary": {"total_trades": len(weekly_logs)},
            "insights": [],
            "recommendations": ["Install google-generativeai to enable AI-powered reflections"],
            "market_regime_notes": "Analysis unavailable without Gemini"
        }
    
    # Configure Gemini
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  GEMINI_API_KEY not found - using basic reflection")
        return {
            "week_ending": datetime.now().strftime("%Y-%m-%d"),
            "summary": {"total_trades": len(weekly_logs)},
            "insights": [],
            "recommendations": ["Configure GEMINI_API_KEY to enable AI-powered reflections"],
            "market_regime_notes": "Analysis unavailable without API key"
        }
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    logs_text = json.dumps(weekly_logs, indent=2)
    playbook_text = json.dumps(current_playbook, indent=2)
    
    user_prompt = f"""
Analyze this week's trading performance:

**WEEKLY TRADE LOGS**:
{logs_text}

**CURRENT PLAYBOOK**:
{playbook_text}

Provide insights and suggested playbook updates as JSON.
"""
    
    try:
        response = model.generate_content(
            [{"role": "user", "parts": [{"text": REFLECTOR_SYSTEM_PROMPT}]},
             {"role": "model", "parts": [{"text": "I will analyze the trading logs and provide structured JSON insights."}]},
             {"role": "user", "parts": [{"text": user_prompt}]}],
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 4096,
            }
        )
        
        reflection_text = response.text.strip()
        
        # Save raw response for debugging
        debug_dir = Path("trading_session") / "debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        debug_file = debug_dir / f"reflection_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(debug_file, 'w') as f:
                f.write(reflection_text)
            print(f"📝 Raw reflection saved to: {debug_file}")
        except Exception as debug_e:
            print(f"⚠️  Could not save debug file: {debug_e}")
        
        # Clean JSON if wrapped in markdown
        if reflection_text.startswith("```"):
            parts = reflection_text.split("```")
            if len(parts) >= 2:
                reflection_text = parts[1]
                if reflection_text.strip().startswith("json"):
                    reflection_text = reflection_text.strip()[4:].strip()
                elif reflection_text.strip().startswith("JSON"):
                    reflection_text = reflection_text.strip()[4:].strip()
        
        # Remove any trailing markdown markers
        if reflection_text.endswith("```"):
            reflection_text = reflection_text[:-3].strip()
        
        # Try to parse JSON
        try:
            reflection = json.loads(reflection_text)
        except json.JSONDecodeError as json_err:
            print(f"❌ JSON parsing failed: {json_err}")
            print(f"📄 First 500 chars of response: {reflection_text[:500]}")
            print(f"📄 Last 200 chars of response: {reflection_text[-200:]}")
            raise  # Re-raise to be caught by outer exception handler
        
        return reflection
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error in reflection: {e}")
        print(f"⚠️  The AI model returned malformed JSON. Check debug folder for inspection.")
        return {
            "week_ending": datetime.now().strftime("%Y-%m-%d"),
            "summary": {"total_trades": len(weekly_logs), "error": f"JSONDecodeError: {str(e)}"},
            "insights": [],
            "recommendations": ["Error parsing reflection - AI returned malformed JSON"],
            "market_regime_notes": "Analysis incomplete due to parsing error"
        }
    except Exception as e:
        print(f"❌ Error generating reflection: {e}")
        # Return minimal reflection
        return {
            "week_ending": datetime.now().strftime("%Y-%m-%d"),
            "summary": {"total_trades": len(weekly_logs), "error": str(e)},
            "insights": [],
            "recommendations": ["Error generating reflection - review manually"],
            "market_regime_notes": "Analysis incomplete"
        }


def save_reflection(reflection: Dict[str, Any]) -> None:
    """Save weekly reflection to file."""
    week_ending = reflection.get("week_ending", datetime.now().strftime("%Y-%m-%d"))
    # Convert date to week number format
    date_obj = datetime.strptime(week_ending, "%Y-%m-%d")
    week_str = date_obj.strftime("%Y_W%U")
    
    reflection_path = WEEKLY_REFLECTIONS_DIR / f"{week_str}_reflection.json"
    with open(reflection_path, 'w') as f:
        json.dump(reflection, f, indent=2)
    
    print(f"✅ Weekly reflection saved to: {reflection_path}")


# --- Curator Component ---

def run_curator(reflection: Dict[str, Any], current_playbook: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update playbook based on Reflector insights.
    
    Uses deterministic logic to:
    - Add new bullets
    - Update helpful/harmful counts
    - Remove outdated bullets
    
    Args:
        reflection: Weekly reflection with insights
        current_playbook: Current playbook state
        
    Returns:
        Updated playbook
    """
    updated_playbook = json.loads(json.dumps(current_playbook))  # Deep copy
    
    for insight in reflection.get("insights", []):
        action = insight.get("suggested_action")
        
        if action == "add_bullet":
            # Add new bullet to specified section
            section_name = insight.get("section", "strategies_and_hard_rules")
            if section_name in updated_playbook["sections"]:
                new_bullet = {
                    "id": generate_bullet_id(section_name),
                    "content": insight.get("content", ""),
                    "helpful_count": 0,
                    "harmful_count": 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "last_used": None
                }
                updated_playbook["sections"][section_name].append(new_bullet)
                updated_playbook["metadata"]["total_bullets"] += 1
                print(f"➕ Added bullet: {new_bullet['id']}")
        
        elif action == "increment_helpful":
            # Increment helpful count for bullet
            bullet_id = insight.get("bullet_id")
            if bullet_id:
                for section in updated_playbook["sections"].values():
                    for bullet in section:
                        if bullet["id"] == bullet_id:
                            bullet["helpful_count"] += 1
                            print(f"👍 Incremented helpful count for {bullet_id}")
        
        elif action == "increment_harmful":
            # Increment harmful count for bullet
            bullet_id = insight.get("bullet_id")
            if bullet_id:
                for section in updated_playbook["sections"].values():
                    for bullet in section:
                        if bullet["id"] == bullet_id:
                            bullet["harmful_count"] += 1
                            print(f"👎 Incremented harmful count for {bullet_id}")
        
        elif action == "review_bullet":
            # Mark for manual review (could auto-remove if harmful >> helpful)
            bullet_id = insight.get("bullet_id")
            print(f"⚠️  Bullet {bullet_id} flagged for review")
    
    # Prune bullets where harmful_count > helpful_count + 2
    for section_name, section in updated_playbook["sections"].items():
        original_count = len(section)
        updated_playbook["sections"][section_name] = [
            bullet for bullet in section
            if bullet["harmful_count"] <= bullet["helpful_count"] + 2
        ]
        removed_count = original_count - len(updated_playbook["sections"][section_name])
        if removed_count > 0:
            updated_playbook["metadata"]["total_bullets"] -= removed_count
            print(f"🗑️  Removed {removed_count} harmful bullets from {section_name}")
    
    # Increment version
    current_version = float(updated_playbook["metadata"]["version"])
    updated_playbook["metadata"]["version"] = f"{current_version + 0.1:.1f}"
    
    return updated_playbook


def load_trade_logs_for_week(week_ending_date: str = None) -> List[Dict[str, Any]]:
    """
    Load all trade logs for a given week.
    
    Args:
        week_ending_date: Date string in format YYYY-MM-DD, defaults to current week
        
    Returns:
        List of trade logs
    """
    if week_ending_date is None:
        week_ending_date = datetime.now().strftime("%Y-%m-%d")
    
    end_date = datetime.strptime(week_ending_date, "%Y-%m-%d")
    
    # Get Monday of that week (assuming week_ending_date is Friday)
    # Go back to find Monday
    days_back = end_date.weekday()  # 0 = Monday
    start_date = end_date - timedelta(days=days_back)
    
    weekly_logs = []
    
    # Load logs for each day of the week
    for i in range(5):  # Monday to Friday
        date = start_date + timedelta(days=i)
        date_str = date.strftime("%Y_%m_%d")
        log_path = TRADING_SESSIONS_DIR / date_str / "trade_log.json"
        
        if log_path.exists():
            with open(log_path, 'r') as f:
                log = json.load(f)
                weekly_logs.append(log)
    
    print(f"📊 Loaded {len(weekly_logs)} trade logs for week ending {week_ending_date}")
    return weekly_logs
