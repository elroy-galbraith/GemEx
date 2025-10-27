#!/bin/bash
# Quick verification script to test if GemEx ACE system is properly configured

set -e  # Exit on any error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║      GemEx ACE System - Quick Verification Script         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "ace_main.py" ]; then
    echo "❌ Error: Please run this script from the GemEx root directory"
    exit 1
fi

# Step 1: Check virtual environment
echo "📦 Step 1: Checking virtual environment..."
if [ -d "gemx_venv" ]; then
    echo "✅ Virtual environment found"
else
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv gemx_venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source gemx_venv/bin/activate

# Step 2: Check Python version
echo ""
echo "🐍 Step 2: Checking Python version..."
PYTHON_VERSION=$(python --version)
echo "✅ $PYTHON_VERSION"

# Step 3: Check dependencies
echo ""
echo "📚 Step 3: Checking dependencies..."
if python -c "import pandas, numpy, yfinance, google.generativeai" 2>/dev/null; then
    echo "✅ All required packages are installed"
else
    echo "⚠️  Some packages are missing. Installing dependencies..."
    pip install -q -r requirements.txt
    echo "✅ Dependencies installed"
fi

# Step 4: Check environment variables
echo ""
echo "🔑 Step 4: Checking environment variables..."
if [ -f ".env" ]; then
    echo "✅ .env file found"
    if grep -q "GEMINI_API_KEY=your_gemini_api_key_here" .env 2>/dev/null; then
        echo "⚠️  Warning: GEMINI_API_KEY appears to be placeholder. Update .env with your actual API key."
    else
        echo "✅ GEMINI_API_KEY appears to be configured"
    fi
else
    echo "⚠️  .env file not found. Copy .env.example to .env and configure it."
    echo "   Run: cp .env.example .env"
fi

# Step 5: Run unit tests
echo ""
echo "🧪 Step 5: Running unit tests..."
if python tests/test_ace_system.py; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed. Check output above."
    exit 1
fi

# Step 6: Check directory structure
echo ""
echo "📁 Step 6: Verifying directory structure..."
for dir in "data" "data/playbook_history" "trading_session" "weekly_reflections"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir exists"
    else
        echo "⚠️  Creating $dir..."
        mkdir -p "$dir"
        echo "✅ $dir created"
    fi
done

# Step 7: Check if playbook exists
echo ""
echo "📖 Step 7: Checking playbook..."
if [ -f "data/playbook.json" ]; then
    VERSION=$(python -c "import json; print(json.load(open('data/playbook.json'))['metadata']['version'])" 2>/dev/null)
    BULLETS=$(python -c "import json; print(json.load(open('data/playbook.json'))['metadata']['total_bullets'])" 2>/dev/null)
    echo "✅ Playbook exists (v$VERSION, $BULLETS bullets)"
else
    echo "⚠️  Playbook will be created on first run"
fi

# Final summary
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    VERIFICATION COMPLETE                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "✅ System is ready to use!"
echo ""
echo "Next steps:"
echo "1. Ensure GEMINI_API_KEY is set in .env file"
echo "2. Run daily cycle: python ace_main.py --cycle daily"
echo "3. Run weekly cycle: python ace_main.py --cycle weekly"
echo ""
echo "For detailed testing, see TESTING_GUIDE.md"
