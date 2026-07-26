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
        "selected_guest_id": None,
        "selected_guest_ids": set(),
        "bulk_selection_version": 0,
        "bulk_send_results": None,
        "bulk_document_results": None,
        "bulk_pdf_results": None,
        "generated_pdfs": {},
        "sidebar_open": True,
        "active_page": "communications",
        "document_status": {},
        "generated_documents": {},
        "activity": {},
        "word_opened": {},
        "email_sent": {},
        "filter_arrival_from": default_date,
        "filter_arrival_to": default_date,
        "filter_departure_from": default_date,
        "filter_departure_to": default_date,
        "filter_quick_option": "Tomorrow",
        "applied_arrival_from": default_date,
        "applied_arrival_to": default_date,
        "applied_departure_from": default_date,
        "applied_departure_to": default_date,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_selected_guest_ids() -> set[str]:
    selected = st.session_state.get("selected_guest_ids", set())

    if not isinstance(selected, set):
        selected = set(selected or [])
        st.session_state.selected_guest_ids = selected

    return selected


def get_bulk_selection_version() -> int:
    return int(st.session_state.get("bulk_selection_version", 0))


def _reset_bulk_results() -> None:
    st.session_state.bulk_send_results = None
    st.session_state.bulk_document_results = None
    st.session_state.bulk_pdf_results = None


def set_bulk_selection(guest_ids: set[str]) -> None:
    st.session_state.selected_guest_ids = set(guest_ids)
    st.session_state.bulk_selection_version = (
        get_bulk_selection_version() + 1
    )
    _reset_bulk_results()


def toggle_bulk_guest(guest_id: str, selected: bool) -> None:
    selected_ids = get_selected_guest_ids().copy()

    if selected:
        selected_ids.add(guest_id)
    else:
        selected_ids.discard(guest_id)

    set_bulk_selection(selected_ids)


def clear_bulk_selection() -> None:
    set_bulk_selection(set())


def ensure_selected_guest(guests: list[dict[str, Any]]) -> None:
    available_ids = {guest["id"] for guest in guests}

    selected_guest_id = st.session_state.get("selected_guest_id")
    if selected_guest_id not in available_ids:
        st.session_state.selected_guest_id = None

    selected_guest_ids = get_selected_guest_ids()
    valid_bulk_ids = selected_guest_ids & available_ids

    if valid_bulk_ids != selected_guest_ids:
        set_bulk_selection(valid_bulk_ids)

    if len(valid_bulk_ids) == 1:
        st.session_state.selected_guest_id = next(iter(valid_bulk_ids))
    elif len(valid_bulk_ids) > 1:
        st.session_state.selected_guest_id = None


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
