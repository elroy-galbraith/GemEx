# GemEx Scripts Directory

This folder contains all shell scripts and utility programs for the GemEx trading system.

## Scripts

### 🚀 `launch_ui.sh`
**Purpose:** Launch the Streamlit web interface

**Usage:**
```bash
./scripts/launch_ui.sh
# Or use the root symlink:
./launch_ui.sh
```

**Features:**
- Checks/activates virtual environment
- Verifies Streamlit installation
- Checks API key configuration
- Launches dashboard automatically

**When to use:** Any time you want to use the web UI

---

### 📅 `run_daily.sh`
**Purpose:** Run the daily trading cycle

**Usage:**
```bash
./scripts/run_daily.sh
# Or use the root symlink:
./run_daily.sh
```

**Features:**
- Activates virtual environment
- Runs ACE daily cycle
- Displays formatted output
- Shows session summary

**When to use:** Every trading day before market opens (8:00 AM EST)

---

### ✅ `verify_setup.sh`
**Purpose:** Verify system setup and configuration

**Usage:**
```bash
./scripts/verify_setup.sh
```

**Features:**
- Checks Python version
- Verifies dependencies
- Tests API keys
- Runs comprehensive tests
- Reports system health

**When to use:**
- After initial installation
- When troubleshooting issues
- Before important trading sessions
- After system updates

---

### 🧹 `cleanup_artifacts.sh`
**Purpose:** Clean up old session data and artifacts

**Usage:**
```bash
./scripts/cleanup_artifacts.sh
```

**Features:**
- Removes old trading sessions
- Archives weekly reflections
- Cleans up temporary files
- Frees disk space

**When to use:**
- When disk space is low
- Monthly maintenance
- Before major updates

---

### 🔍 `check_ui_setup.py`
**Purpose:** Diagnostic tool for web UI setup

**Usage:**
```bash
python scripts/check_ui_setup.py
```

**Features:**
- Checks Python environment
- Verifies package installation
- Checks API configuration
- Validates directory structure
- Reports overall status

**When to use:**
- Before launching UI for the first time
- When UI won't start
- When troubleshooting issues

---

## Convenience Symlinks

For frequently used scripts, there are symlinks in the root directory:

```
GemEx/
├── launch_ui.sh -> scripts/launch_ui.sh
├── run_daily.sh -> scripts/run_daily.sh
└── scripts/
    ├── launch_ui.sh (actual file)
    ├── run_daily.sh (actual file)
    ├── verify_setup.sh
    ├── cleanup_artifacts.sh
    └── check_ui_setup.py
```

This allows you to run:
- `./launch_ui.sh` instead of `./scripts/launch_ui.sh`
- `./run_daily.sh` instead of `./scripts/run_daily.sh`

---

## Adding New Scripts

When adding new scripts to this folder:

1. **Make it executable:**
   ```bash
   chmod +x scripts/your_script.sh
   ```

2. **Add proper header:**
   ```bash
   #!/bin/bash
   # Description: What this script does
   # Usage: ./scripts/your_script.sh
   ```

3. **Update this README** with script documentation

4. **Consider adding a symlink** if it's frequently used:
   ```bash
   ln -s scripts/your_script.sh your_script.sh
   ```

---

## Script Organization

### Shell Scripts (.sh)
- Use bash shebang: `#!/bin/bash`
- Include descriptive comments
- Handle errors gracefully
- Provide user feedback

### Python Utilities (.py)
- Follow project coding style
- Include docstrings
- Handle missing dependencies
- Provide clear error messages

---

## Best Practices

1. **Run from project root:**
   ```bash
   # Good
   cd /path/to/GemEx
   ./scripts/run_daily.sh
   
   # Avoid
   cd scripts
   ./run_daily.sh
   ```

2. **Use absolute paths in scripts** when referencing files

3. **Check for virtual environment** before running Python code

4. **Provide feedback** to users (echoing progress, errors, etc.)

5. **Exit with proper codes:**
   - 0 for success
   - Non-zero for errors

---

## Troubleshooting

### Script won't run
```bash
# Make it executable
chmod +x scripts/script_name.sh
```

### "Command not found"
```bash
# Run from project root
cd /path/to/GemEx
./scripts/script_name.sh
```

### Symlink broken
```bash
# Remove old symlink
rm launch_ui.sh

# Create new one
ln -s scripts/launch_ui.sh launch_ui.sh
```

---

## Migration Notes

**Previous Location:** All scripts were in the root directory

**New Location:** All scripts are now in `scripts/`

**Compatibility:** Symlinks maintain backward compatibility for frequently used scripts

**Updated References:** All documentation has been updated to reference `scripts/` folder
