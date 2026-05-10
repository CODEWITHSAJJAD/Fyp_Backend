from datetime import datetime, timedelta

def date_to_string(date_obj):
    """Convert datetime object to YYYY-MM-DD string"""
    if date_obj is None:
        return None
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime("%Y-%m-%d")

def string_to_date(date_str):
    """Convert YYYY-MM-DD string to datetime object"""
    if date_str is None:
        return None
    if isinstance(date_str, datetime):
        return date_str
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        return None

def datetime_to_string(date_obj):
    """Convert datetime object to ISO string YYYY-MM-DDTHH:MM:SS"""
    if date_obj is None:
        return None
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime("%Y-%m-%dT%H:%M:%S")

def string_to_datetime(date_str):
    """Convert ISO string to datetime object"""
    if date_str is None:
        return None
    if isinstance(date_str, datetime):
        return date_str
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    except:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            return None

def add_days_to_string(date_str, days):
    """Add days to a date string (YYYY-MM-DD)"""
    if date_str is None:
        return None
    date_obj = string_to_date(date_str)
    if date_obj is None:
        return None
    new_date = date_obj + timedelta(days=days)
    return date_to_string(new_date)

def get_current_date_string():
    """Get current date as YYYY-MM-DD string"""
    return datetime.now().strftime("%Y-%m-%d")

def get_current_datetime_string():
    """Get current datetime as ISO string"""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def compare_dates(date_str1, date_str2):
    """Compare two date strings. Returns -1, 0, or 1"""
    d1 = string_to_date(date_str1)
    d2 = string_to_date(date_str2)
    if d1 is None or d2 is None:
        return 0
    if d1 < d2:
        return -1
    elif d1 > d2:
        return 1
    return 0

def days_between(date_str1, date_str2):
    """Get days between two date strings"""
    d1 = string_to_date(date_str1)
    d2 = string_to_date(date_str2)
    if d1 is None or d2 is None:
        return None
    return (d2 - d1).days

def days_until(date_str):
    """Get days until a date from today (can be negative if past)"""
    today = get_current_date_string()
    return days_between(today, date_str)

def days_since(date_str):
    """Get days since a date from today (can be negative if future)"""
    today = get_current_date_string()
    return days_between(date_str, today)


def get_month_number(date_str):
    """
    Get month number from a date string (YYYY-MM-DD format)

    Args:
        date_str: Date string in YYYY-MM-DD format or datetime object

    Returns:
        int: Month number (1-12) or None if invalid

    Examples:
        >>> get_month_number("2024-12-25")
        12
        >>> get_month_number("2024-01-01")
        1
    """
    if date_str is None:
        return None

    date_obj = string_to_date(date_str)
    if date_obj is None:
        return None
    return date_obj.month