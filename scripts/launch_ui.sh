#!/bin/bash

# GemEx UI Quick Start Script
# This script sets up and launches the Streamlit web interface

echo "╔════════════════════════════════════════════════════════╗"
echo "║        GemEx Trading System - Web UI Launcher         ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not detected"
    echo ""
    echo "Checking for gemx_venv..."
    
    if [ -d "gemx_venv" ]; then
        echo "✅ Found gemx_venv. Activating..."
        source gemx_venv/bin/activate
    else
        echo "❌ No virtual environment found"
        echo ""
        echo "Creating virtual environment..."
        python3 -m venv gemx_venv
        source gemx_venv/bin/activate
        echo "✅ Virtual environment created"
    fi
    echo ""
fi

# Check if streamlit is installed
echo "Checking dependencies..."
if ! python -c "import streamlit" 2>/dev/null; then
    echo "⚠️  Streamlit not found. Installing dependencies..."
    pip install -q streamlit
    echo "✅ Dependencies installed"
else
    echo "✅ Streamlit found"
fi

echo ""

# Check for API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  WARNING: GEMINI_API_KEY not set"
    echo ""
    echo "The system will work in limited mode without an API key."
    echo "To enable full functionality, set your API key:"
    echo ""
    echo "  export GEMINI_API_KEY='your_api_key_here'"
    echo ""
    echo "Or create a .env file with:"
    echo "  GEMINI_API_KEY=your_api_key_here"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ GEMINI_API_KEY configured"
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo ""
echo "🚀 Launching GemEx Web UI..."
echo ""
echo "The dashboard will open automatically in your browser."
echo "If it doesn't, navigate to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "════════════════════════════════════════════════════════"
echo ""

# Launch Streamlit - use new package structure
streamlit run gemex/ui/app.py
