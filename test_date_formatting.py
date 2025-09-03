#!/usr/bin/env python3
"""
Test date formatting logic to ensure compatibility with GitHub Actions (Linux environment)
and calendar data format.
"""

import platform
from datetime import datetime, timezone
import pandas as pd


def test_current_date_formatting():
    """Test the current platform-specific date formatting logic."""
    print("=== Current Date Formatting Test ===")
    print(f"Platform: {platform.system()}")
    
    # Current logic from market_planner.py
    if platform.system() == "Windows":
        today_str = datetime.now(timezone.utc).strftime('%a %b %#d')  # Windows
        print(f"Windows format (%a %b %#d): '{today_str}'")
    else:
        today_str = datetime.now(timezone.utc).strftime('%a %b %-d')  # Linux/Mac
        print(f"Linux/Mac format (%a %b %-d): '{today_str}'")
    
    # Test specific date (September 3, 2024) to match issue description
    test_date = datetime(2024, 9, 3, 12, 0, 0, tzinfo=timezone.utc)
    
    # Different formatting options
    formats_to_test = [
        ('%a %b %-d', 'Linux/Mac format (%-d)'),
        ('%a %b %#d', 'Windows format (%#d)'),
        ('%a %b %d', 'Standard format (%d) - with leading zero'),
    ]
    
    print(f"\nTesting with date: {test_date}")
    for fmt, description in formats_to_test:
        try:
            result = test_date.strftime(fmt)
            print(f"{description}: '{result}'")
        except ValueError as e:
            print(f"{description}: ERROR - {e}")
    
    return today_str


def test_date_format_consistency():
    """Test that date formats match expected calendar format."""
    print("\n=== Date Format Consistency Test ===")
    
    # Expected format for September 3rd according to issue
    expected_sep_3 = "Wed Sep 3"
    
    test_date = datetime(2024, 9, 3, 12, 0, 0, tzinfo=timezone.utc)
    
    # Test Linux format (what should be used in GitHub Actions)
    linux_format = test_date.strftime('%a %b %-d')
    print(f"Linux format result: '{linux_format}'")
    print(f"Expected format: '{expected_sep_3}'")
    print(f"Match: {linux_format == expected_sep_3}")
    
    # Test for potential issues with extra spacing
    formats_that_might_fail = [
        ('%a %b %d', 'With leading zero'),
        ('%a  %b %-d', 'Extra space between day and month'),
        ('%a %b  %-d', 'Extra space before day'),
    ]
    
    for fmt, description in formats_that_might_fail:
        try:
            result = test_date.strftime(fmt)
            print(f"{description}: '{result}' - Match: {result == expected_sep_3}")
        except ValueError as e:
            print(f"{description}: ERROR - {e}")


def test_edge_cases():
    """Test edge cases for date formatting."""
    print("\n=== Edge Cases Test ===")
    
    edge_dates = [
        (datetime(2024, 1, 1, tzinfo=timezone.utc), "New Year's Day"),
        (datetime(2024, 1, 9, tzinfo=timezone.utc), "Single digit day < 10"),
        (datetime(2024, 12, 31, tzinfo=timezone.utc), "New Year's Eve"),
        (datetime(2024, 2, 29, tzinfo=timezone.utc), "Leap year day"),
    ]
    
    for test_date, description in edge_dates:
        linux_format = test_date.strftime('%a %b %-d')
        print(f"{description} ({test_date.date()}): '{linux_format}'")


def simulate_calendar_data_filtering():
    """Simulate the filtering logic that would be used with actual calendar data."""
    print("\n=== Calendar Data Filtering Simulation ===")
    
    # Simulate calendar_df with various date formats
    calendar_data = [
        "Wed Sep 3",
        "Thu Sep 4", 
        "Fri Sep 5",
        "Mon Sep 9",
        "Wed Sep 03",  # With leading zero - this would be a problem
        "Wednesday Sep 3",  # Full day name - this would be a problem
    ]
    
    df = pd.DataFrame({'Date': calendar_data})
    print("Sample calendar data:")
    print(df)
    
    # Test filtering with current date logic
    test_date = datetime(2024, 9, 3, 12, 0, 0, tzinfo=timezone.utc)
    today_str = test_date.strftime('%a %b %-d')
    print(f"\nFiltering for: '{today_str}'")
    
    # Test exact match (what the current logic does)
    exact_matches = df[df['Date'] == today_str]
    print(f"Exact matches: {len(exact_matches)} rows")
    print(exact_matches)
    
    # Test partial match (more forgiving)
    partial_matches = df[df['Date'].str.contains(today_str)]
    print(f"\nPartial matches: {len(partial_matches)} rows")
    print(partial_matches)
    
    return df, today_str


if __name__ == "__main__":
    test_current_date_formatting()
    test_date_format_consistency()
    test_edge_cases()
    simulate_calendar_data_filtering()