"""
ACE (Agentic Context Engineering) Trading System

This package implements the ACE architecture for forex trading:
- Playbook management (load, save, initialize)
- Generator (trading plan creation)
- Executor (simulated trade execution)
- Reflector (weekly performance analysis)
- Curator (playbook updates)
"""

from gemex.ace.components import (
    load_playbook,
    save_playbook,
    initialize_playbook,
    run_generator,
    simulate_trade_execution,
    save_trade_log,
    run_reflector,
    save_reflection,
    run_curator,
    load_trade_logs_for_week,
)

__all__ = [
    "load_playbook",
    "save_playbook",
    "initialize_playbook",
    "run_generator",
    "simulate_trade_execution",
    "save_trade_log",
    "run_reflector",
    "save_reflection",
    "run_curator",
    "load_trade_logs_for_week",
]
