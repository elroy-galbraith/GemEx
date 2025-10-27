#!/bin/bash
# Daily Trading Cycle Runner
# Run this script every trading day to generate plans and track results

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║           GemEx ACE - Daily Trading Cycle                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get current date
TODAY=$(date +%Y_%m_%d)
TODAY_DISPLAY=$(date +"%A, %B %d, %Y")

echo "📅 Date: $TODAY_DISPLAY"
echo ""

# Activate virtual environment
if [ ! -d "gemx_venv" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "   Run: python -m venv gemx_venv"
    exit 1
fi

source gemx_venv/bin/activate

# Run daily cycle
echo "🔄 Running daily trading cycle..."
echo ""

python gemex/ace/main.py --cycle daily

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "                    📊 DAILY SUMMARY                        "
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if session directory exists
SESSION_DIR="trading_session/$TODAY"

if [ ! -d "$SESSION_DIR" ]; then
    echo "⚠️  No session directory found for today"
    exit 1
fi

# Display trading plan summary
if [ -f "$SESSION_DIR/trading_plan.json" ]; then
    echo "📋 Trading Plan:"
    echo "───────────────────────────────────────────────────────────"
    
    BIAS=$(cat "$SESSION_DIR/trading_plan.json" | python -c "import sys, json; print(json.load(sys.stdin).get('bias', 'unknown'))")
    CONFIDENCE=$(cat "$SESSION_DIR/trading_plan.json" | python -c "import sys, json; print(json.load(sys.stdin).get('confidence', 'unknown'))")
    
    echo "Bias:       $BIAS"
    echo "Confidence: $CONFIDENCE"
    
    if [ "$BIAS" != "neutral" ]; then
        ENTRY_ZONE=$(cat "$SESSION_DIR/trading_plan.json" | python -c "import sys, json; d=json.load(sys.stdin); print(f\"{d.get('entry_zone', ['N/A'])[0]:.4f} - {d.get('entry_zone', ['N/A', 'N/A'])[1]:.4f}\" if 'entry_zone' in d else 'N/A')" 2>/dev/null || echo "N/A")
        STOP_LOSS=$(cat "$SESSION_DIR/trading_plan.json" | python -c "import sys, json; d=json.load(sys.stdin); print(f\"{d.get('stop_loss', 0):.4f}\" if 'stop_loss' in d else 'N/A')" 2>/dev/null || echo "N/A")
        TP1=$(cat "$SESSION_DIR/trading_plan.json" | python -c "import sys, json; d=json.load(sys.stdin); print(f\"{d.get('take_profit_1', 0):.4f}\" if 'take_profit_1' in d else 'N/A')" 2>/dev/null || echo "N/A")
        
        echo "Entry Zone: $ENTRY_ZONE"
        echo "Stop Loss:  $STOP_LOSS"
        echo "TP1:        $TP1"
    fi
    
    echo ""
fi

# Display trade outcome
if [ -f "$SESSION_DIR/trade_log.json" ]; then
    echo "💼 Trade Execution:"
    echo "───────────────────────────────────────────────────────────"
    
    OUTCOME=$(cat "$SESSION_DIR/trade_log.json" | python -c "import sys, json; d=json.load(sys.stdin); print(d.get('execution', {}).get('outcome', d.get('execution', {}).get('status', 'unknown')))")
    
    if [ "$OUTCOME" == "win" ]; then
        PIPS=$(cat "$SESSION_DIR/trade_log.json" | python -c "import sys, json; print(json.load(sys.stdin).get('execution', {}).get('pnl_pips', 0))")
        USD=$(cat "$SESSION_DIR/trade_log.json" | python -c "import sys, json; print(json.load(sys.stdin).get('execution', {}).get('pnl_usd', 0))")
        echo "✅ WINNER! +$PIPS pips (\$$USD)"
    elif [ "$OUTCOME" == "loss" ]; then
        PIPS=$(cat "$SESSION_DIR/trade_log.json" | python -c "import sys, json; print(json.load(sys.stdin).get('execution', {}).get('pnl_pips', 0))")
        USD=$(cat "$SESSION_DIR/trade_log.json" | python -c "import sys, json; print(json.load(sys.stdin).get('execution', {}).get('pnl_usd', 0))")
        echo "❌ Loss: $PIPS pips (\$$USD)"
    elif [ "$OUTCOME" == "no_trade" ]; then
        echo "⏸️  No trade executed (neutral bias or no setup)"
    else
        echo "Status: $OUTCOME"
    fi
    
    echo ""
fi

# Display charts info
CHART_COUNT=$(ls "$SESSION_DIR"/*.png 2>/dev/null | wc -l | tr -d ' ')
if [ "$CHART_COUNT" -gt 0 ]; then
    echo "📈 Charts Generated: $CHART_COUNT files"
    echo ""
fi

# Show file locations
echo "📁 Session Files:"
echo "───────────────────────────────────────────────────────────"
echo "Plan:  $SESSION_DIR/trading_plan.md"
echo "Log:   $SESSION_DIR/trade_log.json"
echo "Data:  $SESSION_DIR/viper_packet.json"
echo ""

# Quick view command
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📖 View full plan:"
echo "   cat $SESSION_DIR/trading_plan.md"
echo ""
echo "🖼️  View charts:"
echo "   open $SESSION_DIR/*.png"
echo ""

# Check if it's Friday for weekly reflection reminder
DAY_OF_WEEK=$(date +%u)  # 1 = Monday, 5 = Friday
if [ "$DAY_OF_WEEK" == "5" ]; then
    echo "🔔 REMINDER: It's Friday!"
    echo "   Run weekly reflection: python gemex/ace/main.py --cycle weekly"
    echo ""
fi

echo "✅ Daily cycle complete!"
