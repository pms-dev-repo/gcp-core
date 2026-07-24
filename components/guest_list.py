from __future__ import annotations

from typing import Any

import streamlit as st

from components.status import status_badge
from utils.state import get_status


def _matches_search(guest: dict[str, Any], search: str) -> bool:
    """Return True when the guest matches the committed search term."""
    if not search:
        return True

    term = search.casefold().strip()

    searchable_values = (
        guest.get("confirmation_number", ""),
        guest.get("full_name", ""),
        guest.get("company", ""),
        guest.get("email", ""),
        guest.get("room", ""),
    )

    return any(term in str(value).casefold() for value in searchable_values)


def _render_movement(
    guests: list[dict[str, Any]],
    movement: str,
    search: str,
) -> None:
    filtered = [
        guest
        for guest in guests
        if guest.get("movement") == movement
        and _matches_search(guest, search)
    ]

    if not filtered:
        st.info("No guests match the current search.")
        return

    for guest in filtered:
        guest_id = guest["id"]
        selected = guest_id == st.session_state.selected_guest_id
        css_class = (
            "guest-card guest-card-selected"
            if selected
            else "guest-card"
        )

        full_name = guest.get("full_name", "Unknown guest")
        room = guest.get("room") or "—"
        confirmation = guest.get("confirmation_number") or "—"
        eta = guest.get("transport", {}).get("eta") or "—"

        st.markdown(
            f"""
            <div class="{css_class}">
                <div class="guest-name">{full_name}</div>
                <div class="guest-meta">
                    Room {room} · Confirmation {confirmation}
                </div>
                <div class="guest-meta">ETA {eta}</div>
                {status_badge(get_status(guest))}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Selected" if selected else "Select",
            key=f"select_{movement}_{guest_id}",
            type="primary" if selected else "secondary",
            disabled=selected,
            use_container_width=True,
        ):
            st.session_state.selected_guest_id = guest_id
            st.rerun()


def _render_guest_search() -> str:
    """
    Render an OPERA-style guest search.

    The filter is applied only when the user presses Enter or clicks Search.
    """
    if "guest_search_value" not in st.session_state:
        st.session_state.guest_search_value = ""

    with st.form("guest_search_form", border=False):
        search_col, button_col = st.columns([5, 1], gap="small")

        with search_col:
            search_input = st.text_input(
                "Guest search",
                value=st.session_state.guest_search_value,
                placeholder=(
                    "Confirmation Number, Guest Name, Company, Email"
                ),
                label_visibility="collapsed",
                key="guest_search_input",
            )

        with button_col:
            submitted = st.form_submit_button(
                "Search",
                type="primary",
                use_container_width=True,
            )

    if submitted:
        st.session_state.guest_search_value = search_input.strip()

    return st.session_state.guest_search_value


def render_guest_list(guests: list[dict[str, Any]]) -> None:
    st.markdown(
        '<div class="panel-title">Guest List</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="muted">Choose an arrival or departure.</div>',
        unsafe_allow_html=True,
    )

    search = _render_guest_search()

    arrivals_count = sum(
        1
        for guest in guests
        if guest.get("movement") == "Arrivals"
        and _matches_search(guest, search)
    )
    departures_count = sum(
        1
        for guest in guests
        if guest.get("movement") == "Departures"
        and _matches_search(guest, search)
    )

    arrivals_tab, departures_tab = st.tabs(
        [
            f"Arrivals ({arrivals_count})",
            f"Departures ({departures_count})",
        ]
    )

    with arrivals_tab:
        _render_movement(guests, "Arrivals", search)

    with departures_tab:
        _render_movement(guests, "Departures", search)
