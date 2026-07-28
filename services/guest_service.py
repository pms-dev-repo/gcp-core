from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

import streamlit as st

from core.config import BASE_DIR, load_client_config

DATE_FORMATS = ("%b %d, %Y", "%Y-%m-%d", "%d %B %Y")


def _guest_data_path(client_code: str) -> Path:
    config = load_client_config(client_code)
    client = config.get("client", {})
    data_folder = str(client.get("data_folder") or client_code)
    return BASE_DIR / "data" / data_folder / "guests.json"


@st.cache_data(show_spinner=False)
def load_guests(client_code: str) -> list[dict[str, Any]]:
    path = _guest_data_path(client_code)

    if not path.is_file():
        raise FileNotFoundError(
            f"Guest data file not found for '{client_code}': {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    guests = payload.get("guests", [])
    if not isinstance(guests, list):
        raise ValueError(f"Invalid guests.json format: {path}")
    return guests


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
    guest_id: str | None,
) -> dict[str, Any] | None:
    if guest_id is None:
        return None

    return next((guest for guest in guests if guest["id"] == guest_id), None)
