from __future__ import annotations

from typing import Any

import streamlit as st

from components.status import status_badge
from utils.state import (
    clear_bulk_selection,
    get_bulk_selection_version,
    get_selected_guest_ids,
    get_status,
    set_bulk_selection,
    toggle_bulk_guest,
)


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


def _sync_single_selection() -> None:
    """
    Keep the original single-guest workflow compatible with bulk selection.

    When exactly one reservation remains selected, it becomes the active guest.
    When two or more are selected, the workspace switches to bulk mode.
    """
    selected_ids = list(get_selected_guest_ids())

    if len(selected_ids) == 1:
        st.session_state.selected_guest_id = selected_ids[0]
    elif len(selected_ids) == 0:
        st.session_state.selected_guest_id = None


def _select_all_visible(filtered: list[dict[str, Any]]) -> None:
    visible_ids = {guest["id"] for guest in filtered}
    selected_ids = get_selected_guest_ids()
    set_bulk_selection(selected_ids | visible_ids)
    _sync_single_selection()


def _clear_visible(filtered: list[dict[str, Any]]) -> None:
    visible_ids = {guest["id"] for guest in filtered}
    selected_ids = get_selected_guest_ids()
    set_bulk_selection(selected_ids - visible_ids)
    _sync_single_selection()


def _render_bulk_controls(filtered: list[dict[str, Any]], movement: str) -> None:
    selected_ids = get_selected_guest_ids()
    visible_ids = {guest["id"] for guest in filtered}
    selected_visible = len(selected_ids & visible_ids)

    st.caption(
        f"{selected_visible} selected in {movement.lower()} · "
        f"{len(selected_ids)} selected total"
    )

    select_col, clear_col = st.columns(2, gap="small")

    with select_col:
        if st.button(
            "Select All",
            key=f"bulk_select_all_{movement}",
            use_container_width=True,
            disabled=not filtered or visible_ids.issubset(selected_ids),
        ):
            _select_all_visible(filtered)
            st.rerun()

    with clear_col:
        if st.button(
            "Clear",
            key=f"bulk_clear_{movement}",
            use_container_width=True,
            disabled=selected_visible == 0,
        ):
            _clear_visible(filtered)
            st.rerun()


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

    _render_bulk_controls(filtered, movement)

    selected_ids = get_selected_guest_ids()
    selection_version = get_bulk_selection_version()

    for guest in filtered:
        guest_id = guest["id"]
        selected_for_bulk = guest_id in selected_ids
        selected_for_single = (
            guest_id == st.session_state.get("selected_guest_id")
            and len(selected_ids) <= 1
        )

        css_class = (
            "guest-card guest-card-selected"
            if selected_for_bulk or selected_for_single
            else "guest-card"
        )

        full_name = guest.get("full_name", "Unknown guest")
        room = guest.get("room") or "—"
        confirmation = guest.get("confirmation_number") or "—"
        eta = guest.get("transport", {}).get("eta") or "—"

        with st.container(border=True):
            checkbox_col, card_col = st.columns([0.10, 0.90], gap="small")

            with checkbox_col:
                checked = st.checkbox(
                    "Select reservation",
                    value=selected_for_bulk,
                    key=(
                        f"bulk_checkbox_{selection_version}_"
                        f"{movement}_{guest_id}"
                    ),
                    label_visibility="collapsed",
                )

                if checked != selected_for_bulk:
                    toggle_bulk_guest(guest_id, checked)
                    _sync_single_selection()
                    st.rerun()

            with card_col:
                st.markdown(
                    '<span class="guest-card-marker"></span>',
                    unsafe_allow_html=True,
                )
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
                "Selected" if selected_for_single else "Open Reservation",
                key=f"select_{movement}_{guest_id}",
                type="primary" if selected_for_single else "secondary",
                disabled=selected_for_single,
                use_container_width=True,
            ):
                clear_bulk_selection()
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
        '<div class="muted">Open one reservation or select several for bulk communication.</div>',
        unsafe_allow_html=True,
    )

    search = _render_guest_search()
    selected_count = len(get_selected_guest_ids())

    if selected_count:
        summary_col, clear_col = st.columns([0.72, 0.28], gap="small")
        with summary_col:
            st.info(f"{selected_count} reservation(s) selected")
        with clear_col:
            if st.button(
                "Clear All",
                key="clear_all_bulk_selection",
                use_container_width=True,
            ):
                clear_bulk_selection()
                st.session_state.selected_guest_id = None
                st.rerun()

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
        with st.container(height=680, border=False):
            _render_movement(guests, "Arrivals", search)

    with departures_tab:
        with st.container(height=680, border=False):
            _render_movement(guests, "Departures", search)
