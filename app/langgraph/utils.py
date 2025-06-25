from datetime import datetime, timedelta
import pytz
import dateparser

def parse_natural_datetime(text: str, default_timezone: str = "Asia/Dhaka") -> datetime:
    """
    Parses a natural language datetime string into a timezone-aware datetime object.
    Uses dateparser for flexible parsing of human phrases.
    Raises ValueError if parsing fails.
    """
    settings = {
        'TIMEZONE': default_timezone,
        'RETURN_AS_TIMEZONE_AWARE': True,
        'PREFER_DATES_FROM': 'future',
        'RELATIVE_BASE': datetime.now(pytz.timezone(default_timezone))
    }
    dt = dateparser.parse(text, settings=settings)
    if dt is None:
        raise ValueError(f"Could not parse datetime from input: {text}")
    return dt

def ensure_future_datetime(dt: datetime) -> datetime:
    """
    If datetime is in the past, push it forward by 1 year (or fallback).
    """
    now = datetime.now(tz=dt.tzinfo)
    if dt < now:
        try:
            dt = dt.replace(year=dt.year + 1)
        except ValueError:
            dt = dt + timedelta(days=365)
    return dt

def format_event_datetime(dt: datetime) -> str:
    """
    Formats datetime to ISO8601 string with timezone for Google Calendar API.
    """
    return dt.isoformat()

def validate_iso_datetime(dt_str: str) -> bool:
    """
    Check if a string is valid ISO 8601 datetime.
    """
    try:
        datetime.fromisoformat(dt_str)
        return True
    except ValueError:
        return False

def default_event_description(summary: str) -> str:
    """
    Generate a default description if none provided, based on the summary/title.
    """
    return f"Auto-generated event description for '{summary}'."

def default_event_color(importance: str = "normal") -> str:
    """
    Return event color ID based on importance.
    Google Calendar color IDs: 11=high, 7=medium, 5=normal/low
    """
    importance_map = {
        "high": "11",
        "medium": "7",
        "normal": "5"
    }
    return importance_map.get(importance.lower(), "5")

def default_event_status() -> str:
    """
    Return default event status.
    """
    return "busy"
