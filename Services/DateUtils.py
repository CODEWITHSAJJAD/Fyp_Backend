# from datetime import datetime, timedelta
#
# def date_to_string(date_obj):
#     """Convert datetime object to YYYY-MM-DD string"""
#     if date_obj is None:
#         return None
#     if isinstance(date_obj, str):
#         return date_obj
#     return date_obj.strftime("%Y-%m-%d")
#
# def string_to_date(date_str):
#     """Convert YYYY-MM-DD string to datetime object"""
#     if date_str is None:
#         return None
#     if isinstance(date_str, datetime):
#         return date_str
#     try:
#         return datetime.strptime(date_str, "%Y-%m-%d")
#     except:
#         return None
#
# def datetime_to_string(date_obj):
#     """Convert datetime object to ISO string YYYY-MM-DDTHH:MM:SS"""
#     if date_obj is None:
#         return None
#     if isinstance(date_obj, str):
#         return date_obj
#     return date_obj.strftime("%Y-%m-%dT%H:%M:%S")
#
# def string_to_datetime(date_str):
#     """Convert ISO string to datetime object"""
#     if date_str is None:
#         return None
#     if isinstance(date_str, datetime):
#         return date_str
#     try:
#         return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
#     except:
#         try:
#             return datetime.strptime(date_str, "%Y-%m-%d")
#         except:
#             return None
#
# def add_days_to_string(date_str, days):
#     """Add days to a date string (YYYY-MM-DD)"""
#     if date_str is None:
#         return None
#     date_obj = string_to_date(date_str)
#     if date_obj is None:
#         return None
#     new_date = date_obj + timedelta(days=days)
#     return date_to_string(new_date)
#
# def get_current_date_string():
#     """Get current date as YYYY-MM-DD string"""
#     return datetime.now().strftime("%Y-%m-%d")
#
# def get_current_datetime_string():
#     """Get current datetime as ISO string"""
#     return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
#
# def compare_dates(date_str1, date_str2):
#     """Compare two date strings. Returns -1, 0, or 1"""
#     d1 = string_to_date(date_str1)
#     d2 = string_to_date(date_str2)
#     if d1 is None or d2 is None:
#         return 0
#     if d1 < d2:
#         return -1
#     elif d1 > d2:
#         return 1
#     return 0
#
# def days_between(date_str1, date_str2):
#     """Get days between two date strings"""
#     d1 = string_to_date(date_str1)
#     d2 = string_to_date(date_str2)
#     if d1 is None or d2 is None:
#         return None
#     return (d2 - d1).days
#
# def days_until(date_str):
#     """Get days until a date from today (can be negative if past)"""
#     today = get_current_date_string()
#     return days_between(today, date_str)
#
# def days_since(date_str):
#     """Get days since a date from today (can be negative if future)"""
#     today = get_current_date_string()
#     return days_between(date_str, today)
#
#
# def get_month_number(date_str):
#     """
#     Get month number from a date string
#
#     Args:
#         date_str: Date string in YYYY-MM-DD format or "Wed-D-M-YYYY" format or datetime object
#
#     Returns:
#         int: Month number (1-12) or None if invalid
#
#     Examples:
#         >>> get_month_number("2024-12-25")
#         12
#         >>> get_month_number("2024-01-01")
#         1
#         >>> get_month_number("Wed-6-2-2026")
#         2
#     """
#     if date_str is None:
#         return None
#
#     if isinstance(date_str, datetime):
#         return date_str.month
#
#     if isinstance(date_str, str):
#         parts = date_str.strip().split('-')
#
#         if len(parts) == 4:
#             try:
#                 return int(parts[2])
#             except (ValueError, IndexError):
#                 pass
#
#         date_obj = string_to_date(date_str)
#         if date_obj is not None:
#             return date_obj.month
#
#     return None


from datetime import datetime, timedelta
import calendar


def date_to_string(date_obj):
    """Convert datetime object to YYYY-MM-DD string"""
    if date_obj is None:
        return None
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime("%Y-%m-%d")


def string_to_date(date_str):
    """
    Convert date string to datetime object.
    Supports YYYY-MM-DD and Wed-D-M-YYYY formats
    """
    if date_str is None:
        return None
    if isinstance(date_str, datetime):
        return date_str
    if isinstance(date_str, str):
        # Try YYYY-MM-DD format first
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            pass

        # Try Wed-D-M-YYYY format (e.g., "Wed-6-2-2026")
        try:
            parts = date_str.strip().split('-')
            if len(parts) == 4:
                # parts[0] is day name (ignored), parts[1] is day, parts[2] is month, parts[3] is year
                day = int(parts[1])
                month = int(parts[2])
                year = int(parts[3])
                return datetime(year, month, day)
        except (ValueError, IndexError):
            pass

    return None

def get_year_number(date_str):
    """
    Get year number from a date string

    Args:
        date_str: Date string in YYYY-MM-DD format or "Wed-D-M-YYYY" format or datetime object

    Returns:
        int: year number  or None if invalid

    Examples:
        >>> get_year_number("2024-12-25")
        2024
        >>> get_year_number("2024-01-01")
        2024
        >>> get_year_number("Wed-6-2-2026")
        2026
    """
    if date_str is None:
        return None

    if isinstance(date_str, datetime):
        return date_str.year

    if isinstance(date_str, str):
        parts = date_str.strip().split('-')
        print("parts",parts[3])

        if len(parts) == 4:
            try:
                return int(parts[3])
            except (ValueError, IndexError):
                pass

        date_obj = string_to_date(date_str)
        if date_obj is not None:
            return date_obj.year

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
    """Add days to a date string (supports YYYY-MM-DD and Wed-D-M-YYYY formats)"""
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
    Get month number from a date string

    Args:
        date_str: Date string in YYYY-MM-DD format or "Wed-D-M-YYYY" format or datetime object

    Returns:
        int: Month number (1-12) or None if invalid

    Examples:
        >>> get_month_number("2024-12-25")
        12
        >>> get_month_number("2024-01-01")
        1
        >>> get_month_number("Wed-6-2-2026")
        2
    """
    if date_str is None:
        return None

    if isinstance(date_str, datetime):
        return date_str.month

    if isinstance(date_str, str):
        parts = date_str.strip().split('-')

        if len(parts) == 4:
            try:
                return int(parts[2])
            except (ValueError, IndexError):
                pass

        date_obj = string_to_date(date_str)
        if date_obj is not None:
            return date_obj.month

    return None


def date_to_custom_string(date_obj):
    """
    Convert datetime object to custom format "Wed-D-M-YYYY"
    """
    if date_obj is None:
        return None
    if isinstance(date_obj, str):
        return date_obj

    day_name = calendar.day_name[date_obj.weekday()][:3]
    return f"{day_name}-{date_obj.day}-{date_obj.month}-{date_obj.year}"


def get_current_date_custom():
    """Get current date in custom format (Wed-D-M-YYYY)"""
    return date_to_custom_string(datetime.now())


def compare_custom_dates(date_str1, date_str2):
    """
    Compare two dates in custom format. Returns -1, 0, or 1
    Handles both YYYY-MM-DD and Wed-D-M-YYYY formats
    """
    d1 = string_to_date(date_str1)
    d2 = string_to_date(date_str2)
    if d1 is None or d2 is None:
        return 0
    if d1 < d2:
        return -1
    elif d1 > d2:
        return 1
    return 0


def is_today_or_tomorrow(date_str):
    """
    Check if date is today or tomorrow based on farmer's preferred date
    Uses the farmer's Prefered_Date as reference point, not system date
    """
    from Model.FarmerModel import FarmerModel

    # Get today's date from system (but we use it for comparison only)
    reference_date = datetime.now().date()
    check_date = string_to_date(date_str)
    if check_date is None:
        return False

    check_date_only = check_date.date()

    today = reference_date
    tomorrow = reference_date + timedelta(days=1)

    return check_date_only == today or check_date_only == tomorrow


def is_past_date(date_str, reference_date_str=None):
    """
    Check if date is in the past compared to reference date
    If no reference provided, uses current system date
    """
    check_date = string_to_date(date_str)
    if check_date is None:
        return False

    if reference_date_str:
        ref_date = string_to_date(reference_date_str)
    else:
        ref_date = datetime.now()

    if ref_date is None:
        ref_date = datetime.now()

    return check_date.date() < ref_date.date()


def get_date_gap_details(date_str1, date_str2):
    """
    Get comprehensive gap details between two dates

    Args:
        date_str1: First date (YYYY-MM-DD or Wed-D-M-YYYY format)
        date_str2: Second date (YYYY-MM-DD or Wed-D-M-YYYY format)

    Returns:
        dict: Dictionary containing various gap measurements
    """
    d1 = string_to_date(date_str1)
    d2 = string_to_date(date_str2)

    if d1 is None or d2 is None:
        return None

    # Ensure d1 is earlier than d2 for consistent calculations
    if d1 > d2:
        d1, d2 = d2, d1
        swapped = True
    else:
        swapped = False

    diff = d2 - d1

    # Calculate various metrics
    years = d2.year - d1.year
    months = (d2.year - d1.year) * 12 + (d2.month - d1.month)
    weeks = diff.days // 7
    days = diff.days
    hours = diff.days * 24
    minutes = hours * 60

    # Adjust years and months for exact differences
    if d2.month < d1.month or (d2.month == d1.month and d2.day < d1.day):
        years -= 1

    # Calculate exact month difference considering days
    month_diff = months
    if d2.day < d1.day:
        month_diff -= 1

    result = {
        'years': years,
        'months': month_diff,
        'weeks': weeks,
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'total_days': days,
        'is_past': swapped,  # True if date_str1 is after date_str2
        'direction': 'past' if swapped else 'future'
    }

    return result


def add_days_to_string_preserve_format(date_str, days):
    """
    Add days to a date string while preserving the original format.
    Supports both YYYY-MM-DD and Wed-D-M-YYYY formats.

    Args:
        date_str: Date string in either format
        days: Number of days to add (can be negative)

    Returns:
        Date string in the same format as input, or None if invalid
    """
    if date_str is None:
        return None

    # Parse the date to datetime object
    date_obj = string_to_date(date_str)
    if date_obj is None:
        return None

    # Calculate new date
    new_date = date_obj + timedelta(days=days)

    # Check original format and return in same format
    if isinstance(date_str, str):
        parts = date_str.strip().split('-')

        # If it's in custom format (Wed-D-M-YYYY)
        if len(parts) == 4 and len(parts[0]) == 3 and parts[0][0].isalpha():
            # Return in custom format
            day_name = calendar.day_name[new_date.weekday()][:3]
            return f"{day_name}-{new_date.day}-{new_date.month}-{new_date.year}"

    # Default to standard YYYY-MM-DD format
    return date_to_string(new_date)


def add_days_to_string(date_str, days):
    """
    Original function - adds days to a date string and returns in YYYY-MM-DD format.
    Kept for backward compatibility.
    """
    if date_str is None:
        return None
    date_obj = string_to_date(date_str)
    if date_obj is None:
        return None
    new_date = date_obj + timedelta(days=days)
    return date_to_string(new_date)


def add_days_to_custom_string(date_str, days):
    """
    Specifically for custom format: adds days and returns in same custom format.
    Useful when you know the input is in Wed-D-M-YYYY format.
    """
    if date_str is None:
        return None
    date_obj = string_to_date(date_str)
    if date_obj is None:
        return None
    new_date = date_obj + timedelta(days=days)

    # Format as custom string
    day_name = calendar.day_name[new_date.weekday()][:3]
    return f"{day_name}-{new_date.day}-{new_date.month}-{new_date.year}"
def get_human_readable_period(date_str, reference_date=None):
    """
    Get human readable time difference (e.g., "2 days ago", "3 weeks ago", "1 month from now")

    Args:
        date_str: Date to compare (YYYY-MM-DD or Wed-D-M-YYYY format)
        reference_date: Reference date (defaults to today)

    Returns:
        str: Human readable period description
    """
    if reference_date is None:
        reference_date = get_current_date_string()

    d1 = string_to_date(date_str)
    d2 = string_to_date(reference_date)

    if d1 is None or d2 is None:
        return "Invalid date"

    diff = d2 - d1
    days_diff = diff.days

    # Future or past?
    if days_diff == 0:
        return "today"
    elif days_diff == 1:
        return "tomorrow"
    elif days_diff == -1:
        return "yesterday"
    elif days_diff > 0:
        # Future dates
        if days_diff < 7:
            return f"{days_diff} day{'s' if days_diff > 1 else ''} from now"
        elif days_diff < 30:
            weeks = days_diff // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} from now"
        elif days_diff < 365:
            months = days_diff // 30
            return f"{months} month{'s' if months > 1 else ''} from now"
        else:
            years = days_diff // 365
            return f"{years} year{'s' if years > 1 else ''} from now"
    else:
        # Past dates
        days_abs = abs(days_diff)
        if days_abs < 7:
            return f"{days_abs} day{'s' if days_abs > 1 else ''} ago"
        elif days_abs < 30:
            weeks = days_abs // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        elif days_abs < 365:
            months = days_abs // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        else:
            years = days_abs // 365
            return f"{years} year{'s' if years > 1 else ''} ago"


def get_relative_date_description(date_str):
    """
    Get relative description like 'today', 'yesterday', '2 weeks ago', etc.
    More detailed version with exact matching for recent dates

    Args:
        date_str: Date to describe (YYYY-MM-DD or Wed-D-M-YYYY format)

    Returns:
        str: Description like 'Today', 'Yesterday', 'Last week', etc.
    """
    today = get_current_date_string()
    days = days_between(date_str, today)

    if days is None:
        return "Invalid date"

    if days == 0:
        return "Today"
    elif days == 1:
        return "Tomorrow"
    elif days == -1:
        return "Yesterday"
    elif days == 2:
        return "Day before yesterday"
    elif days == -2:
        return "Day after tomorrow"
    elif 3 <= days <= 6:
        return f"{days} days ago"
    elif -6 <= days <= -3:
        return f"{abs(days)} days from now"
    elif 7 <= days <= 13:
        return "Last week"
    elif -13 <= days <= -7:
        return "Next week"
    elif 14 <= days <= 20:
        return "2 weeks ago"
    elif -20 <= days <= -14:
        return "2 weeks from now"
    elif 21 <= days <= 27:
        return "3 weeks ago"
    elif -27 <= days <= -21:
        return "3 weeks from now"
    elif 28 <= days <= 45:
        return "Last month"
    elif -45 <= days <= -28:
        return "Next month"
    elif days > 365:
        years = days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif days < -365:
        years = abs(days) // 365
        return f"{years} year{'s' if years > 1 else ''} from now"
    elif days > 45:
        months = days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif days < -45:
        months = abs(days) // 30
        return f"{months} month{'s' if months > 1 else ''} from now"

    return get_human_readable_period(date_str)


def get_date_range(start_date, end_date):
    """
    Get all dates between start and end dates (inclusive)

    Args:
        start_date: Start date (YYYY-MM-DD or Wed-D-M-YYYY format)
        end_date: End date (YYYY-MM-DD or Wed-D-M-YYYY format)

    Returns:
        list: List of date strings in YYYY-MM-DD format between start and end
    """
    start = string_to_date(start_date)
    end = string_to_date(end_date)

    if start is None or end is None:
        return []

    if start > end:
        start, end = end, start

    date_list = []
    current = start
    while current <= end:
        date_list.append(date_to_string(current))
        current += timedelta(days=1)

    return date_list


def get_week_number(date_str):
    """
    Get week number of the year for a given date

    Args:
        date_str: Date string (YYYY-MM-DD or Wed-D-M-YYYY format)

    Returns:
        int: Week number (1-53)
    """
    date_obj = string_to_date(date_str)
    if date_obj is None:
        return None
    return date_obj.isocalendar()[1]


def get_quarter(date_str):
    """
    Get quarter of the year for a given date

    Args:
        date_str: Date string (YYYY-MM-DD or Wed-D-M-YYYY format)

    Returns:
        int: Quarter number (1-4)
    """
    month = get_month_number(date_str)
    if month is None:
        return None
    return (month - 1) // 3 + 1


def is_weekend(date_str):
    """
    Check if a date is weekend (Saturday or Sunday)

    Args:
        date_str: Date string (YYYY-MM-DD or Wed-D-M-YYYY format)

    Returns:
        bool: True if weekend, False otherwise
    """
    date_obj = string_to_date(date_str)
    if date_obj is None:
        return None
    return date_obj.weekday() >= 5  # 5=Saturday, 6=Sunday


def is_weekday(date_str):
    """
    Check if a date is weekday (Monday to Friday)

    Args:
        date_str: Date string (YYYY-MM-DD or Wed-D-M-YYYY format)

    Returns:
        bool: True if weekday, False otherwise
    """
    weekend = is_weekend(date_str)
    if weekend is None:
        return None
    return not weekend


def get_day_name(date_str):
    """
    Get day name for a given date

    Args:
        date_str: Date string (YYYY-MM-DD or Wed-D-M-YYYY format)

    Returns:
        str: Day name (Monday, Tuesday, etc.)
    """
    date_obj = string_to_date(date_str)
    if date_obj is None:
        return None
    return date_obj.strftime("%A")


def get_month_name(date_str):
    """
    Get month name for a given date

    Args:
        date_str: Date string (YYYY-MM-DD or Wed-D-M-YYYY format)

    Returns:
        str: Month name (January, February, etc.)
    """
    month_num = get_month_number(date_str)
    if month_num is None:
        return None
    return calendar.month_name[month_num]


def format_to_standard(date_str):
    """
    Convert any supported date format to YYYY-MM-DD standard format

    Args:
        date_str: Date in YYYY-MM-DD or Wed-D-M-YYYY format

    Returns:
        str: Date in YYYY-MM-DD format or None if invalid
    """
    date_obj = string_to_date(date_str)
    if date_obj is None:
        return None
    return date_to_string(date_obj)


def format_to_custom(date_str):
    """
    Convert any supported date format to Wed-D-M-YYYY custom format

    Args:
        date_str: Date in YYYY-MM-DD or Wed-D-M-YYYY format

    Returns:
        str: Date in Wed-D-M-YYYY format (e.g., "Wed-6-2-2026") or None if invalid
    """
    date_obj = string_to_date(date_str)
    if date_obj is None:
        return None
    day_name = date_obj.strftime("%a")  # Three letter weekday
    return f"{day_name}-{date_obj.day}-{date_obj.month}-{date_obj.year}"


# Example usage and test function
def demo_date_features():
    """Demonstrate all the new date features with both formats"""

    today = get_current_date_string()
    yesterday = add_days_to_string(today, -1)
    tomorrow = add_days_to_string(today, 1)
    last_week = add_days_to_string(today, -7)
    next_week = add_days_to_string(today, 7)
    last_month = add_days_to_string(today, -30)
    next_month = add_days_to_string(today, 30)
    last_year = add_days_to_string(today, -365)
    next_year = add_days_to_string(today, 365)

    # Test custom format
    custom_date = "Wed-6-2-2026"

    print("=== Date Format Conversion ===")
    print(f"Custom format '{custom_date}' to standard: {format_to_standard(custom_date)}")
    print(f"Standard '{today}' to custom: {format_to_custom(today)}")

    print("\n=== Date Gap Analysis ===")
    gap = get_date_gap_details(last_year, next_year)
    if gap:
        print(f"Between {last_year} and {next_year}:")
        print(f"  Years: {gap['years']}")
        print(f"  Months: {gap['months']}")
        print(f"  Weeks: {gap['weeks']}")
        print(f"  Days: {gap['days']}")
        print(f"  Direction: {gap['direction']}")

    print("\n=== Human Readable Periods ===")
    print(f"Today ({today}): {get_human_readable_period(today)}")
    print(f"Yesterday ({yesterday}): {get_human_readable_period(yesterday)}")
    print(f"Tomorrow ({tomorrow}): {get_human_readable_period(tomorrow)}")
    print(f"Last week ({last_week}): {get_human_readable_period(last_week)}")
    print(f"Next week ({next_week}): {get_human_readable_period(next_week)}")
    print(f"Last month ({last_month}): {get_human_readable_period(last_month)}")
    print(f"Next month ({next_month}): {get_human_readable_period(next_month)}")
    print(f"Last year ({last_year}): {get_human_readable_period(last_year)}")
    print(f"Next year ({next_year}): {get_human_readable_period(next_year)}")

    print("\n=== Custom Format Support ===")
    print(f"Custom date '{custom_date}':")
    print(f"  Month number: {get_month_number(custom_date)}")
    print(f"  Month name: {get_month_name(custom_date)}")
    print(f"  Day name: {get_day_name(custom_date)}")
    print(f"  Is weekend: {is_weekend(custom_date)}")
    print(f"  Days until: {days_until(custom_date)}")

    print("\n=== Relative Descriptions ===")
    print(f"{today}: {get_relative_date_description(today)}")
    print(f"{yesterday}: {get_relative_date_description(yesterday)}")
    print(f"{last_week}: {get_relative_date_description(last_week)}")
    print(f"{last_month}: {get_relative_date_description(last_month)}")

    print("\n=== Date Information ===")
    sample_date = "2024-12-25"
    print(f"Date: {sample_date}")
    print(f"  Day name: {get_day_name(sample_date)}")
    print(f"  Month name: {get_month_name(sample_date)}")
    print(f"  Week number: {get_week_number(sample_date)}")
    print(f"  Quarter: {get_quarter(sample_date)}")
    print(f"  Is weekend: {is_weekend(sample_date)}")
    print(f"  Is weekday: {is_weekday(sample_date)}")

    print("\n=== Date Range Example ===")
    date_range = get_date_range("2024-12-01", "2024-12-05")
    print(f"Dates from 2024-12-01 to 2024-12-05: {date_range}")


# Run demo if script is executed directly
if __name__ == "__main__":
    demo_date_features()