from __future__ import annotations

from typing import Any

import streamlit as st

from components.status import status_badge
from utils.state import get_status


def _render_movement(guests: list[dict[str, Any]], movement: str, search: str) -> None:
    filtered = [
        guest
        for guest in guests
        if guest["movement"] == movement
        and (
            not search
            or search.lower() in guest["full_name"].lower()
            or search.lower() in guest["room"].lower()
            or search.lower() in guest["confirmation_number"].lower()
        )
    ]

    if not filtered:
        st.info("No guests match the current filter.")
        return

    for guest in filtered:
        selected = guest["id"] == st.session_state.selected_guest_id
        css = "guest-card guest-card-selected" if selected else "guest-card"
        st.markdown(
            f"""
            <div class="{css}">
              <div class="guest-name">👤 {guest['full_name']}</div>
              <div class="guest-meta">Room {guest['room']} · ETA {guest['transport']['eta']}</div>
              {status_badge(get_status(guest))}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "Selected" if selected else "Select",
            key=f"select_{movement}_{guest['id']}",
            type="primary" if selected else "secondary",
            disabled=selected,
        ):
            st.session_state.selected_guest_id = guest["id"]
            st.rerun()


def render_guest_list(guests: list[dict[str, Any]]) -> None:
    st.markdown('<div class="panel-title">Guest List</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="muted">Choose an arrival or departure.</div>',
        unsafe_allow_html=True,
    )
    arrivals_tab, departures_tab = st.tabs(["✈ Arrivals", "🧳 Departures"])
    search = st.text_input(
        "Search guests",
        placeholder="Search guest, room or confirmation…",
        label_visibility="collapsed",
    )

    with arrivals_tab:
        _render_movement(guests, "Arrivals", search)
    with departures_tab:
        _render_movement(guests, "Departures", search)
