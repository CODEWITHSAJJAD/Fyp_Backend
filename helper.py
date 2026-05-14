from datetime import datetime, timedelta


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

def date_to_string(date_obj):
    """Convert datetime object to YYYY-MM-DD string"""
    if date_obj is None:
        return None
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime("%Y-%m-%d")

def add_days_to_string(date_str, days):
    """Add days to a date string (supports YYYY-MM-DD and Wed-D-M-YYYY formats)"""
    if date_str is None:
        return None
    date_obj = string_to_date(date_str)
    if date_obj is None:
        return None
    new_date = date_obj + timedelta(days=days)
    return date_to_string(new_date)

print(add_days_to_string("Wed-2-10-2024",10))
