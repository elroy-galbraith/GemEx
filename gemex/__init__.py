"""
GemEx - AI-Powered Forex Trading Analysis System
Package initialization for gemex trading system.
"""

__version__ = "1.0.0"

# Import ACE components for convenient access
from gemex.ace.components import (
    load_playbook,
    save_playbook,
    run_generator,
    simulate_trade_execution
)

# Import market planner functions
# Note: market_planner imports are kept minimal due to heavy dependencies
__all__ = [
    'load_playbook',
    'save_playbook', 
    'run_generator',
    'simulate_trade_execution'
]

__version__ = "1.0.0"
__author__ = "GemEx Trading System"

# Make key components easily accessible
from gemex.ace.components import (
    load_playbook,
    save_playbook,
    run_generator,
    simulate_trade_execution,
)

__all__ = [
    "load_playbook",
    "save_playbook",
    "run_generator",
    "simulate_trade_execution",
]
