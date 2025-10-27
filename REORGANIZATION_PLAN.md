# GemEx Repository Reorganization Plan

## Current Issues

1. **Root directory clutter**: 30+ files in the root
2. **Mixed file types**: Python, shell scripts, markdown docs all mixed
3. **No clear separation**: Core code, utilities, docs, and scripts all together
4. **Difficult navigation**: Hard to find specific files quickly

## Proposed Structure

```
GemEx/
├── README.md                          # Main documentation (keep in root)
├── LICENSE                            # License (keep in root)
├── requirements.txt                   # Dependencies (keep in root)
├── .env.example                       # Environment template (keep in root)
├── .gitignore                         # Git config (keep in root)
│
├── src/                               # 🆕 Core application code
│   ├── __init__.py
│   ├── market_planner.py             # Main market analysis
│   ├── ace_main.py                   # ACE orchestration
│   ├── ace_components.py             # ACE components
│   ├── ace_integrated.py             # ACE integration
│   ├── ace_persistence.py            # ACE persistence
│   ├── ace_demo.py                   # ACE demo
│   ├── prompts.py                    # LLM prompts
│   ├── telegram_constants.py         # Telegram config
│   └── app.py                        # Web UI (Streamlit)
│
├── scripts/                           # 🆕 Shell scripts and utilities
│   ├── launch_ui.sh                  # UI launcher
│   ├── run_daily.sh                  # Daily cycle runner
│   ├── verify_setup.sh               # Setup verification
│   ├── cleanup_artifacts.sh          # Cleanup utility
│   └── check_ui_setup.py             # UI setup checker
│
├── docs/                              # 🆕 Documentation
│   ├── README.md                     # Docs index
│   ├── ACE_README.md                 # ACE system docs
│   ├── UI_GUIDE.md                   # Web UI guide
│   ├── UI_QUICK_REFERENCE.md         # UI quick ref
│   ├── UI_VISUAL_GUIDE.md            # UI visual guide
│   ├── UI_DESIGN_SUMMARY.md          # UI design docs
│   ├── PRODUCTION_GUIDE.md           # Production deployment
│   ├── TESTING_GUIDE.md              # Testing guide
│   ├── SIMULATION_MODE_GUIDE.md      # Simulation mode
│   ├── DAILY_WORKFLOW.md             # Daily workflow
│   ├── IMPLEMENTATION_SUMMARY.md     # Implementation notes
│   ├── ARTIFACT_PERSISTENCE.md       # Artifact docs
│   ├── VALIDATION_REPORT.md          # Validation report
│   └── TRADING_JOURNAL_TEMPLATE.md   # Journal template
│
├── tests/                             # Unit tests (already exists)
│   ├── test_ace_components.py
│   ├── test_ace_system.py
│   ├── test_environment.py
│   └── ...
│
├── data/                              # Data storage (already exists)
│   ├── playbook.json
│   └── playbook_history/
│
├── trading_session/                   # Trading sessions (already exists)
│   └── YYYY_MM_DD/
│
├── weekly_reflections/                # Weekly reflections (already exists)
│   └── *.json
│
├── .github/                           # GitHub Actions (already exists)
│   └── workflows/
│
└── gemx_venv/                         # Virtual env (already exists)
```

## Benefits of New Structure

### 1. Clear Separation of Concerns
- **src/** - All Python application code
- **scripts/** - All shell scripts and utilities
- **docs/** - All documentation
- **tests/** - All test files
- **data/** - All data files

### 2. Easier Navigation
- Find scripts quickly in `scripts/`
- Find docs quickly in `docs/`
- Find core code quickly in `src/`

### 3. Cleaner Root Directory
- Only 6 essential files in root
- Everything else organized into subdirectories
- Much easier to understand project structure

### 4. Better for Collaboration
- New contributors can find things easily
- Standard Python project structure
- Clear module organization

### 5. Easier Imports
```python
# Old (current)
from ace_components import load_playbook

# New
from src.ace_components import load_playbook
```

## Migration Steps

### Phase 1: Create New Directories (Low Risk)
```bash
mkdir -p src
mkdir -p scripts
mkdir -p docs
```

### Phase 2: Move Python Files to src/
```bash
mv ace_*.py src/
mv market_planner.py src/
mv prompts.py src/
mv telegram_constants.py src/
mv app.py src/
```

### Phase 3: Move Shell Scripts to scripts/
```bash
mv *.sh scripts/
mv check_ui_setup.py scripts/  # Python utility script
```

### Phase 4: Move Documentation to docs/
```bash
mv *_README.md docs/
mv *_GUIDE.md docs/
mv *_SUMMARY.md docs/
mv *_TEMPLATE.md docs/
mv *_WORKFLOW.md docs/
mv *_REPORT.md docs/
# Keep README.md and LICENSE in root
```

### Phase 5: Update Imports
- Update import statements in all Python files
- Update script paths in shell scripts
- Update paths in GitHub Actions workflows

### Phase 6: Update Documentation
- Update all documentation with new paths
- Update README.md with new structure
- Update UI documentation

### Phase 7: Test Everything
```bash
# Test imports
python -c "from src.ace_components import load_playbook"

# Test scripts
scripts/verify_setup.sh

# Test UI
scripts/launch_ui.sh

# Test daily cycle
python src/ace_main.py --cycle daily

# Run tests
python -m pytest tests/
```

## Alternative: Minimal Reorganization (Recommended for Now)

If full reorganization seems too disruptive, start with just organizing scripts:

```
GemEx/
├── scripts/                           # 🆕 Just scripts
│   ├── launch_ui.sh
│   ├── run_daily.sh
│   ├── verify_setup.sh
│   ├── cleanup_artifacts.sh
│   └── check_ui_setup.py
│
└── [everything else stays in root]
```

This gives you immediate organization benefits with minimal disruption.

## Recommendation

**Start with Minimal Reorganization:**
1. Create `scripts/` folder
2. Move `.sh` files and `check_ui_setup.py` to `scripts/`
3. Update paths in documentation and scripts
4. Test everything works

**Later (optional):**
1. Create `src/` and `docs/` when you have time
2. Move files gradually
3. Update imports and paths
4. Full professional structure

## Breaking Changes

### If You Reorganize Scripts Only:
- ✅ Minimal breaking changes
- Update: `./launch_ui.sh` → `./scripts/launch_ui.sh`
- Update: `./run_daily.sh` → `./scripts/run_daily.sh`
- Update documentation references

### If You Reorganize Everything:
- ⚠️ More breaking changes
- All import statements need updating
- GitHub Actions workflows need updating
- All script paths need updating
- All documentation needs updating

## Decision Points

### Keep Scripts in Root If:
- You run them very frequently from command line
- You want minimal typing
- You prioritize convenience over organization

### Move Scripts to scripts/ If:
- You want a cleaner root directory
- You value organization over convenience
- You're okay typing `scripts/` prefix

### Full Reorganization If:
- You're building for long-term maintenance
- You expect multiple contributors
- You want professional project structure
- You have time to update all references

## My Recommendation

**Go with scripts/ folder now:**
```bash
# Simple, immediate benefit, minimal disruption
mkdir scripts
mv *.sh scripts/
mv check_ui_setup.py scripts/

# Create convenience symlinks in root (optional)
ln -s scripts/launch_ui.sh launch_ui.sh
ln -s scripts/run_daily.sh run_daily.sh
```

This gives you:
- ✅ Cleaner root directory
- ✅ Organized scripts location
- ✅ Backward compatibility via symlinks
- ✅ Minimal testing required
- ✅ Easy to undo if needed

What do you think? Should I implement the minimal reorganization (scripts folder) or the full reorganization?
