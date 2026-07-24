from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

import streamlit as st

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "guests.json"
DATE_FORMATS = ("%b %d, %Y", "%Y-%m-%d", "%d %B %Y")


@st.cache_data
def load_guests() -> list[dict[str, Any]]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)["guests"]


def _parse_guest_date(value: Any) -> date | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = str(value).strip()
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(text, date_format).date()
        except ValueError:
            continue
    return None


def filter_guests_by_stay_dates(
    guests: list[dict[str, Any]],
    arrival_from: date,
    arrival_to: date,
    departure_from: date,
    departure_to: date,
) -> list[dict[str, Any]]:
    """Filter arrivals by arrival date and departures by departure date."""
    filtered: list[dict[str, Any]] = []

    for guest in guests:
        movement = guest.get("movement")
        stay = guest.get("stay", {})

        if movement == "Arrivals":
            movement_date = _parse_guest_date(stay.get("arrival_date"))
            if movement_date and arrival_from <= movement_date <= arrival_to:
                filtered.append(guest)

        elif movement == "Departures":
            movement_date = _parse_guest_date(stay.get("departure_date"))
            if movement_date and departure_from <= movement_date <= departure_to:
                filtered.append(guest)

    return filtered


def get_guest_by_id(
    guests: list[dict[str, Any]],
    guest_id: str,
) -> dict[str, Any]:
    return next(guest for guest in guests if guest["id"] == guest_id)
