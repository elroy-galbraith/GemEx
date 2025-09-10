#!/usr/bin/env python3
"""
Unit tests for date filtering logic in GitHub Actions (Linux environment).
This ensures that the date string format matches the calendar_df format exactly.
"""

import unittest
from datetime import datetime, timezone
import pandas as pd
import platform


class TestDateFiltering(unittest.TestCase):
    """Test cases for date filtering logic."""
    
    def test_linux_date_format_matches_calendar_data(self):
        """Test that strftime('%a %b %-d') matches the format in calendar_df['Date'] column."""
        # Test case for September 3rd as mentioned in the issue
        test_date = datetime(2024, 9, 3, 12, 0, 0, tzinfo=timezone.utc)
        
        # Use Linux-friendly directive (what should be used in GitHub Actions)
        date_str = test_date.strftime('%a %b %-d')
        
        # This should produce "Tue Sep 3" for September 3, 2024
        # (Note: Sep 3, 2024 is actually Tuesday, not Wednesday as mentioned in example)
        expected_format = "Tue Sep 3"
        
        self.assertEqual(date_str, expected_format, 
                        f"Expected '{expected_format}', got '{date_str}'")
        
        # Ensure no leading zeros
        self.assertNotIn("03", date_str, "Date should not contain leading zeros")
        
        # Ensure no extra spacing
        self.assertEqual(len(date_str.split()), 3, "Date should have exactly 3 parts")
        
    def test_date_format_no_extra_spacing(self):
        """Test that date format fails if extra spacing is introduced."""
        test_date = datetime(2024, 9, 3, 12, 0, 0, tzinfo=timezone.utc)
        
        # Correct format
        correct_format = test_date.strftime('%a %b %-d')
        
        # Formats that should NOT match
        bad_formats = [
            test_date.strftime('%a  %b %-d'),  # Extra space between day and month
            test_date.strftime('%a %b  %-d'),  # Extra space before day
            test_date.strftime('%a %b %d'),    # With leading zero
        ]
        
        for bad_format in bad_formats:
            self.assertNotEqual(correct_format, bad_format, 
                              f"'{correct_format}' should not equal '{bad_format}'")
    
    def test_calendar_data_filtering_simulation(self):
        """Test filtering logic with simulated calendar data."""
        # Create sample calendar data similar to what Forex Factory might provide
        calendar_data = {
            'Date': [
                'Tue Sep 3',     # Should match
                'Wed Sep 4',     # Should not match  
                'Thu Sep 5',     # Should not match
                'Tue Sep 03',    # Should not match (leading zero)
                'Tuesday Sep 3', # Should not match (full day name)
            ],
            'Currency': ['USD', 'EUR', 'USD', 'USD', 'USD'],
            'Event': [
                'High Impact Expected',
                'Medium Impact',
                'Low Impact', 
                'High Impact Expected',
                'High Impact Expected'
            ]
        }
        
        calendar_df = pd.DataFrame(calendar_data)
        
        # Test date filtering for September 3, 2024
        test_date = datetime(2024, 9, 3, 12, 0, 0, tzinfo=timezone.utc)
        today_str = test_date.strftime('%a %b %-d')  # Should be "Tue Sep 3"
        
        # Filter for today's events
        todays_events = calendar_df[calendar_df['Date'] == today_str]
        
        # Should find exactly 1 matching row
        self.assertEqual(len(todays_events), 1, 
                        f"Expected 1 matching event, found {len(todays_events)}")
        
        # The matching row should be the first one
        matching_event = todays_events.iloc[0]
        self.assertEqual(matching_event['Date'], 'Tue Sep 3')
        self.assertEqual(matching_event['Event'], 'High Impact Expected')
        
    def test_high_impact_event_filtering(self):
        """Test filtering for high-impact events similar to row 59 example."""
        # Simulate the row 59 example: "Wed Sep 3 | USD | High Impact Expected"
        # Note: Using "Tue Sep 3" since Sep 3, 2024 is actually Tuesday
        calendar_data = {
            'Date': ['Tue Sep 3', 'Wed Sep 4', 'Thu Sep 5'],
            'Currency': ['USD', 'EUR', 'USD'], 
            'Impact': ['High Impact Expected', 'Medium Impact', 'Low Impact'],
            'Event': ['FOMC Meeting', 'ECB Rate Decision', 'GDP Data']
        }
        
        calendar_df = pd.DataFrame(calendar_data)
        
        # Test filtering for September 3rd
        test_date = datetime(2024, 9, 3, 12, 0, 0, tzinfo=timezone.utc)
        today_str = test_date.strftime('%a %b %-d')
        
        # Filter for today's high-impact USD events
        high_impact_events = calendar_df[
            (calendar_df['Date'] == today_str) & 
            (calendar_df['Currency'] == 'USD') &
            (calendar_df['Impact'].str.contains('High Impact', na=False))
        ]
        
        # Should find the high-impact event
        self.assertEqual(len(high_impact_events), 1)
        event = high_impact_events.iloc[0]
        self.assertEqual(event['Date'], 'Tue Sep 3')
        self.assertEqual(event['Currency'], 'USD')
        self.assertIn('High Impact', event['Impact'])
        
    def test_linux_environment_assumption(self):
        """Test that we're running in a Linux environment (as GitHub Actions does)."""
        # Since GitHub Actions uses Linux runners by default, verify we're testing in the right environment
        self.assertEqual(platform.system(), 'Linux', 
                        "Tests should run in Linux environment to match GitHub Actions")
        
    def test_edge_case_single_digit_days(self):
        """Test edge cases with single-digit days to ensure no leading zeros."""
        test_dates = [
            datetime(2024, 1, 1, tzinfo=timezone.utc),   # New Year
            datetime(2024, 1, 9, tzinfo=timezone.utc),   # Single digit < 10
            datetime(2024, 12, 5, tzinfo=timezone.utc),  # Different month
        ]
        
        for test_date in test_dates:
            date_str = test_date.strftime('%a %b %-d')
            
            # Should not contain leading zeros
            parts = date_str.split()
            day_part = parts[2]
            
            # Day should not start with 0 for single digits
            if len(day_part) == 1:
                self.assertNotEqual(day_part[0], '0', 
                                  f"Single digit day should not have leading zero: {date_str}")
            
            # Day should be 1-2 characters max
            self.assertLessEqual(len(day_part), 2, 
                               f"Day part should be 1-2 characters: {date_str}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)