from __future__ import annotations

from typing import Any


def send_guest_email(guest: dict[str, Any]) -> bool:
    """Demo placeholder for Microsoft Graph or another email provider."""
    return bool(guest.get("email"))
