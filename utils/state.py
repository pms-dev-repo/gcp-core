from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import streamlit as st

BARBADOS_TIMEZONE = ZoneInfo("America/Barbados")


def _tomorrow_in_barbados():
    return datetime.now(BARBADOS_TIMEZONE).date() + timedelta(days=1)


def initialize_state(guests: list[dict[str, Any]]) -> None:
    default_date = _tomorrow_in_barbados()
    defaults = {
        "selected_guest_id": guests[0]["id"] if guests else None,
        "document_status": {},
        "generated_documents": {},
        "activity": {},
        "word_opened": {},
        "email_sent": {},
        # Draft values shown in the date controls.
        "filter_arrival_from": default_date,
        "filter_arrival_to": default_date,
        "filter_departure_from": default_date,
        "filter_departure_to": default_date,
        "filter_quick_option": "Tomorrow",
        # Applied values used to filter the guest list.
        "applied_arrival_from": default_date,
        "applied_arrival_to": default_date,
        "applied_departure_from": default_date,
        "applied_departure_to": default_date,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def ensure_selected_guest(guests: list[dict[str, Any]]) -> None:
    """Keep the selected guest valid after a date filter is applied."""
    available_ids = {guest["id"] for guest in guests}
    if st.session_state.get("selected_guest_id") not in available_ids:
        st.session_state.selected_guest_id = guests[0]["id"] if guests else None


def add_activity(guest_id: str, message: str) -> None:
    st.session_state.activity.setdefault(guest_id, []).insert(
        0,
        {"time": datetime.now().strftime("%I:%M %p"), "message": message},
    )


def get_status(guest: dict[str, Any]) -> str:
    guest_id = guest["id"]
    if not guest.get("email"):
        return "Missing email"
    if st.session_state.email_sent.get(guest_id):
        return "Sent"
    if st.session_state.word_opened.get(guest_id):
        return "Reviewed"
    if st.session_state.generated_documents.get(guest_id):
        return "Generated"
    return "Ready"
