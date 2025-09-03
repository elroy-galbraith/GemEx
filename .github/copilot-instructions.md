# GemEx - AI-Powered Forex Trading Analysis System

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Critical Network Dependency Warning

**IMPORTANT**: This repository has known PyPI connectivity issues in CI/containerized environments. The `pip install -r requirements.txt` command frequently fails with read timeouts due to network limitations. This is documented and expected behavior.

## Working Effectively

### Environment Setup
- **CRITICAL TIMEOUT WARNING**: Package installation can take 5-15 minutes and may fail due to network issues. Set timeout to 20+ minutes and NEVER CANCEL.
- **Virtual Environment Setup**:
  ```bash
  python -m venv gemx_venv                                    # Takes ~3 seconds
  source gemx_venv/bin/activate                               # On Windows: gemx_venv\Scripts\activate
  ```

### Dependency Installation (Multiple Approaches Required)

**Approach 1: System Packages (Most Reliable)**
```bash
sudo apt-get update                                           # Takes 2-3 minutes
sudo apt-get install -y python3-pandas python3-numpy python3-scipy python3-requests python3-bs4 python3-pip
                                                             # Takes 3-5 minutes, NEVER CANCEL
```

**Approach 2: pip install (Frequently Fails)**
```bash
pip install --timeout 300 --retries 3 -r requirements.txt   # Takes 5-15 minutes, OFTEN FAILS with network timeouts
```

**Expected pip failure message**: `ReadTimeoutError: HTTPSConnectionPool(host='pypi.org', port=443): Read timed out.`

### Environment Variables (Required for Full Functionality)
```bash
export GEMINI_API_KEY="your_api_key_here"
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"          # Optional for notifications
export TELEGRAM_CHAT_ID="your_telegram_chat_id"             # Optional for notifications
```

### Application Execution
```bash
python market_planner.py                                     # Takes 30-60 seconds, NEVER CANCEL
```

## Build and Test Process

### Pre-execution Validation
```bash
# Verify Python and basic packages
python --version                                              # Should show Python 3.12+
python -c "import pandas; import numpy; print('Core packages OK')"

# Use the comprehensive environment test script
python test_environment.py                                   # Comprehensive environment validation

# Check for critical missing packages (expected to fail without pip install)
python -c "import yfinance; import google.generativeai; print('All packages available')"
```

### Expected Output Structure
After successful execution, check these locations:
```
trading_session/
├── YYYY_MM_DD/                    # Date-based subdirectories (e.g., 2025_09_03)
│   ├── viper_packet.json         # Raw market data analysis
│   ├── trade_plan.md             # Generated trading strategy
│   └── review_scores.json        # AI quality assessment
```

### Manual Validation Scenarios
**CRITICAL**: After making changes, always test these scenarios:

1. **Environment Setup Test**:
   ```bash
   python -c "import sys; print('Python:', sys.version)"
   ```

2. **Data Processing Test** (when packages available):
   ```bash
   python -c "
   import pandas as pd
   import numpy as np
   print('Data packages working')
   df = pd.DataFrame({'test': [1, 2, 3]})
   print('DataFrame created:', len(df))
   "
   ```

3. **Output Directory Test**:
   ```bash
   mkdir -p trading_session
   ls -la trading_session/
   ```

## Key Project Components

### Main Application Files
- **`market_planner.py`** - Main entry point, orchestrates entire trading analysis pipeline
- **`prompts.py`** - System prompts for AI strategy generation and review
- **`requirements.txt`** - Python dependencies (50 packages)

### Core Dependencies
**Available via system packages:**
- pandas (data manipulation)
- numpy (numerical computations)  
- scipy (signal processing, peak detection)
- requests (HTTP requests)
- beautifulsoup4 (HTML parsing)

**Requires pip install (often fails):**
- yfinance (Yahoo Finance market data)
- google-generativeai (Gemini AI integration)
- cloudscraper (Economic calendar scraping)
- python-dotenv (Environment variable management)

### GitHub Actions Integration
- **Workflow file**: `.github/workflows/daily-trading-analysis.yml`
- **Schedule**: Runs at 7:00 PM JST (10:00 AM UTC) on weekdays
- **Manual trigger**: Available via "Run workflow" button
- **Expected secrets**: `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

## Common Tasks and Timing

### Repository Exploration
```bash
ls -la                                                        # Takes <1 second
find . -name "*.py" | head -10                              # Takes 1-2 seconds
cat README.md | head -50                                     # Takes <1 second
```

### Development Workflow
1. **Setup environment** (5-10 minutes total, may fail on pip step)
2. **Set environment variables** (<1 second)
3. **Run analysis** (30-60 seconds)
4. **Validate outputs** (5-10 seconds)

### Expected Timing Guidelines
- Virtual environment creation: 3 seconds
- System package installation: 3-5 minutes (SUCCESS)
- pip install: 5-15 minutes (FREQUENTLY FAILS)
- Application execution: 30-60 seconds
- **NEVER CANCEL any command that takes less than 20 minutes**

## Troubleshooting

### Known Issues
1. **PyPI connectivity failures**: Expected and documented. Use system packages where possible.
2. **Missing API keys**: Application will fail gracefully with clear error messages.
3. **Network timeouts**: Common in CI environments, requires retry strategies.

### Alternative Environments
- **Local development**: pip install typically works better with home internet
- **GitHub Actions**: Use cached actions/setup-python when possible
- **Docker**: Consider pre-built containers with dependencies

### Validation Commands
```bash
# Check Python environment
python --version && which python

# Test basic imports
python -c "import sys, os; print('Environment ready')"

# Check directory structure
find . -name "*.py" -o -name "*.yml" -o -name "*.md" | sort

# Verify workflows
cat .github/workflows/daily-trading-analysis.yml | grep -A5 -B5 "pip install"
```

## File Locations Reference

### Key Files
```
GemEx/
├── market_planner.py          # Main application (500 lines)
├── prompts.py                 # AI prompts (153 lines)
├── requirements.txt           # 50 Python packages
├── test_environment.py        # Environment validation script
├── README.md                  # Comprehensive documentation
├── .github/
│   └── workflows/
│       ├── daily-trading-analysis.yml    # Production workflow
│       └── test-workflow.yml             # Test workflow
└── trading_session/           # Output directory (created at runtime)
```

### Important Code Patterns
- **Error handling**: Look for try/except blocks around API calls
- **Environment variables**: Check `os.environ.get()` calls
- **File I/O**: Output files use `pathlib.Path` for cross-platform compatibility
- **Timing**: API calls and data processing can take 30-60 seconds

## Development Guidelines

### Before Making Changes
1. **Always test environment setup** with both system packages and pip
2. **Set appropriate timeouts** (20+ minutes for package installation)
3. **Never cancel long-running operations** - they may be working normally
4. **Test with and without API keys** to ensure graceful degradation

### After Making Changes
1. **Test import statements** for any new dependencies
2. **Verify output file generation** in trading_session directory
3. **Check GitHub Actions compatibility** if modifying workflows
4. **Validate with mock data** when API keys aren't available

### Environment-Specific Notes
- **CI/CD environments**: Expect pip failures, plan for system packages
- **Local development**: Usually works better for pip installations
- **Containerized environments**: Consider dependency pre-installation