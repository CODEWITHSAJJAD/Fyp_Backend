from datetime import datetime

# text="d2hlbiBzaG91bGQgaSBjdWx0aXZhdGUgYmFqcmEgYW5kIHdoYXQgYXJlIGl0cyByZXF1aXJlbWVudHMg"
# from Services.TranslationService import TranslationService
# print(TranslationService.decode_unicode(text))


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

year=get_year_number("Fri-24-4-2026")
print(year)