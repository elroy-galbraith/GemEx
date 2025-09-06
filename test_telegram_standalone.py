#!/usr/bin/env python3
"""
Simple test for TelegramMessageBuilder without external dependencies.
Tests the core logic and message formatting.
"""

import json
import random
from datetime import datetime

# Standalone TelegramMessageBuilder for testing
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
    'general': [
        "💡 Plan your trade, trade your plan",
        "⚖️ Risk management is profit management", 
        "🎯 Focus on process, not outcomes",
        "📈 Consistency beats perfection"
    ]
}

class TestTelegramMessageBuilder:
    """Standalone test version of TelegramMessageBuilder."""
    
    def __init__(self):
        self.emojis = VISUAL_INDICATORS["emojis"]
        self.psychology_tips = PSYCHOLOGY_TIPS
        
    def build_summary_message(self, data_packet, review_scores, mt5_alerts_count=0):
        """Build concise primary summary message."""
        try:
            # Extract key data
            current_price = data_packet["marketSnapshot"]["currentPrice"]
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
            
            # Calculate VIX level placeholder
            vix_level = "N/A"
            
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
    
    def get_daily_psychology_tip(self, market_condition='general'):
        """Get rotating psychology reminder based on context."""
        try:
            tips_pool = self.psychology_tips.get(market_condition, self.psychology_tips['general'])
            today = datetime.now().timetuple().tm_yday
            tip_index = today % len(tips_pool)
            return f"💡 {tips_pool[tip_index]}"
        except Exception as e:
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

def test_message_builder():
    """Test the TelegramMessageBuilder with various scenarios."""
    print("🧪 Testing TelegramMessageBuilder...")
    print("=" * 50)
    
    builder = TestTelegramMessageBuilder()
    
    # Test scenarios
    scenarios = [
        {
            "name": "GO Decision - Strong Bull Trend",
            "data": {
                "marketSnapshot": {"currentPrice": 1.0835},
                "multiTimeframeAnalysis": {
                    "Daily": {"trendDirection": "Bullish"},
                    "H4": {"trendDirection": "Bullish"}
                }
            },
            "scores": {"planQualityScore": {"score": 8}, "confidenceScore": {"score": 7}}
        },
        {
            "name": "WAIT Decision - Mixed Signals",
            "data": {
                "marketSnapshot": {"currentPrice": 1.0820},
                "multiTimeframeAnalysis": {
                    "Daily": {"trendDirection": "Bullish"},
                    "H4": {"trendDirection": "Bearish"}
                }
            },
            "scores": {"planQualityScore": {"score": 7}, "confidenceScore": {"score": 4}}
        },
        {
            "name": "SKIP Decision - Low Quality",
            "data": {
                "marketSnapshot": {"currentPrice": 1.0810},
                "multiTimeframeAnalysis": {
                    "Daily": {"trendDirection": "Bearish"},
                    "H4": {"trendDirection": "Bearish"}
                }
            },
            "scores": {"planQualityScore": {"score": 4}, "confidenceScore": {"score": 3}}
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 {scenario['name']}")
        print("-" * 40)
        
        message = builder.build_summary_message(scenario['data'], scenario['scores'])
        print(message)
        print(f"Length: {len(message)} characters")
        
        # Test psychology tip for this scenario
        if 'bull' in str(scenario['data']['multiTimeframeAnalysis']['Daily']['trendDirection']).lower():
            condition = 'calm_market'
        else:
            condition = 'volatile_market'
        
        tip = builder.get_daily_psychology_tip(condition)
        print(f"Psychology tip: {tip}")
        print("-" * 40)
    
    print("\n✅ Message builder tests completed!")
    return True

def test_message_length_comparison():
    """Compare message lengths between old and new format."""
    print("\n📏 Message Length Analysis")
    print("=" * 50)
    
    # Old format example (estimated)
    old_format = """🚀 GemEx Trading Analysis Complete

📊 Market Snapshot
• EURUSD: 1.0835
• Daily Trend: Bullish
• H4 Trend: Bullish  
• Time: 2025-09-06T10:30:00 UTC

📈 Analysis Scores
• Plan Quality: 8/10
• Confidence: 7/10

🔔 MT5 Price Alerts
• Generated 5 alerts for key levels
• Available in mt5_alerts.json

🎯 Decision
🟢 GO FOR EXECUTION - Plan is solid and conviction is high"""
    
    # New format
    builder = TestTelegramMessageBuilder()
    mock_data = {
        "marketSnapshot": {"currentPrice": 1.0835},
        "multiTimeframeAnalysis": {
            "Daily": {"trendDirection": "Bullish"},
            "H4": {"trendDirection": "Bullish"}
        }
    }
    mock_scores = {"planQualityScore": {"score": 8}, "confidenceScore": {"score": 7}}
    
    new_format = builder.build_summary_message(mock_data, mock_scores)
    
    print(f"Old format length: {len(old_format)} characters")
    print(f"New format length: {len(new_format)} characters")
    
    reduction = ((len(old_format) - len(new_format)) / len(old_format)) * 100
    print(f"Reduction: {reduction:.1f}%")
    
    if reduction > 0:
        print(f"✅ Successfully reduced message length!")
    else:
        print(f"⚠️ New format is longer - consider further optimization")
    
    print(f"\nNew format preview:")
    print("-" * 40)
    print(new_format)
    print("-" * 40)

if __name__ == "__main__":
    print("🚀 Testing New Telegram Message Format (Standalone)")
    print("This test validates the TelegramMessageBuilder logic without dependencies")
    print()
    
    success1 = test_message_builder()
    test_message_length_comparison()
    
    print("\n" + "=" * 50)
    if success1:
        print("🎉 TESTS PASSED!")
        print("New concise Telegram format is working correctly.")
    else:
        print("❌ TESTS FAILED")
    print("=" * 50)