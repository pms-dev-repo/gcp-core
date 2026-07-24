from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st


def initialize_state(guests: list[dict[str, Any]]) -> None:
    defaults = {
        "selected_guest_id": guests[0]["id"],
        "document_status": {},
        "generated_documents": {},
        "activity": {},
        "word_opened": {},
        "email_sent": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


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
