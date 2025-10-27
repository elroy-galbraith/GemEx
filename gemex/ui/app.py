"""
GemEx Trading System - Streamlit Dashboard UI

A simple, elegant web interface for the ACE Forex Trading System.
Provides controls for daily/weekly cycles, playbook management, and performance tracking.
"""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import sys
from typing import Dict, Any, List

# Page configuration
st.set_page_config(
    page_title="GemEx Trading System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .danger-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Paths
PLAYBOOK_PATH = Path("data/playbook.json")
TRADING_SESSIONS_DIR = Path("trading_session")
WEEKLY_REFLECTIONS_DIR = Path("weekly_reflections")

# --- Helper Functions ---

def load_playbook() -> Dict[str, Any]:
    """Load the current playbook."""
    if PLAYBOOK_PATH.exists():
        with open(PLAYBOOK_PATH, 'r') as f:
            return json.load(f)
    return None

def get_latest_session() -> tuple[Path, Dict]:
    """Get the most recent trading session data."""
    if not TRADING_SESSIONS_DIR.exists():
        return None, None
    
    session_dirs = sorted([d for d in TRADING_SESSIONS_DIR.iterdir() if d.is_dir()], reverse=True)
    if not session_dirs:
        return None, None
    
    latest_dir = session_dirs[0]
    
    # Try to load trading plan
    plan_files = list(latest_dir.glob("trading_plan.json"))
    if plan_files:
        with open(plan_files[0], 'r') as f:
            plan_data = json.load(f)
        return latest_dir, plan_data
    
    return latest_dir, None

def get_latest_reflection() -> Dict:
    """Get the most recent weekly reflection."""
    if not WEEKLY_REFLECTIONS_DIR.exists():
        return None
    
    reflection_files = sorted(WEEKLY_REFLECTIONS_DIR.glob("*.json"), reverse=True)
    if not reflection_files:
        return None
    
    with open(reflection_files[0], 'r') as f:
        return json.load(f)

def get_recent_sessions(n: int = 5) -> List[tuple]:
    """Get N most recent trading sessions."""
    if not TRADING_SESSIONS_DIR.exists():
        return []
    
    session_dirs = sorted([d for d in TRADING_SESSIONS_DIR.iterdir() if d.is_dir()], reverse=True)[:n]
    sessions = []
    
    for session_dir in session_dirs:
        log_files = list(session_dir.glob("trade_log.json"))
        if log_files:
            with open(log_files[0], 'r') as f:
                log_data = json.load(f)
            sessions.append((session_dir.name, log_data))
    
    return sessions

def run_command(command: List[str]) -> tuple[bool, str]:
    """Run a shell command and return success status and output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out after 5 minutes"
    except Exception as e:
        return False, str(e)

# --- Sidebar ---

with st.sidebar:
    st.markdown("### 🎯 GemEx Control Panel")
    
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["Dashboard", "Daily Cycle", "Weekly Reflection", "Playbook", "Charts & Data"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("### 📊 Quick Stats")
    playbook = load_playbook()
    if playbook:
        st.metric("Playbook Version", playbook['metadata']['version'])
        st.metric("Total Bullets", playbook['metadata']['total_bullets'])
    else:
        st.info("No playbook found. Run Daily Cycle to initialize.")
    
    latest_session_dir, _ = get_latest_session()
    if latest_session_dir:
        st.metric("Last Session", latest_session_dir.name.replace("_", "-"))
    
    st.markdown("---")
    
    # System Status
    st.markdown("### ⚙️ System Status")
    
    # Check API key
    import os
    if os.environ.get("GEMINI_API_KEY"):
        st.success("✓ Gemini API Connected")
    else:
        st.error("✗ Gemini API Not Configured")
    
    # Check Telegram
    if os.environ.get("TELEGRAM_BOT_TOKEN"):
        st.success("✓ Telegram Configured")
    else:
        st.warning("⚠ Telegram Not Configured")

# --- Main Content ---

if page == "Dashboard":
    st.markdown('<p class="main-header">📊 GemEx Trading Dashboard</p>', unsafe_allow_html=True)
    st.markdown("**AI-Powered Forex Trading Analysis System**")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("System Status", "🟢 Active")
    
    with col2:
        playbook = load_playbook()
        if playbook:
            st.metric("Playbook Bullets", playbook['metadata']['total_bullets'])
        else:
            st.metric("Playbook Bullets", "N/A")
    
    with col3:
        recent_sessions = get_recent_sessions()
        st.metric("Recent Sessions", len(recent_sessions))
    
    with col4:
        reflection = get_latest_reflection()
        if reflection:
            st.metric("Last Reflection", reflection.get('week_ending', 'N/A'))
        else:
            st.metric("Last Reflection", "None")
    
    st.markdown("---")
    
    # Latest Trading Plan
    st.subheader("📋 Latest Trading Plan")
    latest_session_dir, plan_data = get_latest_session()
    
    if plan_data:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**Date:** {plan_data.get('date', 'N/A')}")
            st.markdown(f"**Bias:** {plan_data.get('bias', 'N/A').upper()}")
            st.markdown(f"**Confidence:** {plan_data.get('confidence', 'N/A').upper()}")
            
            with st.expander("View Rationale"):
                st.markdown(plan_data.get('rationale', 'No rationale available'))
        
        with col2:
            # Display chart if available
            chart_files = list(latest_session_dir.glob("EURUSD_4H_*.png"))
            if chart_files:
                st.image(str(chart_files[0]), caption="EURUSD 4H Chart")
    else:
        st.info("No trading plan available. Run the Daily Cycle to generate one.")
    
    st.markdown("---")
    
    # Recent Performance
    st.subheader("📈 Recent Performance")
    recent_sessions = get_recent_sessions(5)
    
    if recent_sessions:
        performance_data = []
        for date, log in recent_sessions:
            execution = log.get('execution', {})
            performance_data.append({
                'Date': date.replace('_', '-'),
                'Outcome': execution.get('outcome', 'N/A'),
                'Pips': execution.get('pnl_pips', 0),
                'USD': f"${execution.get('pnl_usd', 0):.2f}",
                'Quality': execution.get('execution_quality', 'N/A')
            })
        
        df = pd.DataFrame(performance_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Simple stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            wins = sum(1 for _, log in recent_sessions if log.get('execution', {}).get('outcome') == 'win')
            st.metric("Wins", wins)
        
        with col2:
            losses = sum(1 for _, log in recent_sessions if log.get('execution', {}).get('outcome') == 'loss')
            st.metric("Losses", losses)
        
        with col3:
            total_pips = sum(log.get('execution', {}).get('pnl_pips', 0) for _, log in recent_sessions)
            st.metric("Total Pips", f"{total_pips:+.1f}")
    else:
        st.info("No recent performance data available.")

elif page == "Daily Cycle":
    st.markdown('<p class="main-header">🌅 Daily Trading Cycle</p>', unsafe_allow_html=True)
    st.markdown("Run the daily trading analysis and plan generation.")
    
    st.markdown("---")
    
    # Explanation
    with st.expander("ℹ️ How Daily Cycle Works"):
        st.markdown("""
        The Daily Cycle performs the following steps:
        
        1. **Load Playbook** - Retrieves the current trading strategies
        2. **Gather Market Data** - Fetches EURUSD, DXY, SPX500, US10Y data and news
        3. **Generate Charts** - Creates technical analysis charts for multiple timeframes
        4. **Create Trading Plan** - AI generates a trading plan using playbook + market data
        5. **Simulate Execution** - Paper trades the plan and logs outcomes
        6. **Send Notifications** - Sends plan to Telegram (if configured)
        
        **Best Time to Run:** Before NY session (8:00 AM EST)
        """)
    
    st.markdown("---")
    
    # Run button
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("▶️ Run Daily Cycle", type="primary", use_container_width=True):
            with st.spinner("Running daily cycle... This may take 1-2 minutes"):
                success, output = run_command([sys.executable, "ace_main.py", "--cycle", "daily"])
                
                if success:
                    st.success("✅ Daily cycle completed successfully!")
                    st.rerun()
                else:
                    st.error("❌ Daily cycle failed")
                
                with st.expander("View Console Output"):
                    st.code(output)
    
    with col2:
        st.info("💡 The daily cycle will generate charts, create a trading plan, and simulate execution.")
    
    st.markdown("---")
    
    # Display today's session if it exists
    today = datetime.now().strftime("%Y_%m_%d")
    today_session_dir = TRADING_SESSIONS_DIR / today
    
    if today_session_dir.exists():
        st.subheader("📅 Today's Session")
        
        # Load trading plan
        plan_files = list(today_session_dir.glob("trading_plan.json"))
        if plan_files:
            with open(plan_files[0], 'r') as f:
                plan = json.load(f)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Trading Plan")
                st.json(plan)
            
            with col2:
                st.markdown("### Charts")
                chart_files = sorted(today_session_dir.glob("*.png"))
                for chart_file in chart_files[:3]:  # Show first 3 charts
                    st.image(str(chart_file), caption=chart_file.stem)
        
        # Load trade log
        log_files = list(today_session_dir.glob("trade_log.json"))
        if log_files:
            with open(log_files[0], 'r') as f:
                log = json.load(f)
            
            st.markdown("### Execution Log")
            st.json(log)

elif page == "Weekly Reflection":
    st.markdown('<p class="main-header">🔄 Weekly Reflection</p>', unsafe_allow_html=True)
    st.markdown("Analyze weekly performance and update the playbook.")
    
    st.markdown("---")
    
    # Explanation
    with st.expander("ℹ️ How Weekly Reflection Works"):
        st.markdown("""
        The Weekly Reflection performs the following steps:
        
        1. **Load Trade Logs** - Gathers all trading logs from the past week
        2. **Analyze Performance** - AI identifies patterns, successes, and failures
        3. **Generate Insights** - Creates actionable recommendations
        4. **Update Playbook** - Adds/removes/modifies trading strategies
        5. **Save History** - Creates versioned backup of playbook
        
        **Best Time to Run:** Friday EOD (5:00 PM EST)
        """)
    
    st.markdown("---")
    
    # Run button
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("▶️ Run Weekly Reflection", type="primary", use_container_width=True):
            with st.spinner("Running weekly reflection... This may take 2-3 minutes"):
                success, output = run_command([sys.executable, "ace_main.py", "--cycle", "weekly"])
                
                if success:
                    st.success("✅ Weekly reflection completed successfully!")
                    st.rerun()
                else:
                    st.error("❌ Weekly reflection failed")
                
                with st.expander("View Console Output"):
                    st.code(output)
    
    with col2:
        st.info("💡 The weekly reflection analyzes your trading performance and evolves the playbook.")
    
    st.markdown("---")
    
    # Display latest reflection
    st.subheader("📊 Latest Reflection")
    reflection = get_latest_reflection()
    
    if reflection:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Summary")
            summary = reflection.get('summary', {})
            st.metric("Total Trades", summary.get('total_trades', 0))
            st.metric("Win Rate", f"{summary.get('win_rate', 0):.1f}%")
            st.metric("Total P&L (pips)", f"{summary.get('total_pnl_pips', 0):+.1f}")
        
        with col2:
            st.markdown("### Market Regime")
            st.markdown(reflection.get('market_regime_notes', 'No notes available'))
        
        st.markdown("### Insights")
        insights = reflection.get('insights', [])
        if insights:
            for i, insight in enumerate(insights, 1):
                st.markdown(f"**{i}.** {insight}")
        else:
            st.info("No insights available")
        
        st.markdown("### Recommendations")
        recommendations = reflection.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"**{i}.** {rec}")
        else:
            st.info("No recommendations available")
    else:
        st.info("No reflection data available. Run the Weekly Reflection to generate one.")

elif page == "Playbook":
    st.markdown('<p class="main-header">📚 Trading Playbook</p>', unsafe_allow_html=True)
    st.markdown("View and understand your evolving trading strategies.")
    
    st.markdown("---")
    
    playbook = load_playbook()
    
    if playbook:
        # Metadata
        metadata = playbook['metadata']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Version", metadata['version'])
        with col2:
            st.metric("Total Bullets", metadata['total_bullets'])
        with col3:
            updated = datetime.fromisoformat(metadata['last_updated'].replace('Z', '+00:00'))
            st.metric("Last Updated", updated.strftime("%Y-%m-%d"))
        
        st.markdown("---")
        
        # Sections
        sections = playbook['sections']
        
        # Strategies and Hard Rules
        st.subheader("🎯 Strategies and Hard Rules")
        strategies = sections.get('strategies_and_hard_rules', [])
        
        if strategies:
            for strategy in strategies:
                with st.expander(f"**{strategy['id']}** - {strategy['content'][:60]}..."):
                    st.markdown(f"**Content:** {strategy['content']}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Helpful", strategy.get('helpful_count', 0))
                    with col2:
                        st.metric("Harmful", strategy.get('harmful_count', 0))
                    with col3:
                        last_used = strategy.get('last_used')
                        if last_used:
                            used_date = datetime.fromisoformat(last_used.replace('Z', '+00:00'))
                            st.metric("Last Used", used_date.strftime("%Y-%m-%d"))
                        else:
                            st.metric("Last Used", "Never")
        else:
            st.info("No strategies available")
        
        # Useful Code and Templates
        st.subheader("💻 Useful Code and Templates")
        templates = sections.get('useful_code_and_templates', [])
        
        if templates:
            for template in templates:
                with st.expander(f"**{template['id']}** - {template['content'][:60]}..."):
                    st.code(template['content'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Helpful", template.get('helpful_count', 0))
                    with col2:
                        st.metric("Harmful", template.get('harmful_count', 0))
        else:
            st.info("No templates available")
        
        # Troubleshooting and Pitfalls
        st.subheader("⚠️ Troubleshooting and Pitfalls")
        pitfalls = sections.get('troubleshooting_and_pitfalls', [])
        
        if pitfalls:
            for pitfall in pitfalls:
                with st.expander(f"**{pitfall['id']}** - {pitfall['content'][:60]}..."):
                    st.markdown(f"**Content:** {pitfall['content']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Helpful", pitfall.get('helpful_count', 0))
                    with col2:
                        st.metric("Harmful", pitfall.get('harmful_count', 0))
        else:
            st.info("No pitfalls documented")
        
        st.markdown("---")
        
        # Raw JSON viewer
        with st.expander("📄 View Raw Playbook JSON"):
            st.json(playbook)
    else:
        st.warning("No playbook found. Run the Daily Cycle to initialize the playbook.")

elif page == "Charts & Data":
    st.markdown('<p class="main-header">📈 Charts & Market Data</p>', unsafe_allow_html=True)
    st.markdown("View technical analysis charts and market data from recent sessions.")
    
    st.markdown("---")
    
    # Session selector
    if TRADING_SESSIONS_DIR.exists():
        session_dirs = sorted([d.name for d in TRADING_SESSIONS_DIR.iterdir() if d.is_dir()], reverse=True)
        
        if session_dirs:
            selected_session = st.selectbox(
                "Select Trading Session",
                session_dirs,
                format_func=lambda x: x.replace("_", "-")
            )
            
            session_path = TRADING_SESSIONS_DIR / selected_session
            
            # Display charts
            st.subheader("📊 Technical Charts")
            
            chart_files = sorted(session_path.glob("*.png"))
            
            if chart_files:
                # Group charts by type
                timeframes = {}
                for chart_file in chart_files:
                    name = chart_file.stem
                    if "EURUSD_" in name:
                        tf = name.split("_")[1]  # Extract timeframe
                        if tf not in timeframes:
                            timeframes[tf] = []
                        timeframes[tf].append(chart_file)
                
                # Display in tabs
                tabs = st.tabs(list(timeframes.keys()))
                
                for tab, tf in zip(tabs, timeframes.keys()):
                    with tab:
                        for chart_file in timeframes[tf]:
                            st.image(str(chart_file), caption=chart_file.stem, use_container_width=True)
            else:
                st.info("No charts available for this session")
            
            st.markdown("---")
            
            # Display data files
            st.subheader("📄 Session Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Viper packet
                viper_packet_path = session_path / "viper_packet.json"
                if viper_packet_path.exists():
                    with st.expander("🐍 Viper Packet (Market Data)"):
                        with open(viper_packet_path, 'r') as f:
                            viper_data = json.load(f)
                        st.json(viper_data)
                
                # Trading plan
                plan_files = list(session_path.glob("trading_plan.json"))
                if plan_files:
                    with st.expander("📋 Trading Plan"):
                        with open(plan_files[0], 'r') as f:
                            plan_data = json.load(f)
                        st.json(plan_data)
            
            with col2:
                # Trade log
                log_files = list(session_path.glob("trade_log.json"))
                if log_files:
                    with st.expander("📊 Trade Log"):
                        with open(log_files[0], 'r') as f:
                            log_data = json.load(f)
                        st.json(log_data)
                
                # Review scores
                review_path = session_path / "review_scores.json"
                if review_path.exists():
                    with st.expander("⭐ Review Scores"):
                        with open(review_path, 'r') as f:
                            review_data = json.load(f)
                        st.json(review_data)
        else:
            st.info("No trading sessions found. Run the Daily Cycle to create one.")
    else:
        st.warning("Trading sessions directory not found.")

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>GemEx - AI-Powered Forex Trading Analysis System</p>
    <p>Built with Streamlit | For Educational Purposes Only</p>
</div>
""", unsafe_allow_html=True)
