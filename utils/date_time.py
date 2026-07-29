from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


def get_hotel_datetime(timezone_name: str) -> datetime:
    """
    Return the current date and time for the hotel's configured timezone.
    """
    try:
        return datetime.now(ZoneInfo(timezone_name))
    except Exception:
        # Safe fallback if the timezone is missing or invalid
        return datetime.now(ZoneInfo("UTC"))


def get_greeting(timezone_name: str) -> str:
    """
    Return a greeting based on the hotel's local time.
    """
    local_time = get_hotel_datetime(timezone_name)
    hour = local_time.hour

    if 5 <= hour < 12:
        return "Good morning"

    if 12 <= hour < 18:
        return "Good afternoon"

    return "Good evening"