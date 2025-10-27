"""
GemEx UI Setup Checker

Quick diagnostic script to verify the system is ready for the web UI.
Run this before launching the UI for the first time.
"""

import sys
import os
from pathlib import Path

def check_mark(condition):
    return "✅" if condition else "❌"

def warning_mark(condition):
    return "✅" if condition else "⚠️ "

print("═" * 60)
print("GemEx UI Setup Checker")
print("═" * 60)
print()

# Check Python version
print("🐍 Python Environment")
print("-" * 60)
python_version = sys.version_info
python_ok = python_version.major == 3 and python_version.minor >= 8
print(f"{check_mark(python_ok)} Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
if not python_ok:
    print("   ⚠️  Python 3.8+ recommended (3.12+ preferred)")
print()

# Check dependencies
print("📦 Required Packages")
print("-" * 60)

packages = {
    'streamlit': 'Web UI framework',
    'pandas': 'Data processing',
    'numpy': 'Numerical computations',
    'google.generativeai': 'AI integration',
    'yfinance': 'Market data',
    'mplfinance': 'Chart generation',
    'matplotlib': 'Visualization',
}

missing_packages = []
for package, description in packages.items():
    try:
        __import__(package)
        print(f"✅ {package:25} - {description}")
    except ImportError:
        print(f"❌ {package:25} - {description} (NOT INSTALLED)")
        missing_packages.append(package)

if missing_packages:
    print()
    print("⚠️  Missing packages detected. Install with:")
    print("   pip install -r requirements.txt")
print()

# Check API keys
print("🔑 API Configuration")
print("-" * 60)
gemini_key = os.environ.get("GEMINI_API_KEY")
telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
telegram_chat = os.environ.get("TELEGRAM_CHAT_ID")

print(f"{check_mark(bool(gemini_key))} GEMINI_API_KEY: {'Configured' if gemini_key else 'Not set'}")
if not gemini_key:
    print("   ⚠️  Required for AI features. Set with:")
    print("      export GEMINI_API_KEY='your_key_here'")

print(f"{warning_mark(bool(telegram_token))} TELEGRAM_BOT_TOKEN: {'Configured' if telegram_token else 'Not set (optional)'}")
print(f"{warning_mark(bool(telegram_chat))} TELEGRAM_CHAT_ID: {'Configured' if telegram_chat else 'Not set (optional)'}")
print()

# Check directories
print("📁 Directory Structure")
print("-" * 60)

directories = {
    'data': 'Playbook storage',
    'data/playbook_history': 'Playbook backups',
    'trading_session': 'Trading sessions',
    'weekly_reflections': 'Weekly analysis',
}

for dir_path, description in directories.items():
    exists = Path(dir_path).exists()
    print(f"{warning_mark(exists)} {dir_path:25} - {description}")

print()

# Check for essential files
print("📄 Essential Files")
print("-" * 60)

files = {
    'app.py': 'Web UI application',
    'ace_main.py': 'ACE orchestration',
    'ace_components.py': 'ACE components',
    'market_planner.py': 'Market analysis',
    'requirements.txt': 'Dependencies list',
}

for file_path, description in files.items():
    exists = Path(file_path).exists()
    print(f"{check_mark(exists)} {file_path:25} - {description}")

print()

# Check for existing data
print("💾 Existing Data")
print("-" * 60)

playbook_exists = Path('data/playbook.json').exists()
print(f"{warning_mark(playbook_exists)} Playbook: {'Found' if playbook_exists else 'Not initialized (will be created)'}")

trading_sessions = list(Path('trading_session').glob('*/')) if Path('trading_session').exists() else []
print(f"{warning_mark(len(trading_sessions) > 0)} Trading Sessions: {len(trading_sessions)} found")

reflections = list(Path('weekly_reflections').glob('*.json')) if Path('weekly_reflections').exists() else []
print(f"{warning_mark(len(reflections) > 0)} Weekly Reflections: {len(reflections)} found")

print()

# Overall status
print("═" * 60)
print("Overall Status")
print("═" * 60)

critical_ok = python_ok and not missing_packages and Path('app.py').exists()
functional_ok = critical_ok and bool(gemini_key)

if functional_ok:
    print("✅ System is fully operational!")
    print()
    print("🚀 Launch the UI with:")
    print("   ./launch_ui.sh")
    print("   or: streamlit run app.py")
elif critical_ok:
    print("⚠️  System is partially operational")
    print()
    print("The UI will launch, but AI features require GEMINI_API_KEY")
    print()
    print("Set your API key:")
    print("   export GEMINI_API_KEY='your_key_here'")
    print()
    print("Then launch with:")
    print("   ./launch_ui.sh")
else:
    print("❌ System setup incomplete")
    print()
    if missing_packages:
        print("Install missing packages:")
        print("   pip install -r requirements.txt")
    if not Path('app.py').exists():
        print("Missing essential files. Please verify your installation.")

print()
print("═" * 60)
print("📖 For more help, see UI_GUIDE.md")
print("═" * 60)
