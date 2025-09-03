#!/usr/bin/env python3
"""
Test script to validate GemEx environment setup without requiring full dependencies.
This can be used to test basic functionality when pip install fails.
"""

import sys
import os
from pathlib import Path

def test_environment():
    """Test basic environment setup."""
    print("=== GemEx Environment Test ===")
    
    # Test Python version
    print(f"✓ Python version: {sys.version}")
    
    # Test working directory
    print(f"✓ Working directory: {os.getcwd()}")
    
    # Test basic imports
    try:
        import pandas as pd
        print(f"✓ pandas available: {pd.__version__}")
    except ImportError:
        print("✗ pandas not available")
    
    try:
        import numpy as np
        print(f"✓ numpy available: {np.__version__}")
    except ImportError:
        print("✗ numpy not available")
    
    try:
        import requests
        print("✓ requests available")
    except ImportError:
        print("✗ requests not available")
    
    # Test optional dependencies
    optional_deps = ['yfinance', 'google.generativeai', 'cloudscraper', 'dotenv']
    available_optional = []
    missing_optional = []
    
    for dep in optional_deps:
        try:
            __import__(dep)
            available_optional.append(dep)
        except ImportError:
            missing_optional.append(dep)
    
    if available_optional:
        print(f"✓ Optional dependencies available: {', '.join(available_optional)}")
    
    if missing_optional:
        print(f"! Optional dependencies missing: {', '.join(missing_optional)}")
        print("  (This is expected if pip install failed due to network issues)")
    
    # Test output directory creation
    output_dir = Path("trading_session")
    output_dir.mkdir(exist_ok=True)
    print(f"✓ Output directory: {output_dir.absolute()}")
    
    # Test environment variables
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        print("✓ GEMINI_API_KEY is set")
    else:
        print("! GEMINI_API_KEY not set (required for full functionality)")
    
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if telegram_token:
        print("✓ TELEGRAM_BOT_TOKEN is set")
    else:
        print("! TELEGRAM_BOT_TOKEN not set (optional)")
    
    print("\n=== Test Summary ===")
    if len(missing_optional) == 0:
        print("✓ Full environment ready - you can run: python market_planner.py")
    elif len(available_optional) > 0:
        print("⚠ Partial environment - some features may not work")
    else:
        print("✗ Minimal environment - needs dependency installation")
        print("  Try: sudo apt-get install python3-pandas python3-numpy python3-scipy")
        print("  Then: pip install yfinance google-generativeai cloudscraper python-dotenv")

if __name__ == "__main__":
    test_environment()