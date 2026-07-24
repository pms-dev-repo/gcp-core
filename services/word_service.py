from __future__ import annotations

from typing import Any


def open_in_word_365(guest: dict[str, Any]) -> str:
    """Demo placeholder.

    Production flow:
    1. Upload DOCX to OneDrive or SharePoint with Microsoft Graph.
    2. Return the item's webUrl.
    """
    return f"demo://word365/{guest['confirmation_number']}"
