from __future__ import annotations

import streamlit as st

from components.guest_list import render_guest_list
from components.stay_filter import render_stay_filter
from components.workspace import render_workspace
from services.guest_service import filter_guests_by_stay_dates
from utils.state import ensure_selected_guest


def render(guests: list[dict]) -> None:
    render_stay_filter()
    filtered_guests = filter_guests_by_stay_dates(
        guests=guests,
        arrival_from=st.session_state.applied_arrival_from,
        arrival_to=st.session_state.applied_arrival_to,
        departure_from=st.session_state.applied_departure_from,
        departure_to=st.session_state.applied_departure_to,
    )
    ensure_selected_guest(filtered_guests)

    left, right = st.columns([0.23, 0.77], gap="large")
    with left:
        render_guest_list(filtered_guests)
    with right:
        if not filtered_guests:
            st.info("No arrivals or departures were found for the selected date ranges.")
        elif (
            st.session_state.selected_guest_id is None
            and len(st.session_state.get("selected_guest_ids", set())) == 0
        ):
            st.markdown(
                """
                <div class="empty-workspace-card">
                    <div class="empty-workspace-icon">▤</div>
                    <div class="empty-workspace-title">Please select a reservation</div>
                    <div class="empty-workspace-text">
                        Choose a reservation to view its details and document workflow.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            render_workspace(filtered_guests)
