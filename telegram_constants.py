#!/usr/bin/env python3
"""
Shared constants for Telegram messaging system.
Centralizes visual indicators and psychology tips to avoid duplication across files.
"""

VISUAL_INDICATORS = {
    "emojis": {
        "go": "✅",
        "wait": "⏸️", 
        "skip": "❌",
        "low_risk": "🟢",
        "medium_risk": "🟡", 
        "high_risk": "🔴",
        "bullish": "📈",
        "bearish": "📉",
        "neutral": "➡️",
        "decision": "🎯",
        "market": "📊",
        "action": "⚡"
    }
}

PSYCHOLOGY_TIPS = {
    'calm_market': [
        "🎯 Patience in calm markets prevents overtrading",
        "📊 Stick to your position sizing rules",
        "🕰️ Quality setups are worth waiting for"
    ],
    'volatile_market': [
        "🛡️ Reduce position size in high volatility", 
        "⏱️ Wait for clear setups - volatility creates traps",
        "📏 Wider stops may be needed in volatile conditions"
    ],
    'winning_streak': [
        "📈 Stay humble - markets can change quickly",
        "💰 Consider banking some profits",
        "🎲 Don't increase risk due to recent wins"
    ],
    'losing_streak': [
        "🔄 Trust your system through drawdowns", 
        "📉 Reduce size until confidence returns",
        "📖 Review your rules and stick to them"
    ],
    'general': [
        "💡 Plan your trade, trade your plan",
        "⚖️ Risk management is profit management", 
        "🎯 Focus on process, not outcomes",
        "📈 Consistency beats perfection"
    ]
}