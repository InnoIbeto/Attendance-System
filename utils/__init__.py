"""
Utility functions for the attendance system
"""

import csv
from typing import List, Tuple


def export_to_csv(data: List[Tuple], headers: List[str], filename: str) -> bool:
    """
    Export data to a CSV file
    
    Args:
        data: List of tuples containing the data rows
        headers: List of header names
        filename: Path to the output CSV file
    
    Returns:
        True if export was successful, False otherwise
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)  # Write header row
            writer.writerows(data)    # Write data rows
        return True
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False


def validate_staff_id(staff_id: str) -> bool:
    """
    Validate staff ID format
    
    Args:
        staff_id: The staff ID to validate
    
    Returns:
        True if valid, False otherwise
    """
    # Basic validation: non-empty string with alphanumeric characters
    if not staff_id:
        return False
    
    # You can add more specific validation rules here based on your requirements
    # For example: length check, specific format, etc.
    return staff_id.isalnum() and len(staff_id) > 0


def format_timestamp_for_display(timestamp: str) -> str:
    """
    Format timestamp for display purposes
    
    Args:
        timestamp: The timestamp string to format
    
    Returns:
        Formatted timestamp string
    """
    # This function can be expanded based on your formatting preferences
    return timestamp